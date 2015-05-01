#!/usr/bin/env python
# coding:utf-8

"""
This module documents exception types in the service architecture.
"""


# -- Exception types ----------------------------------------------------------
class ServiceException(Exception):
    """
    Base package exception type.
    """
    pass


class AnnotationsUndeliverable(ServiceException):
    """
    Indicates that annotations could not be delivered.
    """
    pass


class InvalidDocumentPath(ServiceException):
    """
    Indicates that a document cannot be found at given path.
    """
    pass


class InvalidConfigType(ServiceException):
    """
    Indicates that a configuration type is invalid.
    """
    pass


class ConfigFileNotFound(ServiceException):
    """
    Indicates that a configuration file could not be found.
    """
    pass


class InvalidDocumentType(ServiceException):
    """
    Indicates that the Service cannot use the submitted document type.
    """
    pass


class DownloadError(ServiceException):
    """
    Indicates that a requested download could not be performed.
    """
    pass


class UploadError(ServiceException):
    """
    Indicates that a document cannot be uploaded error.
    """
    pass


class InvalidAnnotationFormat(ServiceException):
    """
    Indicates that an annotations object should be of type list.
    """
    pass


class MissingArgumentError(ServiceException):
    """
    Indicates that a required argument was not supplied.
    """
    pass
