# -*- coding: utf-8 -*-
"""\
Various utilities and helper functions used by this package.
"""
import datetime


ROUTING_KEY_FORMAT = "{project}.{format}.{build_engine}"

def get_routing_key(job):
    """Given an anomaly.models.Job, return a routing key for the topic
    exchange.

    """
    return ROUTING_KEY_FORMAT.format(**job.data)

def check_timestamp(timestamp, interval):
    """Verify the we are in the future at least as much as
    the interval amount (in seconds).

    """
    delta = datetime.timedelta(seconds=interval)
    now = datetime.datetime.utcnow()
    then = datetime.datetime.fromtimestamp(timestamp)
    lapsed_time = now - then
    state = False
    if lapsed_time > delta:
        state = True
    return state

def get_timestamp_offset(timestamp, interval):
    """Return the remaining time until the interval is reached."""
    delta = datetime.timedelta(seconds=interval)
    now = datetime.datetime.utcnow()
    then = datetime.datetime.fromtimestamp(timestamp)
    lapsed_time = now - then
    offset = delta - lapsed_time
    return offset.total_seconds()
