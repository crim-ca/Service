#!/usr/bin/env python
# coding:utf-8

"""
This module defines a format for the report written by the worker
after each task and sent to the platform.
"""

# -- standard library ---------------------------------------------------------
from enum import Enum
import json
import copy


class ReportStatus(Enum):
    Init = 0
    Processing = 1
    Success = 2
    Failure = 3


class TaskStatus(Enum):
    Queued = 0
    Processing = 1
    Success = 2
    Failure = 3
    Ignore = 4


class WorkerReportEncoder(json.JSONEncoder):
    """
    JSON encoder for the worker report
    """
    def encode(self, o):
        if isinstance(o, WorkerReport):
            obj = copy.deepcopy(o)
            obj.status = obj.status.name.lower()
            obj.detail = [tr.to_dict() for tr in obj.detail]
            return json.JSONEncoder().encode(vars(obj))
        return json.JSONEncoder().encode(o)


class WorkerReport:

    def __init__(self, nb_tasks=0):
        """
        Class defining the information included in the worker report
        """

        self.status = ReportStatus.Init
        self.completion_ratio = 0
        self.nb_tasks = nb_tasks
        self.nb_success = 0
        self.nb_ignores = 0
        self.nb_failures = 0
        self.detail = []

    def set_nb_tasks(self, nb_tasks):
        """
        Set the number of tasks
        :param nb_tasks:
        :return:
        """
        self.nb_tasks = nb_tasks

    def update(self, task_report):
        """
        Update the worker report after the execution of a task
        :param task_report: The report produced after the execution of a task
        :type task_report: TaskReport
        :return:
        """
        self.detail.append(task_report)
        if task_report.status == TaskStatus.Success:
            self.nb_success += 1
        elif task_report.status == TaskStatus.Ignore:
            self.nb_ignores += 1
        else:
            self.nb_failures += 1

    def set_processing(self):
        """
        Set the status of the report to "Processing"
        """
        self.status = ReportStatus.Processing

    def set_succeeded(self):
        """
        Set the status of the report to "Success"
        """
        self.status = ReportStatus.Success

    def set_failed(self):
        """
        Set the status of the report to "Failure"
        """
        self.status = ReportStatus.Failure

    def update_completion_ratio(self):
        """
        Calculate and update the completion ratio
        """
        if self.nb_tasks != 0:
            self.completion_ratio = \
                (self.nb_success + self.nb_ignores + self.nb_failures) \
                / self.nb_tasks

    def to_json(self):
        """
        :return: The report as a JSON document
        """
        encoder = WorkerReportEncoder()
        return encoder.encode(self)

    def abbreviated_json(self, url):
        """
        Encode the report in an abbreviated form,
        indicating the url of the full report
        :param url: the url of the full report
        :return:
        """
        report_dict = dict(status=self.status.name.lower(),
                           completion_ratio=self.completion_ratio,
                           nb_tasks=self.nb_tasks,
                           nb_success=self.nb_success,
                           nb_ignores=self.nb_ignores,
                           nb_failures=self.nb_failures,
                           full_report_url=url)
        encoder = json.JSONEncoder()
        return encoder.encode(report_dict)


class TaskReport:

    def __init__(self, doc_id, tool):
        """
        Class defining the status of a task
        :param doc_id: the id of the document to be processed
        :param tool: The worker tool
        """
        self.status = TaskStatus.Queued
        self.doc_id = doc_id
        self.step = tool
        self.code = 0
        self.message = ""

    def to_dict(self):
        """
        :return: the report in a dict form
        """
        tr_dict = dict()
        tr_dict["doc_id"] = self.doc_id
        tr_dict["step"] = self.step
        if self.status == TaskStatus.Failure:
            tr_dict["code"] = self.code
            tr_dict["message"] = self.message
        tr_dict["status"] = self.status.name.lower()
        return tr_dict

    def set_succeeded(self):
        """
        Set the status of the report to "Success"
        """
        self.status = TaskStatus.Success

    def set_ignored(self):
        """
        Set the status of the report to "Ignore"
        """
        self.status = TaskStatus.Ignore

    def set_failed(self, code, message):
        """
        Set the status of the report to "Failure"
        :param code: the error code
        :param message: the error message
        """
        self.status = TaskStatus.Failure
        self.code = code
        self.message = message

    def set_processing(self):
        self.status = TaskStatus.Processing
