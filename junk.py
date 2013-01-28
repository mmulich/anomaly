# -*- coding: utf-8 -*-
import jsonpickle
from anomaly.persistent import Status


class Consumer(object):

    def __init__(self, settings):
        self.settings = settings

    def __call__(self, channel, method, header, body):
        if header.content_type != 'application/json':
            raise Exception("unrecognized message content-type: "
                            "{0}".format(header.content_type))
        job = jsonpickle.decode(body)
        print("Received message: {0} - {1}"
              "\n\t{2!r}"
              "\n\t{3!r}".format(job.id, job.timestamp, job, job.data))

        # Update status to checked if the job is not currently being
        #   worked on.
        job.stamp()
        status = Status('Working', job.timestamp)
        job.update_status(status)
        print("Status updated to 'Working' on {0}.".format(job))

        # Do the work here...

        job.stamp()
        status = Status('Complete', job.timestamp)
        job.update_status(status)
        print("Status updated to 'Complete' on {0}".format(job))

        channel.basic_ack(method.delivery_tag)
