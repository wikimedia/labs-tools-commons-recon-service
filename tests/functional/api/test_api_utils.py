#!/usr/bin/env python3

# Author: Eugene Egbe
# Unit tests for the api utility functions in the reconciliation service


import unittest

from service.api.utils import extract_file_names, build_results, build_query_result_object


class TestApiUtils(unittest.TestCase):
    """Test utility functions in the api blueprint."""

    def setUp(self):

        self.file_not_found = {
            'q0': {
                'query': 'File:filenot+found+query.jpg'
            }
        }
        self.fake_page_not_found = {
            '-1': {
                'ns': 6,
                'title': 'File:Filenot found query.jpg',
                'missing': '',
                'imagerepository': ''
            }
        }

        self.fake_page_not_found_result = {
            'q0': {
                'result': []
            }
        }

        self.fake_query = {
            'q0': {
                'query': 'File:Commons-logo.svg'
            }
        }

        self.fake_page = {
            '317966': {
                'pageid': 317966,
                'ns': 6,
                'title': 'File:Commons-logo.svg',
                'imagerepository': 'local',
                'imageinfo': [
                    {
                        'timestamp': '2014-06-03T13:43:45Z',
                        'user': 'Steinsplitter'
                    }
                ]
            }
        }

        self.query_string = extract_file_names(self.fake_query)

        self.fake_queries = {
            'q0': {
                'query': 'File:Commons-logo.svg'
            },
            'q1': {
                'query': 'File:Hudson Commons (95051).jpg'
            }
        }

        self.fake_query_result_object = {
            'result': [
                {
                    'id': 'M317966',
                    'name': 'File:Commons-logo.svg'
                }
            ]
        }

        self.fake_pages = {
            '317966': {
                'pageid': 317966,
                'ns': 6,
                'title': 'File:Commons-logo.svg',
                'imagerepository': 'local',
                'imageinfo': [
                    {
                        'timestamp': '2014-06-03T13:43:45Z',
                        'user': 'Steinsplitter'
                    }
                ]
            },
            '83241361': {
                'pageid': 83241361,
                'ns': 6,
                'title': 'File:Hudson Commons (95051).jpg',
                'imagerepository': 'local',
                'imageinfo': [
                    {
                        'timestamp': '2019-10-21T00:01:07Z',
                        'user': 'Rhododendrites'
                    }
                ]
            }
        }
        self.fake_result = {
            'q0': {
                'result': [
                    {
                        'id': 'M317966',
                        'name': 'File:Commons-logo.svg'
                    }
                ]
            }
        }
        self.fake_results = {
            'q0': {
                'result': [
                    {
                        'id': 'M317966',
                        'name': 'File:Commons-logo.svg'
                    }
                ]
            },
            'q1': {
                'result': [
                    {
                        'id': 'M83241361',
                        'name': 'File:Hudson Commons (95051).jpg'
                    }
                ]
            }
        }


    def tearDown(self):
        pass


    def test_extract_file_names(self):
        self.assertEqual(self.query_string, 'File:Commons-logo.svg')


    def test_build_results(self):
        result = build_results(self.fake_query, self.fake_page)
        self.assertEqual(result, self.fake_result)


    def test_build_results_with_many_queries(self):
        fake_build_objects = build_results(self.fake_queries, self.fake_pages)
        self.assertEqual(fake_build_objects, self.fake_results)


    def test_build_results_with_file_not_found(self):
        fake_build_object = build_results(self.file_not_found, self.fake_page_not_found)
        self.assertEqual(fake_build_object, self.fake_page_not_found_result)


    def test_build_query_result_object(self):
        result = build_query_result_object(self.fake_page['317966'])
        self.assertEqual(result, self.fake_query_result_object)


if __name__ == '__main__':
    unittest.main()
