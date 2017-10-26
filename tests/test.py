#!/usr/bin/env python
# coding:utf-8

"""
Test functionality of Service elements.
"""

# -- standard library ---------------------------------------------------------
import unittest
import os

# --Modules to test -----------------------------------------------------------
from VestaService import Document
from VestaService import Message
from VestaService import RemoteAccess

from VestaService.service_exceptions import DownloadError

CURRENT_DIR = os.path.dirname(__file__)
TEST_DOC_DURATION = 19.9375
PROCESS_DURATION = 2.0  # Processing time in seconds.


# -- fixtures ----------------------------------------------------------------
class TestUtilities(unittest.TestCase):
    """
    Test utility modules.
    """
    def test_document_creation(self):
        """
        Check structure of Document instance.
        """
        some_url = 'http://www.crim.ca'
        some_path = __file__
        doc = Document.Document(url=some_url, path=some_path)
        self.assertEqual(doc.url, some_url)
        self.assertEqual(doc.local_path, some_path)

    def test_blank_message_creation(self):
        """
        Validate message contents after creating blank message.
        """
        msg = Message.request_message_factory()
        self.assertTrue('request_time' in msg)
        self.assertTrue('service' in msg)
        self.assertTrue('annotation_service' in msg)

    def test_download(self):
        """
        Check download function
        """
        MAX_TRY = 1

        #Testing the error returned when the respons code != 200
        doc_msg= {"url" : "http://www.crim.ca/page_inconnue"}
        with self.assertRaises(DownloadError):
            doc = RemoteAccess.download(doc_msg, max_try=MAX_TRY)

        #Testing the size of the data written on the disk
        doc_msg = {"url": "https://httpbin.org/stream-bytes/1024"}
        doc = RemoteAccess.download(doc_msg, max_try=MAX_TRY)
        self.assertEqual(os.stat(doc.local_path).st_size, 1024)
        RemoteAccess.cleanup(doc)

        doc_msg = {"url": "https://httpbin.org/bytes/1024"}
        doc = RemoteAccess.download(doc_msg, max_try=MAX_TRY)
        self.assertEqual(os.stat(doc.local_path).st_size, 1024)
        RemoteAccess.cleanup(doc)

if __name__ == '__main__':
    unittest.main()