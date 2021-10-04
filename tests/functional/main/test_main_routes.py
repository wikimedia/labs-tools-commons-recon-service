#!/usr/bin/env python3

# Author: Eugene Egbe
# Unit tests for the main routes in the reconciliation service

import unittest

from service import app


class TestMain(unittest.TestCase):
    
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
    def test_home_route(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
