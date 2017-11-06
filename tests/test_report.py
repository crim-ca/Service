# coding:utf-8

# -- standard library ---------------------------------------------------------
import json
import unittest

# --Modules to test -----------------------------------------------------------
from VestaService.Report import WorkerReport, TaskReport


class UtilsTests(unittest.TestCase):

    def test_WorkerReport_update(self):
        wr = WorkerReport(nb_tasks=3)
        tr = TaskReport(doc_id="secret", tool="screwdriver")
        tr.set_succeeded()
        wr.update(tr)
        self.assertEqual(wr.nb_success, 1,
                         msg="Error by updating a worker report "
                             "with a successful task report.")
        tr.set_failed(code=444, message="No screwdriver in this drawer.")
        wr.update(tr)
        self.assertEqual(wr.nb_failures, 1,
                         msg="Error by updating a worker report "
                             "with a failed task report.")
        self.assertEqual(len(wr.detail), 2,
                         msg="Error by updating a worker report "
                             "with a failed task report. "
                             " Wrong number of tasks.")

    def test_WorkerReport_tojson(self):
        wr = WorkerReport(nb_tasks=2)
        tr = TaskReport(doc_id="secret", tool="screwdriver")
        tr.set_succeeded()
        wr.update(tr)
        tr2 = TaskReport(doc_id="secret", tool="screwdriver")
        tr2.set_failed(code=444, message="No screwdriver in this drawer.")
        wr.update(tr2)
        wr.set_succeeded()
        wr.update_completion_ratio()
        attended_wrjson_str = ('{"nb_success": 1, "nb_ignores": 0, '
                               '"nb_failures": 1, "completion_ratio" : 1.0, '
                               '"nb_tasks" : 2, "status" : "success",'
                               '"detail": ['
                               '{"doc_id" : "secret", "step" : "screwdriver", '
                               '"status" : "success"},'
                               '{"doc_id" : "secret", "step" : "screwdriver", '
                               '"status" : "failure", "code":444, '
                               '"message" : "No screwdriver in this drawer."}'
                               ']'
                               '}')
        wrjson = wr.to_json()
        self.assertEqual(json.JSONDecoder().decode(wrjson),
                         json.JSONDecoder().decode(attended_wrjson_str))

    def test_WorkerReport_abbreviated_json(self):
        wr = WorkerReport(nb_tasks=2)
        tr = TaskReport(doc_id="secret", tool="screwdriver")
        tr.set_succeeded()
        wr.update(tr)
        tr2 = TaskReport(doc_id="secret", tool="screwdriver")
        tr2.set_failed(code=444, message="No screwdriver in this drawer.")
        wr.update(tr2)
        wr.set_succeeded()
        wr.update_completion_ratio()
        attended_wrjson_str = ('{"nb_success": 1, "nb_ignores": 0, '
                               '"nb_failures": 1, "completion_ratio" : 1.0, '
                               '"nb_tasks" : 2, "status" : "success",'
                               '"full_report_url":"http://mss:1234"'
                               '}')
        wrjson = wr.abbreviated_json("http://mss:1234")
        self.assertEqual(json.JSONDecoder().decode(wrjson),
                         json.JSONDecoder().decode(attended_wrjson_str))
