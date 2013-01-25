# -*- coding: utf-8 -*-
"""\

"""
import logging
import jsonpickle
from pika.adapters import BlockingConnection


EXCHANGE = 'anomaly-analysis'
BINDING_KEY = '#'
logger = logging.getLogger()


def consumer(channel, method, header, body):
    if header.content_type != 'application/json':
        raise Exception("unrecognized message content-type: "
                        "{0}".format(header.content_type))
    job = jsonpickle.decode(body)
    print("Message: {0}"
          "\n\t{1!r}"
          "\n\t{2!r}".format(job.id, job, job.data))

    channel.basic_ack(method.delivery_tag)


def main(argv=None):
    """Main logic hit by the commandline invocation."""
    logger.setLevel(logging.INFO)
    connection = BlockingConnection()
    channel = connection.channel()
    # Declare the exchange and an unnamed queue.
    channel.exchange_declare(exchange=EXCHANGE, type='topic')
    declared_queue = channel.queue_declare(exclusive=True)
    queue_name = declared_queue.method.queue
    channel.queue_bind(exchange=EXCHANGE, queue=queue_name,
                       routing_key=BINDING_KEY)

    # Setup up our consumer callback
    channel.basic_consume(consumer, queue=queue_name)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == '__main__':
    main()
