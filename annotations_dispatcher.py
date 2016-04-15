# coding:utf-8

"""
The purpose of this module is to encapsulate all the necessary code to submit
an annotation storage request. It is adapted to the Annotations Storage Service
(JASS) developed for the CANARIE / Vesta project by CRIM.
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
    logger.info("Submitting annotations to target %s", ann_srv_url)

    if not isinstance(annotations, list):
        raise InvalidAnnotationFormat("Annotations should be an object of type"
                                      " list")

    cur_try = 1
    max_tries = 5
    result = None

    payload = json.dumps({'common': {},
                          'data': annotations})

    headers = {'content-type': 'application/json',
               'accept': 'application/json'}

    logger.debug("Upload URL is %s", ann_srv_url)
    logger.debug("Submitted data is %s", payload)

    while cur_try <= max_tries and not result:
        logger.debug("Trying HTTP POST request %s/%s", cur_try, max_tries)

        try:
            result = requests.post(ann_srv_url,
                                   data=payload,
                                   timeout=TIMEOUT,
                                   headers=headers)

            if result.status_code not in [200, 201, 204]:
                logger.error("Got following code : %s", result.status_code)
                result.raise_for_status()

        except requests.exceptions.Timeout as error:
            # Handle timeout error separately
            if cur_try < max_tries:
                cur_try += 1
                logger.debug("Current try : %s", cur_try)
                logger.warning("Timeout occurred while uploading document to "
                               "%s. Retry (%s/%s)",
                               ann_srv_url, cur_try, max_tries)
            else:
                logger.error("Could not upload document to %s", ann_srv_url)
                raise UploadError(error)

        except requests.exceptions.RequestException as error:
            logger.error("Could not upload document to %s", ann_srv_url)
            raise UploadError(error)


def main():
    """
    Command line entry point to test upload of annotations.
    """
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)

    usage = '%prog storage_service_url annotation'
    parser = optparse.OptionParser(usage=usage)

    args = parser.parse_args()[-1]

    if len(args) != 2:
        parser.error("Insufficient arguments")

    url = args[0]
    annotation = args[1]
    submit_annotations(url, annotation)

if __name__ == '__main__':
    main()
