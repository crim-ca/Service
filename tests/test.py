#!/usr/bin/env python
# coding:utf-8

"""
Test functionality of Service elements.
"""

# -- standard library ---------------------------------------------------------
from cgi import parse_header, FieldStorage
from threading import Thread
import unittest
import tempfile
import zipfile
import socket
import json
import sys
import os

# -- Third-party imports ------------------------------------------------------
import requests

# --Modules to test -----------------------------------------------------------
from VestaService import (Document, Message, RemoteAccess,
                          annotations_dispatcher)

from VestaService.service_exceptions import DownloadError

if sys.version_info >= (3, 1):
    from http.server import BaseHTTPRequestHandler, HTTPServer
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

CURRENT_DIR = os.path.dirname(__file__)
TEST_DOC_DURATION = 19.9375
PROCESS_DURATION = 2.0  # Processing time in seconds.


class MockServerRequestHandler(BaseHTTPRequestHandler):
    """
    Mock server to test the submit_annotation function

    """
    def do_POST(self):
        '''
        Process an HTTP POST request and return a response with the length of
        the data received.  If the data is zipped, unzip it on the disk and
        check the length of the unzipped data.
        '''

        ctype, pdict = parse_header(self.headers['content-type'])

        # Handling unzipped data
        if ctype == "application/json":
            content_len = int(self.headers.get("Content-Length"))
            post_body = self.rfile.read(content_len)
            body = json.loads(post_body.decode('utf-8'))
            if body["data"] is not None:
                self.send_response(requests.codes.ok)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write('{{"Content-Length" : {} }}'.
                                 format(content_len).encode('utf-8'))
            else:
                self.send_response(requests.codes.bad)
                self.end_headers()

        # Handling zipped data
        elif ctype == "multipart/form-data":
            form = FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type'],
                         })
            filename = form['file'].filename
            if filename != "annotations.zip":
                self.send_response(requests.codes.bad)
            else:
                data = form['file'].file.read()
                temp_file_path = os.path.join(tempfile.gettempdir(),
                                              "test.zip")

                with open(temp_file_path, "wb") as zip_file:
                    zip_file.write(data)
                with zipfile.ZipFile(temp_file_path, "r") as zippy:
                    infolist = zippy.infolist()
                    if len(infolist) != 1:
                        self.send_response(requests.codes.bad)
                    else:
                        self.send_response(requests.codes.ok)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write('{{"Content-Length" : {} }}'.
                                         format(infolist[0].file_size).
                                         encode('utf-8'))
                os.remove(temp_file_path)


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


# -- fixtures ----------------------------------------------------------------
class TestUtilities(unittest.TestCase):
    """
    Test utility modules.
    """

    def setUp(self):
        self.mock_server_port = get_free_port()
        self.mock_server = HTTPServer(('localhost', self.mock_server_port),
                                      MockServerRequestHandler)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        self.mock_server_thread = Thread(target=self.mock_server.serve_forever)
        self.mock_server_thread.setDaemon(True)
        self.mock_server_thread.start()

    def tearDown(self):
        self.mock_server.server_close()

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

        # Testing the error returned when the respons code != 200
        doc_msg = {"url": "http://www.crim.ca/page_inconnue"}
        with self.assertRaises(DownloadError):
            doc = RemoteAccess.download(doc_msg, max_try=MAX_TRY)

        # Testing the size of the data written on the disk
        doc_msg = {"url": "https://httpbin.org/stream-bytes/1024"}
        doc = RemoteAccess.download(doc_msg, max_try=MAX_TRY)
        self.assertEqual(os.stat(doc.local_path).st_size, 1024)
        RemoteAccess.cleanup(doc)

        doc_msg = {"url": "https://httpbin.org/bytes/1024"}
        doc = RemoteAccess.download(doc_msg, max_try=MAX_TRY)
        self.assertEqual(os.stat(doc.local_path).st_size, 1024)
        RemoteAccess.cleanup(doc)

    def test_submit_annotations(self):
        """
        Check the annotations_dispatcher.submit_annotation function
        :return:
        """

        post_url = "http://localhost:{}".format(self.mock_server_port)
        annotations = [{"annotation": "annotation"}]

        # Sending the annotations zipped
        result = annotations_dispatcher.submit_annotations(post_url,
                                                           annotations, True)
        self.assertEqual(result.status_code, 200)
        zip_resp = json.loads(result.content.decode('utf-8'))

        # Sending the annotations unzipped
        result = annotations_dispatcher.submit_annotations(post_url,
                                                           annotations, False)
        self.assertEqual(result.status_code, 200)
        no_zip_resp = json.loads(result.content.decode('utf-8'))

        # Checking that the length of the data sent by both method is the same
        self.assertEqual(zip_resp["Content-Length"],
                         no_zip_resp["Content-Length"])


if __name__ == '__main__':
    unittest.main()
