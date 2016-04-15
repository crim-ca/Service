#!/usr/bin/env python
# coding:utf-8

"""
This module offers the downloading entry point for a given remote ressource..
"""

# -- Standard library --------------------------------------------------------
import optparse

# --Project specific----------------------------------------------------------
from . import RemoteAccess


def main():
    """
    Command line entry point.
    """
    usage = '%prog url'
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-c', '--credentials', dest='credentials_fn',
                      help='Path to crendentials filename',
                      default=None)
    args = parser.parse_args()[-1]
    if len(args) != 1:
        parser.error('Insufficient arguments')

    doc_msg = {'url': args[0], 'credentials': None}
    doc = RemoteAccess.download(doc_msg)
    print("Downloaded file is at «{fn}»".format(fn=doc.local_path))

if __name__ == '__main__':
    main()
