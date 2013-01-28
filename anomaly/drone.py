# -*- coding: utf-8 -*-
"""\
A commandline exoskeleton interface for drone workers to process
anomalous jobs.

"""
import argparse
import logging
import time
from logging.config import fileConfig
from ConfigParser import ConfigParser

import jsonpickle
from pika import BasicProperties
from pika.adapters import BlockingConnection

from .persistent import create_database_session, Status
from .utils import check_timestamp, get_timestamp_offset


EXCHANGE = 'anomaly-analysis'
logger = logging.getLogger('anomaly')


def main(argv=None):
    """Main logic hit by the commandline invocation."""
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('config', help="path to the configuration file")
    parser.add_argument('-n', '--name',
                        help="drone name (used in configuration)")
    args = parser.parse_args(argv)
    if args.config is not None:
        fileConfig(args.config)
        logger.info("Logging initialized")

    config = ConfigParser()
    config.read(args.config)

    # Retrieve the drone's settings from a generic section or one
    #   specified in the arguments.
    config_section = 'drone'
    if args.name is not None:
        config_section = 'drone:{0}'.format(args.name)
    drone_settings = dict(config.items(config_section))

    # XXX Used to initialize a sql session, but this should never
    #     happen because drones shouldn't have access to the
    #     persistent storage.
    Session = create_database_session(config.get('anomaly', 'database-uri'))

    # Queue initialization
    connection = BlockingConnection()
    channel = connection.channel()
    # Declare the exchange and an unnamed queue.
    channel.exchange_declare(exchange=EXCHANGE, type='topic')
    declared_queue = channel.queue_declare(exclusive=True)
    queue_name = declared_queue.method.queue
    channel.queue_bind(exchange=EXCHANGE, queue=queue_name,
                       routing_key=drone_settings['binding-key'])

    # Import the consumer from the settings line.
    module_path, consumer_name = drone_settings['consumer-class'].split(':')
    consumer_import = __import__(module_path, globals(), locals(),
                                 [consumer_name])
    consumer_cls = getattr(consumer_import, consumer_name)
    consumer = consumer_cls(drone_settings)

    # Setup up our consumer callback
    channel.basic_consume(consumer, queue=queue_name)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


if __name__ == '__main__':
    main()
