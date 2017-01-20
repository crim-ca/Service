#!/usr/bin/env python
# coding:utf-8

"""
Expose a stub method through Celery for testing purposes.
"""

# -- Standard library --------------------------------------------------------
from time import sleep

# --3rd party modules----------------------------------------------------------
from celery.utils.log import get_task_logger
from celery import Celery

APP = Celery(__name__)


@APP.task
def process_stub(args):
    """
    A celery process which does nothing but return supplied arguments, mostly
    useful for testing.

    :param args: Random arguments which will be returned to caller.
    :returns: Result as produced by :py:func:`.detect.score_copies` .
    """
    logger = get_task_logger(__name__.split('.')[0])
    logger.info("Got request to process %s", args)
    duration = .1
    logger.info("Sleeping for %s", duration)
    sleep(duration)
    return {'result': {'type': 'Useless', 'value': args}}
