# -*- coding: utf-8 -*-
"""\
A consumer of raw job data. The output of this consumer is
a more procise and trackable message that is published to the
anomaly exchange.
"""
import argparse
import logging
import json
import jsonpickle
from ConfigParser import ConfigParser
from logging.config import fileConfig
from pika import BasicProperties
from pika.adapters import BlockingConnection

from .models import Job
from .persistent import create_database_session, Job as PersistentJob
from .utils import get_routing_key


QUEUE = 'anomaly-spotted'
EXCHANGE = 'anomaly-analysis'

logger = logging.getLogger('anomaly')


class Consumer(object):

    def __init__(self, session):
        self.session = session

    def __call__(self, consuming_channel, method, header, body):
        if header.content_type != 'application/json':
            raise Exception("unrecognized message content-type: "
                            "{0}".format(header.content_type))
        data = json.loads(body)

        # Create the SQL Job entry and commit it.
        type = data.get('type', '')
        persistent_job = PersistentJob(body, type)
        self.session.add(persistent_job)
        self.session.commit()
        id = persistent_job.id

        # Create the new Job message object.
        job = Job(id, data)
        job.stamp()
        logger.info("Created job {0}".format(job))

        # Submit the new message to the topic exchange.
        connection = BlockingConnection()
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE, type='topic')

        routing_key = get_routing_key(job)
        message = jsonpickle.encode(job)
        properties = BasicProperties(content_type="application/json")
        channel.basic_publish(exchange=EXCHANGE,
                              routing_key=routing_key,
                              properties=properties,
                              body=message)
        logger.debug("Sent message to '{0}' with {1!r}".format(routing_key,
                                                               message))
        connection.close()

        # Acknowledge message receipt
        consuming_channel.basic_ack(method.delivery_tag)


def main(argv=None):
    """Main logic hit by the commandline invocation."""
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('config', help="path to the configuration file")
    args = parser.parse_args(argv)
    if args.config is not None:
        fileConfig(args.config)
        logger.info("Logging initialized")

    config = ConfigParser()
    config.read(args.config)
    # Grab the database uri setting from the config.
    session = create_database_session(config.get('anomaly', 'database-uri'))

    # Queue initialization
    connection = BlockingConnection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True, exclusive=False)

    # Setup up our consumer callback
    consumer = Consumer(session)
    channel.basic_consume(consumer, queue=QUEUE)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == '__main__':
    main()
