# -*- coding: utf-8 -*-
"""\
Contains models used throughout the anomaly codebase. These models are passed
between the queues as message data. They are rebuilt on the other end.
"""
import time
import datetime

from .persistent import create_database_session, Job as PersistentJob, Status


class Job(object):
    """Used to store data about the submitted job and obtain and post related
    data about this job.

    """

    def __init__(self, id, data, timestamp=None):
        self.id = id
        self.data = data
        self.timestamp = timestamp

    def __repr__(self):
        return "<{0} id:{1}, timestamp:{2}>".format(self.__class__.__name__,
                                                    self.id, self.timestamp)

    def stamp(self, timestamp=None):
        """Stamp the job with the given timestamp (POSIX time)
        or with the current time.

        """
        if timestamp is not None:
            self.timestamp = timestamp
        else:
            dt = datetime.datetime.utcnow()
            timestamp_seconds = dt.microsecond * 0.000001
            # Python doesn't add seconds to the stamp.
            self.timestamp = time.mktime(dt.timetuple()) + timestamp_seconds

    def update_status(self, status):
        """Inserts (or updates) the status object into
        the persistent storage.

        """
        Session = create_database_session()
        session = Session()
        status.assign_to_job(self.id)
        session.add(status)
        session.commit()
        session.close()

    def get_latest_status(self):
        """Returns the latest status object"""
        Session = create_database_session()
        session = Session()
        status = session.query(Status).\
            filter(PersistentJob.id == self.id).\
            order_by(Status.timestamp.desc()).\
            first()
        session.close()
        return status

    @property
    def is_complete(self):
        Session = create_database_session()
        session = Session()
        completed_statuses = session.query(Status).\
            filter(PersistentJob.id == self.id).\
            filter(Status.name == 'Complete').\
            all()
        state = False
        if len(completed_statuses) > 0:
            state = True
        session.close()
        return state
