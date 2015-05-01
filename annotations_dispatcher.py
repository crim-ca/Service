#!/usr/bin/env python
# coding:utf-8

"""
The purpose of this module is to encapsulate all the necessary code to submit
an annotation storage request. It is adapted to the Annotations Storage Service
developped for the CANARIE / Vesta project by CRIM.
"""

# Standard library requirements ----------------------------------------------
import optparse
import logging
import json

# 3rd party requirements -----------------------------------------------------
import requests

# -- project - specific ------------------------------------------------------
from .service_exceptions import (UploadError, InvalidAnnotationFormat)

TIMEOUT = 10


def submit_annotations(ann_srv_url, annotations):
    """
    Call the Annotation Storage Service to save annotations.

    :param ann_srv_url: URL of the annotation service where the annotations
                        will be stored.
    :param annotations: Annotations to append to the annotations Document.
    :type annotations: list
    """
    logger = logging.getLogger(__name__)
    logger.info(u"Submitting annotations to target {url}".
                format(url=ann_srv_url))

    if type(annotations) != list:
        raise InvalidAnnotationFormat("Annotations should be an object of type"
                                      " «list»")

    cur_try = 1
    max_tries = 5
    result = None

    payload = json.dumps({'common': {},
                          'data': annotations})

    headers = {'content-type': 'application/json',
               'accept': 'application/json'}

    logger.debug(u"Upload URL is «{0}»".format(ann_srv_url))
    logger.debug(u"Submitted data is {0}".format(payload))

    while cur_try <= max_tries and not result:
        logger.debug(u"Trying HTTP POST request {0}/{1}".
                     format(cur_try, max_tries))

        try:
            result = requests.post(ann_srv_url,
                                   data=payload,
                                   timeout=TIMEOUT,
                                   headers=headers)

            if result.status_code not in [200, 201, 204]:
                logger.error(u"Got following code : {0}".
                             format(result.status_code))
                result.raise_for_status()

        except requests.exceptions.Timeout as error:
            # Handle timeout error separately
            if cur_try < max_tries:
                cur_try += 1
                logger.debug(u"Current try : {0}".format(cur_try))
                logger.warning(u"Timeout occurred while uploading document to "
                               u"«{url}». Retry ({cur_try}/{max_tries})".
                               format(url=ann_srv_url,
                                      cur_try=cur_try,
                                      max_tries=max_tries))
            else:
                logger.error(u"Could not upload document to «{url}»".
                             format(url=ann_srv_url))
                raise UploadError(error)

        except requests.exceptions.RequestException as error:
            logger.error(u"Could not upload document to «{url}»".
                         format(url=ann_srv_url))
            raise UploadError(error)


def main():
    """
    Command line entry point.
    """
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

    usage = '%prog storage_service_url'
    parser = optparse.OptionParser(usage=usage)

    args = parser.parse_args()[-1]

    if len(args) != 1:
        parser.error("Insufficient arguments")

    url = args[0]
    submit_annotations(url, [{'a': 2}, {'a': 1}])

if __name__ == '__main__':
    main()
