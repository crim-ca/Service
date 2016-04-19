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
