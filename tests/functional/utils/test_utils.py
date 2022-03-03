#!/usr/bin/env python3

# Author: Eugene Egbe
# Unit tests for the utility functions in the reconciliation service


from sys import prefix
import unittest

import json

from service import app
from service.utils.utils import validate_input, check_valid_json


class TestUtils(unittest.TestCase):
    """Test utility functions in the reconciliation service."""

    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["DEBUG"] = False
        self.app = app.test_client()
        self.sample_valid_input = """{"q0":{"query": "File:Commons-logo.svg"}}"""
        self.sample_invalid_input = """{"q1":"g"}}"""
        self.valid_input_result = {"q0": {"query": "File:Commons-logo.svg"}}
        self.invalid_input_response_data = """{"error": "error", "message": "Invalid input provided"}"""

    def tearDown(self):
        pass


    def test_validate_input_with_valid_input(self):
        result = validate_input(self.sample_valid_input)
        self.assertEqual(result, True)


    def test_check_valid_json_invalid(self):
        result = check_valid_json(self.sample_invalid_input)
        self.assertEqual(result, False)


    def test_check_valid_json_valid(self):
        result = check_valid_json(self.sample_valid_input)
        self.assertEqual(result, True)


    def test_validate_input_with_invalid_input_queries(self):
        response = self.app.get("/en/api?queries={'q1':'g\"}\"}", follow_redirects=True)
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data, json.loads(self.invalid_input_response_data))


    def test_validate_input_with_invalid_input_extend(self):
        response = self.app.get("/en/api?extend={'q1':'g\"}\"}", follow_redirects=True)
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data, json.loads(self.invalid_input_response_data))


    def test_validate_input_with_invalid_Mid_input_extend(self):
        response = self.app.get("/en/api?extend={'ids':['M-Number'],'properties':[{'id':'P571'}]}", follow_redirects=True)
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data, json.loads(self.invalid_input_response_data))


if __name__ == "__main__":
    unittest.main()
