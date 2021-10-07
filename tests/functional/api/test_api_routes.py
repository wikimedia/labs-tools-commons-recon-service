#!/usr/bin/env python3

# Author: Eugene Egbe
# Unit tests for the main routes in the reconciliation service


import unittest
import json

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

        self.fake_query = {
            'q0': {
                'query': 'File:Commons-logo.svg'
            }
        }

        self.fake_queries = {
            'q0': {
                'query': 'File:Commons-logo.svg'
            },
            'q1': {
                'query': 'File:Hudson Commons (95051).jpg'
            }
        }

        self.file_not_found = {
            'q0': {
                'query': 'File:filenot+found+query.jpg'
            }
        }
        
        self.fake_page_not_found_result = {
            'q0': {
                'result': []
            }
        }

    # executed after each test
    def tearDown(self):
        pass


    # tests #


    def test_get_manifest(self):
        response = self.app.get('/en/api', follow_redirects=True)
        response_data = json.loads(response.data.decode('utf8'))
        service_manifest = get_api_manifest('en', app.config['SERVICE_URL'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['identifierSpace'], service_manifest['identifierSpace'])
        self.assertEqual(response_data['name'], service_manifest['name'])
        self.assertEqual(response_data['versions'], service_manifest['versions'])
        self.assertEqual(response_data['schemaSpace'], service_manifest['schemaSpace'])
        self.assertEqual(response_data['view']['url'], service_manifest['view']['url'])


    def test_get_manifest_with_single_query(self):
        response = self.app.get('/en/api?queries={}'.format(json.dumps(self.fake_query)), follow_redirects=True)
        results = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(results['q0']['result'][0]['id'], 'M317966')
        self.assertEqual(results['q0']['result'][0]['name'], 'File:Commons-logo.svg')


    def test_get_manifest_with_many_queries(self):
        response = self.app.get('/en/api?queries={}'.format(json.dumps(self.fake_queries)), follow_redirects=True)
        results = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(results['q0']['result'][0]['id'], 'M317966')
        self.assertEqual(results['q0']['result'][0]['name'], 'File:Commons-logo.svg')
        self.assertEqual(results['q1']['result'][0]['id'], 'M83241361')
        self.assertEqual(results['q1']['result'][0]['name'], 'File:Hudson Commons (95051).jpg')


    def test_post_manifest_with_single_query(self):
        response = self.app.post('/en/api?queries={}'.format(json.dumps(self.fake_query)), follow_redirects=True)
        results = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(results['q0']['result'][0]['id'], 'M317966')
        self.assertEqual(results['q0']['result'][0]['name'], 'File:Commons-logo.svg')


    def test_post_manifest_with_many_queriess(self):
        response = self.app.post('/en/api?queries={}'.format(json.dumps(self.fake_queries)), follow_redirects=True)
        results = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(results['q0']['result'][0]['id'], 'M317966')
        self.assertEqual(results['q0']['result'][0]['name'], 'File:Commons-logo.svg')
        self.assertEqual(results['q1']['result'][0]['id'], 'M83241361')
        self.assertEqual(results['q1']['result'][0]['name'], 'File:Hudson Commons (95051).jpg')


    def test_get_manifest_with_file_not_found(self):
        response = self.app.get('/en/api?queries={}'.format(json.dumps(self.file_not_found)), follow_redirects=True)
        results = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(results, self.fake_page_not_found_result)


if __name__ == '__main__':
    unittest.main()
