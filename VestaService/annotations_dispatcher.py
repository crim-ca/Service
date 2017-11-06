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
import zipfile
import tempfile
import os

# 3rd party requirements -----------------------------------------------------
import requests

# -- project - specific ------------------------------------------------------
from .service_exceptions import (UploadError, InvalidAnnotationFormat)

TIMEOUT = 10


def submit_annotations(ann_srv_url, annotations, send_zip=False):
    """
    Call the Annotation Storage Service to save annotations.

    :param ann_srv_url: URL of the annotation service where the annotations
                        will be stored.
    :param annotations: Annotations to append to the annotations Document.
    :param send_zip: indicates if the annotations should be sent in a zip file
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

    logger.debug("Upload URL is %s", ann_srv_url)
    logger.debug("Submitted data is %s", payload)

    files = None
    temp_text_file = None
    temp_zip_file = None

    if send_zip:
        headers = {'accept': 'application/json'}
        # creating annotations.txt file to be zipped
        temp_dir = tempfile.gettempdir()
        text_file_name = "annotations.txt"
        zip_file_name = "annotations.zip"
        temp_text_file = os.path.join(temp_dir, text_file_name)
        temp_zip_file = os.path.join(temp_dir, zip_file_name)
        with open(temp_text_file, 'w') as file_to_zip:
            file_to_zip.write(str(payload))

        # creating zipped file
        with zipfile.ZipFile(temp_zip_file, "w",
                             compression=zipfile.ZIP_DEFLATED) as zippy:
            zippy.write(temp_text_file, text_file_name)
            zippy.close()

        # Opened for transport (HTTP POST via form-data, as bytes)
            opened_zipped_file = open(temp_zip_file, "rb")
            files = {"file": opened_zipped_file}
    else:
        headers = {'content-type': 'application/json',
                   'accept': 'application/json'}

    while cur_try <= max_tries and not result:
        logger.debug("Trying HTTP POST request %s/%s", cur_try, max_tries)

        try:
            if files is None:
                result = requests.post(ann_srv_url,
                                       data=payload,
                                       timeout=TIMEOUT,
                                       headers=headers)
            else:
                result = requests.post(ann_srv_url,
                                       files=files,
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

        finally:
            # Delete artifacts
            if temp_text_file and os.path.exists(temp_text_file) and\
               os.path.isfile(temp_text_file):
                os.remove(temp_text_file)
            if temp_zip_file and os.path.exists(temp_zip_file) and\
               os.path.isfile(temp_zip_file):
                os.remove(temp_zip_file)

    return result


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
