#!/usr/bin/env python3

# Author: Eugene Egbe
# Unit tests for the main routes in the reconciliation service

import unittest
import json
from flask import session

from service import app
from service.manifest.manifest import get_api_manifest


class TestApi(unittest.TestCase):
    
    # setup and teardown #

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()

    # executed after each test
    def tearDown(self):
        pass
    
    # tests #

    def test_get_manifest(self):
        response = self.app.get('/en/api', follow_redirects=True)
        response_data = json.loads(response.data.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['identifierSpace'], get_api_manifest('en')['identifierSpace'])
        self.assertEqual(response_data['name'], get_api_manifest('en')['name'])
        self.assertEqual(response_data['versions'], get_api_manifest('en')['versions'])
        self.assertEqual(response_data['schemaSpace'], get_api_manifest('en')['schemaSpace'])
        self.assertEqual(response_data['view']['url'], get_api_manifest('en')['view']['url'])

if __name__ == '__main__':
    unittest.main()
