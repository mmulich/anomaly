# -*- coding: utf-8 -*-
"""\
A consumer of raw job data. The output of this consumer is
a more procise and trackable message that is published to the
anomaly exchange.
"""
from pika.adapters import BlockingConnection


QUEUE = 'anomaly-spotted'


def consumer(channel, method, header, body):
    print("Message:"
          "\n\t{0!r}"
          "\n\t{1!r}"
          "\n\t{2!r}".format(method, header, body))

    # Acknowledge message receipt
    channel.basic_ack(method.delivery_tag)


def main(argv=None):
    """Main logic hit by the commandline invocation."""
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
