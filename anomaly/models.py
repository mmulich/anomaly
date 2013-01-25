# -*- coding: utf-8 -*-
"""\
Contains models used throughout the anomaly codebase. These models are passed
between the queues as message data. They are rebuilt on the other end.
"""



class Job(object):
    """Used to store data about the submitted job and obtain and post related
    data about this job.

    """

    def __init__(self, id, data):
        self.id = id
        self.data = data
