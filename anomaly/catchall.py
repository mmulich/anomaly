# -*- coding: utf-8 -*-
"""\
Contains the job worker that catches all processed data message and ensures
that each request is worked on even if it hasn't been worked on yet.

"""
import argparse
import logging
import jsonpickle
from logging.config import fileConfig
import jsonpickle
from pika.adapters import BlockingConnection


EXCHANGE = 'anomaly-analysis'
QUEUE = 'anomaly-catchall'
BINDING_KEY = '#'

logger = logging.getLogger('anomaly')


def consumer(channel, method, header, body):
    """Consume a message to do one of two things:
    1) update its status and republish
    2) notify someone of the jobs progress or results

    """
    if header.content_type != 'application/json':
        raise Exception("unrecognized message content-type: "
                        "{0}".format(header.content_type))
    job = jsonpickle.decode(body)
    logger.debug("Received message: {0} - {1}"
                 "\n\t{2!r}"
                 "\n\t{3!r}".format(job.id, job.timestamp, job, job.data))

    # Update status to checked if the job is not currently being
    #   worked on.
    ##status = Checked(job, OK)
    ##job.update_status(status)

    # Stamp the job and republish it back to this queue.
    job.stamp()

    # Update the job in the database.
    ##session = ???
    ##job.save(session)

    channel.basic_ack(method.delivery_tag)


def main(argv=None):
    """Main logic hit by the commandline invocation."""
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('-c', '--config',
                        help="path to the configuration file")
    args = parser.parse_args(argv)
    if args.config is not None:
        fileConfig(args.config)
        logger.info("Logging initialized")

    # Queue initialization
    connection = BlockingConnection()
    channel = connection.channel()
    # Declare the exchange and an unnamed queue.
    channel.exchange_declare(exchange=EXCHANGE, type='topic')
    declared_queue = channel.queue_declare(queue=QUEUE, durable=True,
                                           exclusive=False)
    channel.queue_bind(exchange=EXCHANGE, queue=QUEUE,
                       routing_key=BINDING_KEY)

    # Setup up our consumer callback
    channel.basic_consume(consumer, queue=QUEUE)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == '__main__':
    main()
