# -*- coding: utf-8 -*-
"""\
A consumer of raw job data. The output of this consumer is
a more procise and trackable message that is published to the
anomaly exchange.
"""
import json
import logging
import jsonpickle
from pika.adapters import BlockingConnection
from pika import BasicProperties

from .models import Job
from .utils import get_routing_key


QUEUE = 'anomaly-spotted'
EXCHANGE = 'anomaly-analysis'

logger = logging.getLogger()


def consumer(consuming_channel, method, header, body):
    if header.content_type != 'application/json':
        raise Exception("unrecognized message content-type: "
                        "{0}".format(header.content_type))
    data = json.loads(body)
    # Create the SQL Job entry and commit it.
    id = 0  # TODO

    # Create the new Job message object.
    job = Job(id, data)

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
    logger.info("Sent {0!r}:{1!r}".format(routing_key, job))
    connection.close()

    # Acknowledge message receipt
    consuming_channel.basic_ack(method.delivery_tag)


def main(argv=None):
    """Main logic hit by the commandline invocation."""
    logger.setLevel(logging.INFO)
    connection = BlockingConnection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True, exclusive=False)

    # Setup up our consumer callback
    channel.basic_consume(consumer, queue=QUEUE)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == '__main__':
    main()
