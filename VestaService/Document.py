#!/usr/bin/env python
# coding:utf-8

"""
This module documents a URL download process
"""

# --Standard lib modules------------------------------------------------------
from datetime import datetime
import logging


# ----------------------------------------------------------------------------
class Document(object):
    """
    Container for all information related to downloading of a distant document
    to a local file.
    """
    url = None
    local_path = None
    transfer_time = None
    length = None

    def __init__(self, url=None, path=None):
        """
        Constructor.

        :param url: URL of the source document which will be handled locally.
        :param path: Local path to the document copy.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Creating an instance with parameters url=%s,"
                          " path=%s", url, path)
        self.url = url
        self.local_path = path
        self.transfer_time = datetime.now()

    def __repr__(self):
        """
        Printable representation
        """
        return self.url
