# coding:utf-8

"""
Submit a request to one of the annotation / service providers through the
distributed request system.
"""

# --Standard lib modules-------------------------------------------------------
import optparse
import logging
import sys
import imp  # Access import internals.
import os

# --3rd party modules----------------------------------------------------------
from celery import Celery

# --Project specific-----------------------------------------------------------
from .service_exceptions import ConfigFileNotFound
from . import Message

ENCODING = 'utf-8'


# ----------------------------------------------------------------------------
class WorkerExceptionWrapper(Exception):
    """
    Wrapper for worker exception
    """
    def __init__(self, task_uuid, task_status,
                 worker_exception,
                 worker_exc_traceback):
        """
        Build worker Exception wrapper instance.

        >>> w = WorkerExceptionWrapper('abcd1234', 'status',\
                                       'This is a test', 'traceback')

        """
        self.task_uuid = task_uuid
        self.task_status = task_status
        self.worker_exception = worker_exception
        self.worker_exc_traceback = worker_exc_traceback
        w_e_msg = str(worker_exception).encode(ENCODING)
        super(WorkerExceptionWrapper, self).__init__(w_e_msg)


def send_task_request(url,
                      name,
                      app,
                      misc={},
                      ann_srv_url=None):
    """
    Send a request for a process on URL.

    :param url: URL of the file to process
    :param name: Name of the process.
    :param app: Handle to the Celery application.
    :param misc: Optional data that can be passed to a celery worker.
    :param ann_srv_url: URL to where the final annotations will be stored.
    :returns: Instance of :py:class:`celery.result.AsyncResult`
    """
    logger = logging.getLogger(__name__)
    # The message to send on the queue.
    msg = Message.request_message_factory()
    msg['service']['document']['url'] = url
    msg['service']['misc'] = misc
    msg['service']['type'] = name
    msg['annotation_service']['url'] = ann_srv_url

    logger.debug("Celery App is : {}".format(app))

    task_name = '{}.{}'.format(app.main, name)
    logger.debug("Using task name {}".format(task_name))
    result = app.send_task(task_name, args=(msg,))
    logger.info(u"Sent message {msg}".format(msg=msg))
    return result


def get_request_info(uuid, app):
    """
    Get information on a processing request.

    :param uuid: UUID of a given request
    :param app: Handle to the Celery application.
    :returns: dict with information on request processing.
    """
    logger = logging.getLogger(__name__)
    # If uuid doesn't exist the status PENDING is returned
    # so it must be checked at a higher level if we don't want to tell user
    # that a task is pending even if it doesn't exist.

    logger.info("Obtaining information for task %s", uuid)
    async_result = app.AsyncResult(id=uuid)
    status = async_result.state
    result = async_result.result

    # Result for PENDING, PROGRESS and SUCCESS can be sent as is

    # For the moment I cannot validate the returned result for
    # RECEIVED and STARTED so force a None value as it's what
    # should be returned anyway
    logger.info("Task has status %s", status)
    if status == 'RECEIVED' or status == 'STARTED':
        result = None

    # FAILURE, RETRY and REVOKED status contain an exception in the result
    # object. The only difference is that RETRY state result has been
    # serialized so it must be reconstructed (use the exception_to_python
    # function as for the FAILURE state)
    # Raise the exception so that it can be handled at a higher level
    elif status == 'FAILURE' or status == 'RETRY' or status == 'REVOKED':
        if status == 'RETRY':
            result = async_result.backend.exception_to_python(result)

        exc_traceback = async_result.traceback
        raise WorkerExceptionWrapper(uuid, status, result, exc_traceback)

    information = {
        'uuid': uuid,
        'status': status,
        'result': result
    }
    return information


def cancel_request(uuid, app):
    """
    Cancel a processing request.

    :param uuid: UUID of a given request
    :param app: Handle to the Celery application.
    """
    logger = logging.getLogger(__name__)
    logger.info("Issuing a revoke command for task %s", uuid)
    app.control.revoke(uuid, terminate=True, signal='SIGKILL')


def main():
    """
    Command line entry point.
    """
    usage = "%prog document_url"
    parser = optparse.OptionParser(usage=usage)
    default_config = 'config'
    parser.add_option('-c', '--config',
                      dest="config_fn",
                      default=default_config,
                      help="Configuration filename "
                           "(defaults to \"{0}\")".format(default_config))

    parser.add_option('-l', '--log',
                      dest="log_level",
                      default='INFO',
                      help='Change log level')

    options, arguments = parser.parse_args()

    if len(arguments) != 1:
        parser.error("Insufficient arguments")

    document_url = arguments[0]
    config_fn = options.config_fn

    if not os.path.exists(config_fn+'.py'):
        # Cheap way to signal an error at script level.
        raise ConfigFileNotFound("No such file : " + config_fn+'.py')

    config_dir = os.path.dirname(config_fn)
    sys.path.append(config_dir)
    fp_, pathname, description = imp.find_module(config_fn)
    celery_proj_name = 'worker'
    app = Celery(celery_proj_name)
    celeryconfig = imp.load_module('celeryconfig', fp_, pathname, description)
    app.config_from_object(celeryconfig)

    log_level_map = {'DEBUG': logging.DEBUG,
                     'INFO': logging.INFO,
                     'WARNING': logging.WARNING,
                     'ERROR': logging.ERROR,
                     'CRITICAL': logging.CRITICAL, }

    conf_log_level = options.log_level
    log_level = log_level_map.get(conf_log_level, logging.NOTSET)

    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    process_name = celeryconfig.PROCESS_NAME

    res = send_task_request(document_url, process_name, app)
    logger = logging.getLogger(__name__)
    logger.info("Waiting for results...")
    results = res.get()
    print("Results: {r}".format(r=results))

if __name__ == '__main__':
    main()
