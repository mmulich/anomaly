# -*- coding: utf-8 -*-
"""\
Various utilities and helper functions used by this package.
"""

ROUTING_KEY_FORMAT = "{project}.{format}.{build_engine}"

def get_routing_key(job):
    """Given an anomaly.models.Job, return a routing key for the topic
    exchange.

    """
    return ROUTING_KEY_FORMAT.format(**job.data)
