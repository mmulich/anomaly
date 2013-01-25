
The Story
---------

An incoming message comes in from a producer. The message is raw JSON
day that contains the name, version, build type (usually
null), format (e.g. pdf), project (e.g. ccap) and point of origin.

Th raw information is pulled off the incomping queue by an initial
preprocessing worker. This worker assigns an id to the message
and creates a jsonpickle object form the data. This transformed
message with an id is then submitted to the topic exchange.

The catch-all queue has a worker that checks the status of jobs, including
whether a worker is available to do the work. The worker does the work
and then updates the status by sending a message to the status queue.

In the event that the catch-all worker comes across a job that has no
worker available, it will add a checked status to the job. In the
event that a maxium number of checks has been done on the job  without
any work being done, the catch-all worker will attempt to spawn a new
worker to fulfil the need. If this can't be done, it will report a
status error and notify whomever has been setup to receive problem
notifications.

How does the producer track the status of a message submitted to the
queue? We could allow the producer to provide an obscure callback url
that posts the message id. 

Once the status of the job has been set to complete the catch-all
queue worker will remove the item from the queue. In the event an
error has occured it will send an email to whomever has been setup to
recieve problem notifications.

SQL DB
------

Contains info about the message and an id to attach to the
message/job. Then status assignments can be handled against this
message persistent info. 

Queues
------

- Incoming - preprocessed messages, create the SQL DB entry with an id
  and then put the id into the message.
- Catch-all - All processed message go to this queue to make sure the
  message gets worked on even if a worker process isn't running just
  yet.
- Various worker queues - These queues are topic based queues that
  grab work they know they can take care of. This also makes it so
  that the workers can be spun up and tore down dynamically without
  killing the machine with an uncountable number of dependencies. This
  way each worker machine can be setup for it's specific task,
  including any proprietary software usage that is cpu based.
- Status update - Status messages are sent to this queue. These will
  be handled almost immediately. The idea here is to make it so that
  the worker doesn't have to make a sql connection to update the jobs
  status.
