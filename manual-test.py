# -*- coding: utf-8 -*-
"""\
A commandline script for randomly populating the anomaly system.
This is a demonstration of the beginning of the story developed
in the README of the anomaly package.
"""
import json
from pika.adapters import BlockingConnection
from pika import BasicProperties


QUEUE = 'anomaly-spotted'
LATEX = 'latex'
PRINCEXML = 'princexml'
XXX_DATA_STRUCT = ('name', 'version', 'build', 'format', 'project', 'origin',)
XXX_DATA = (
    ('flan', '1.1', None, 'pdf', 'cnx', 'http://cnx.org',),
    ('bio', 'latest', PRINCEXML, 'mobi', 'ccap', 'http://bio.cnx.org',),
    ('hact', '2.5', None, 'completezip', None, 'http://cnx.org',),
    ('trok', '0.1', LATEX, 'epub', 'openstax', 'http://cnx.org',),
    )


def main(argv=None):
    """Main logic hit by the commandline invocation."""
    connection = BlockingConnection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True, exclusive=False)

    # Convert the data over to JSON message bits relative to what the
    #   producer would send.
    data = [json.dumps(dict(zip(XXX_DATA_STRUCT, d))) for d in XXX_DATA]
    for message in data:
        # Send the message to the preprocessor/incoming queue.
        properties = BasicProperties(content_type="application/json",
                                     delivery_mode=1)
        channel.basic_publish(exchange='', routing_key=QUEUE, body=message,
                              properties=properties)


if __name__ == "__main__":
    main()
