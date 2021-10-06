#!/usr/bin/env python3

# Authors: Eugene Egbe
# Utility functions for api blueprint

import sys
import requests

from service import app


def extract_file_names(query_data):
    """ Extract file name from the queries data.

        Parameters:
            query_data (obj): The queries data object.

        Returns:
            query_string (str): A concatenated string of file names.
    """
    
    return '|'.join(entry['query'] for entry in query_data.values())


def make_commons_search(query_string):
    """ Makes request to commons API to get images info

        Parameters:
            query_string (str): The concatenated file names.

        Returns:
            pages (obj): Json object of image inforamtion.
    """

    S = requests.Session()
    url = app.config['API_URL']
    PARAMS = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "titles": query_string
    }

    r = S.get(url=url, params=PARAMS)
    data = r.json()
    pages = data["query"]["pages"]

    return pages


def build_query_result_object(page):
    """ Builds result object for an image info.

        Parameters:
            page (obj): Page object of search result.

        Returns:
            query_result_object (obj): Result object of image.
    """

    result_object = {}
    result_array = []
    query_result_object = {}

    result_object['id'] = 'M' + str(page['pageid'])
    result_object['name'] = page['title']
    result_array.append(result_object)
    query_result_object['result'] = result_array

    return query_result_object


def build_results(query_data, results):
    """ Builds result using image search results.

        Parameters:
            query_data (obj): Query data from api request.
            results (obj): Results from image search from wmc api.

        Returns:
            overall_query_object (obj): Reconciliation api result for queries.
    """

    overall_query_object = {}

    query_labels = list(query_data.keys())
    query_values = [value['query'] for value in query_data.values()]
    result_values = list(results.values())

    for i in range(0, len(result_values)):

        if 'pageid' in result_values[i]:

            # Files are sorted by commons api so we find the results index in query data
            element_index_in_results = query_values.index(result_values[i]['title'])
            overall_query_object[query_labels[element_index_in_results]] = build_query_result_object(result_values[i])
        else:
            overall_query_object[query_labels[i]] = {'result': []}

    return overall_query_object
