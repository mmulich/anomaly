# -*- coding: utf-8 -*-
"""\
Contains models used throughout the anomaly codebase. These models are used
to persist data in a SQL database.
"""
import argparse
import logging
from ConfigParser import ConfigParser
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy.orm import backref, relationship, sessionmaker
from sqlalchemy import (
    Column,
    ForeignKey,
    Float,
    Integer,
    String,
    Text,
    )
from sqlalchemy.ext.declarative import declarative_base


logger = logging.getLogger('anomaly')

engine = None
Session = sessionmaker()
Base = declarative_base()



def create_database_session(db_uri=None):
    """Creates a session for use with the database."""
    global engine
    if engine is None:
        if db_uri is None:
            # FIXME This is bad, but without a main application object
            #       and/or registry, there isn't a clean way around it
            #       at this time.
            raise RuntimeError("A database URI is required to "
                               "initialize the database.")
        engine = create_engine(db_uri)
    Session.configure(bind=engine)
    return Session()


class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    data = Column(String)
    type = Column(String)

    def __init__(self, data, type=''):
        self.data = data
        self.type = type


class Status(Base):
    __tablename__ = 'statuses'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    name = Column(String)
    timestamp = Column(Float)
    message = Column(Text)
    job = relationship('Job', backref=backref('statuses', order_by=timestamp))

    def __init__(self, name, timestamp, message=''):
        self.name = name
        self.timestamp = timestamp
        self.message = message

    def assign_to_job(self, id):
        self.job_id = id


# ######################### #
#   Commandline Interface   #
# ######################### #

commands = {}

def initialize_database(session):
    """Initializes the database"""
    global engine
    Base.metadata.create_all(engine)

commands['initialize'] = initialize_database


def main(argv=None):
    """Main logic hit by the commandline invocation for initializing,
    maintaining and poking the database.

    """
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('config', help="path to the configuration file")
    parser.add_argument('command', choices=commands.keys(),
                        help="command to invoke")
    args = parser.parse_args(argv)
    if args.config is not None:
        fileConfig(args.config)
        logger.info("Logging initialized")

    config = ConfigParser()
    config.read(args.config)
    # Grab the database uri setting from the config.
    session = create_database_session(config.get('anomaly', 'database-uri'))

    commands[args.command](session)

if __name__ == '__main__':
    main()
