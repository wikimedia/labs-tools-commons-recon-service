#!/usr/bin/env python3

# Author: Eugene Egbe
# Unit tests for the Wikidata utility functions of the reconciliations service


import json
import unittest
import requests_mock

from service import app
from service.properties.property_suggest import get_property_suggest_results



class TestProperties(unittest.TestCase):
    
    # setup and teardown #
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()

        self.properties_suggest_result = """{"properties": [{"id": "wikitext","name": "Wikitext"},{"id": "P180","name": "depicts"},{"id": "P6243","name": "digital representation of"},{"id": "P921","name": "main subject"},{"id": "P170","name": "creator"},{"id": "P571","name": "inception"},{"id": "P1071","name": "location of creation"},{"id": "P195","name": "collection"},{"id": "P7482","name": "source of file"},{"id": "P6216","name": "copyright status"},{"id": "P275","name": "copyright license"},{"id": "P1259","name": "coordinates of the point of view"}],"type": "mediafile"}"""
        self.properties_suggest_mock_data = """{"entities": {"P180": {"type": "property", "datatype": "wikibase-item", "id": "P180", "labels": {"en": {"language": "en", "value": "depicts"}}}, "P6243": {"type": "property", "datatype": "wikibase-item", "id": "P6243", "labels": {"en": {"language": "en", "value": "digital representation of"}}}, "P921": {"type": "property", "datatype": "wikibase-item", "id": "P921", "labels": {"en": {"language": "en", "value": "main subject"}}}, "P170": {"type": "property", "datatype": "wikibase-item", "id": "P170", "labels": {"en": {"language": "en", "value": "creator"}}}, "P571": {"type": "property", "datatype": "time", "id": "P571", "labels": {"en": {"language": "en", "value": "inception"}}}, "P1071": {"type": "property", "datatype": "wikibase-item", "id": "P1071", "labels": {"en": {"language": "en", "value": "location of creation"}}}, "P195": {"type": "property", "datatype": "wikibase-item", "id": "P195", "labels": {"en": {"language": "en", "value": "collection"}}}, "P7482": {"type": "property", "datatype": "wikibase-item", "id": "P7482", "labels": {"en": {"language": "en", "value": "source of file"}}}, "P6216": {"type": "property", "datatype": "wikibase-item", "id": "P6216", "labels": {"en": {"language": "en", "value": "copyright status"}}}, "P275": {"type": "property", "datatype": "wikibase-item", "id": "P275", "labels": {"en": {"language": "en", "value": "copyright license"}}}, "P1259": {"type": "property", "datatype": "globe-coordinate", "id": "P1259", "labels": {"en": {"language": "en", "value": "coordinates of the point of view"}}}}, "success": 1}"""

    # executed after each test


    def tearDown(self):
        pass
    
    # tests #

    def test_get_property_suggest_results(self):
        with requests_mock.Mocker() as m:
            m.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&languages=en&props=labels&ids=P180|P6243|P921|P170|P571|P1071|P195|P7482|P6216|P275|P1259",
                  text=self.properties_suggest_mock_data)
            suggest_properties = get_property_suggest_results('en')
        self.assertEqual(suggest_properties, json.loads(self.properties_suggest_result))


if __name__ == '__main__':
    unittest.main()
