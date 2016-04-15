#!/usr/bin/env python3

"""
Send contents to server.
"""

from subprocess import check_call
from urllib.parse import urljoin
from shlex import split
import argparse
import logging


from conf import __version__ as VERSION

DOC_DESTINATION = ("/dev/null")


def norm_perms():
    """
    Normalize permissions in the build directory.
    """
    cmd = split("find _build/html/ -type d -exec chmod o+x '{}' ';'")
    check_call(cmd)
    cmd = split("chmod -R o+r _build/html/")
    check_call(cmd)


def send_static(destination=DOC_DESTINATION):
    """
    Send static site on server.
    """
    logger = logging.getLogger(__name__)
    cmd = split("rsync -av _build/html/")
    dest = urljoin(destination, VERSION)
    logger.info("Sending documentation to %s", dest)
    cmd += [dest]
    check_call(cmd)


def main():
    """
    Command line entry point.
    """
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',
                        action='store',
                        default=DOC_DESTINATION,
                        help="Where the static version of the documentation "
                             "will be sent, "
                             "default={}".format(DOC_DESTINATION))
    args = parser.parse_args()
    norm_perms()
    send_static(destination=args.destination)


if __name__ == '__main__':
    main()
