# -*- coding: utf-8 -*-
"""\
Contains models used throughout the anomaly codebase. These models are passed
between the queues as message data. They are rebuilt on the other end.
"""
import time


class Job(object):
    """Used to store data about the submitted job and obtain and post related
    data about this job.

    """

    def __init__(self, id, data, timestamp=None):
        self.id = id
        self.data = data
        self.timestamp = timestamp

    def stamp(self, timestamp=None):
        """Stamp the job with the given timestamp (POSIX time)
        or with the current time.

        """
        if timestamp is not None:
            self.timestamp = timestamp
        else:
            self.timestamp = time.time()
