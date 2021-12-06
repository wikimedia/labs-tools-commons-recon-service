#!/usr/bin/env python3

# Author: Eugene Egbe
# Unit tests for the Wikidata utility functions of the reconciliations service


import json
import unittest
import requests_mock

from service import app
from service.wikidata.wikidata import make_wd_properties_request, get_wikidata_entity_label
from service.reconcile.processresults import get_suggest_result, build_suggest_result, build_extend_meta_info


class TestWikidata(unittest.TestCase):
    
    # setup and teardown #
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()

        self.test_wd_properties_data = """
        {"entities":{"P180":{"type":"property","datatype":"wikibase-item","id":"P180","labels":{"en":{"language":"en","value":"depicts"}}}},"success":1}
        """
        self.wd_entity_label_data_2 = """
        {"entities":{"Q192465":{"type":"item","id":"Q192465","labels":{"en":{"language":"en","value":"Chick Corea"}}},"Q453406":{"type":"item","id":"Q453406","labels":{"en":{"language":"en","value":"Stanley Clarke"}}}}}
        """
        self.suggest_endpoint_data_result = """{"result":[{"description": "depicted entity", "id": "P180", "name": "depicts"}]}"""
        self.suggest_mock_result = """{"search":[{"id": "P180", "label": "depicts", "description": "depicted entity"}]}"""
        self.wd_entity_label_data = """
        {"searchinfo":{"search":"Q192465"},"search":[{"id":"Q192465","title":"Q192465","pageid":190630,"repository":"wikidata","url":"//www.wikidata.org/wiki/Q192465","concepturi":"http://www.wikidata.org/entity/Q192465","label":"Chick Corea","description":"American jazz and fusion pianist, keyboardist, and composer","match":{"type":"entityId","text":"Q192465"},"aliases":["Q192465"]}],"success":1}
        """
        self.meta_info_data = [{"id": "wikitext", "name": "Wikitext"}, {"id": "P180", "name": "depicts"}]

        self.properties = ["P180"]
        self.test_lang = "en"
        self.extend_properties = [{"id": "P180"}, {"id": "wikitext"}]

    # executed after each test
    def tearDown(self):
        pass
    
    # tests #

    def test_make_wd_properties_request(self):
        with requests_mock.Mocker() as m:
            m.get("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=P180&format=json",
                  text=self.test_wd_properties_data)
            response = make_wd_properties_request(self.properties, self.test_lang)

        self.assertEqual(response, json.loads(self.test_wd_properties_data))

    
    def test_get_wikidata_entity_label(self):
        wd_ids = ["Q192465", "Q453406"]
        with requests_mock.Mocker() as m:
            m.get("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q192465|Q453406&format=json&languages=en&props=labels",
                  text=self.wd_entity_label_data_2)
            response = get_wikidata_entity_label(wd_ids, self.test_lang)

        self.assertEqual(response, json.loads(self.wd_entity_label_data_2)["entities"])


    def test_make_suggest_request(self):
        prefix = "depicts"
        with requests_mock.Mocker() as m:
            m.get("https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=property&search="+prefix,
                  text=self.suggest_mock_result)

            suggest_result = get_suggest_result(prefix, self.test_lang)
            self.assertEqual(suggest_result, json.loads(self.suggest_endpoint_data_result))


    def test_get_suggest_result(self):
        prefix = "depicts"
        with requests_mock.Mocker() as m:
            m.get("https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=property&search="+prefix,
                  text=self.suggest_mock_result)

            suggest_result = get_suggest_result(prefix, self.test_lang)
            self.assertEqual(suggest_result, json.loads(self.suggest_endpoint_data_result))


    def test_build_suggest_result(self):
        prefix = "depicts"
        with requests_mock.Mocker() as m:
            m.get("https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=property&search="+prefix,
                  text=self.suggest_mock_result)
            
            suggest_result = build_suggest_result(prefix, json.loads(self.suggest_mock_result)['search'])
            self.assertEqual(suggest_result, json.loads(self.suggest_endpoint_data_result))


    def test_build_extend_meta_info(self):
        with requests_mock.Mocker() as m:
            m.get("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=P180&format=json",
                  text=self.test_wd_properties_data)
            response = build_extend_meta_info(self.extend_properties, self.test_lang)

        self.assertEqual(response, self.meta_info_data)


if __name__ == '__main__':
    unittest.main()
