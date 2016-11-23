#!/usr/bin/env python
# coding:utf-8

"""
This module offers tools for message creation / manipulation.

This essentially defines message contents.
"""

# --Standard lib modules-------------------------------------------------------
from datetime import datetime

# -- Configuration ------------------------------------------------------------
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def mk_timestamp():
    """
    Return current time as a string as defined by RFC 3339 .
    """
    return datetime.now().strftime(DATETIME_FORMAT)


def request_message_factory():
    """
    Return a blank message, useful for submitting annotation requests.
    """
    msg = {
        'request_time': mk_timestamp(),
        'service': {
            'misc': None,
            'type': None,
            'document': {
                'url': None,
                'credentials': None,
            },
        },
        'annotation_service': {
            'url': None,
            'uuid': None,
            'credentials': None,
        },
    }
    return msg
