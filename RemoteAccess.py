#!/usr/bin/env python
# coding:utf-8

"""
This module offers the downloading and uploading capacity for annotation
services working on a AMQP.
"""

# --Standard lib modules------------------------------------------------------
from tempfile import NamedTemporaryFile
from logging import getLogger
import os

# --3rd party modules----------------------------------------------------------
import requests

# --Project specific----------------------------------------------------------
from .service_exceptions import (DownloadError, UploadError)
from .Document import Document

CHUNK_SIZE = 16 * 1024
TIMEOUT = 10


def download(doc_msg):
    """
    Download a given document to a local file.
    The calling function is responsible for the resulting file.

    :param doc_msg: dict containing the following keys::
                    url: path to a distant document
                    credentials: credentials to access document
    :returns: object of type Document.
    """
    logger = getLogger(__name__)
    url = doc_msg['url']
    logger.info(u"Getting remote document at «{url}»".format(url=url))
    extension = os.path.splitext(url)[-1]
    cur_try = 1
    max_try = 5
    response = None

    # TODO : Handle cases were urlopen doesn't throw error but the result isn't
    #        200
    while cur_try <= max_try and response is None:
        try:
            response = requests.get(url, timeout=TIMEOUT, stream=True)
        except requests.Timeout as error:
            # Handle timeout error separately
            if cur_try < max_try:
                cur_try += 1
                logger.warning(u"Timeout occurred while downloading document "
                               u"«{url}». Retry ({cur_try}/{max_try})".
                               format(url=url,
                                      cur_try=cur_try,
                                      max_try=max_try))
            else:
                logger.error(u"Could not download document «{url}»".
                             format(url=url))
                raise DownloadError(error)
        except requests.exceptions.RequestException as error:
            logger.error(u"Could not download document «{url}»".
                         format(url=url))
            raise DownloadError(error)

    with NamedTemporaryFile(mode='w+',
                            suffix=extension,
                            delete=False) as destination:
        for chunk in response.iter_content(CHUNK_SIZE):
            destination.write(chunk)
    doc = Document(url=url, path=destination.name)
    logger.info(u"Download of URL «{url}» complete".format(url=doc.url))
    logger.debug(u"Local copy name is : «{fn}»".format(fn=doc.local_path))
    return doc


def upload(doc):
    """
    Upload a given document from a local file.
    This function is built to upload exclusively to the Vesta storage service.

    :param doc: a Document with valid values.
    :returns: Object of type Document with the URL updated by the one that
              should be used to download the uploaded file.
    """
    logger = getLogger(__name__)
    logger.info(u"Uploading document to remote URL «{url}»".
                format(url=doc.url))
    logger.debug(u"Uploading «{doc}» to remote URL «{url}»".
                 format(doc=doc.local_path, url=doc.url))

    file_handle = open(doc.local_path, 'rb')
    headers = {'Content-Type': 'application/octet-stream'}

    cur_try = 1
    max_try = 5
    result = None
    upload_url = None
    storage_doc_id = None
    while cur_try <= max_try and result is None:
        try:
            if upload_url is None or storage_doc_id is None:
                result_inter = requests.get('{url}?filename={fn}'.format(
                    url=doc.url,
                    fn=os.path.basename(doc.local_path)), timeout=TIMEOUT)

                if result_inter.status_code != requests.codes.ok:
                    result_inter.raise_for_status()

                json_struct = result_inter.json()
                upload_url = json_struct['upload_url']
                storage_doc_id = json_struct['storage_doc_id']

                logger.info(u"Retrieved an upload temporary url for document "
                            u"«{id}» : «{url}»"
                            .format(url=upload_url, id=storage_doc_id))

            result = requests.put(upload_url,
                                  headers=headers,
                                  data=file_handle,
                                  verify=False,
                                  timeout=TIMEOUT)

        except requests.exceptions.Timeout as error:
            # Handle timeout error separately
            if cur_try < max_try:
                cur_try += 1
                logger.warning(u"Timeout occurred while uploading document to "
                               u"«{url}». Retry ({cur_try}/{max_try})".
                               format(url=doc.url,
                                      cur_try=cur_try,
                                      max_try=max_try))
            else:
                logger.error(u"Could not upload document to «{url}»".
                             format(url=doc.url))
                raise UploadError(error)

        except requests.exceptions.RequestException as error:
            logger.error(u"Could not upload document to «{url}»".
                         format(url=doc.url))
            raise UploadError(error)

    if result.status_code != requests.codes.ok:
        result.raise_for_status()

    logger.info(u"Upload to «{url}» complete, "
                u"document can be retrieved with id «{id}»".
                format(url=upload_url, id=storage_doc_id))

    doc.url = storage_doc_id

    return doc


def cleanup(doc):
    """
    Remove a given local document.

    :param doc: Document on which the cleanup will act.
    """
    logger = getLogger(__name__)
    if doc.local_path:
        logger.debug(u"Removing local copy «{fn}»".format(fn=doc))
        os.remove(doc.local_path)
