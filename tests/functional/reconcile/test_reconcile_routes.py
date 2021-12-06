#!/usr/bin/env python3

# Author: Eugene Egbe
# Unit tests for the main routes in the reconciliation service


import unittest
import json
import requests_mock

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
        self.commons_response = """
        {"continue":{"iistart":"2014-04-10T10:05:06Z","continue":"||"},"query":{"pages":{"317966":{"pageid":317966,"ns":6,"title":"File:Commons-logo.svg","imagerepository":"local","imageinfo":[{"timestamp":"2014-06-03T13:43:45Z","user":"Steinsplitter"}]}}}}
        """

        self.commons_response_many_files = """
        {"batchcomplete":"","query":{"pages":{"74943657":{"pageid":74943657,"ns":6,"title":"File:Allah-green-transparent.svg","imagerepository":"local","imageinfo":[{"timestamp":"2018-12-09T10:44:53Z","user":"\u042e\u043a\u0430\u0442\u0430\u043d"}]},"317966":{"pageid":317966,"ns":6,"title":"File:Commons-logo.svg","imagerepository":"local","imageinfo":[{"timestamp":"2014-06-03T13:43:45Z","user":"Steinsplitter"}]}}}}        """

        self.commons_response_no_file = """
        {"batchcomplete":"","query":{"pages":{"-1":{"ns":0,"title":"File:Filenot found query.jpg","missing":""}}}}
        """

        self.fake_queries = {
            'q0': {
                'query': 'File:Commons-logo.svg'
            },
            'q1': {
                'query': 'File:Allah-green-transparent.svg'
            }
        }

        self.extend_data = {"ids": ["M74698470"], "properties": [{"id": "P180"}, {"id": "wikitext"}]}

        self.file_not_found = {
            'q0': {
                'query': 'File:filenot found query.jpg'
            }
        }

        self.fake_page_not_found_result = {
            'q0': {
                'result': []
            }
        }

        self.test_wmc_properties_data = """
        {"entities":{"M74698470":{"pageid":74698470,"ns":6,"title":"File:Chick Corea & Stanley Clarke.jpg","lastrevid":590206738,"modified":"2021-09-10T13:54:13Z","type":"mediainfo","id":"M74698470","labels":{"en":{"language":"en","value":"Chick Corea and Stanley Clarke playing at the San Sebastian Jazz Festival"}},"descriptions":{},"statements":{"P180":[{"mainsnak":{"snaktype":"value","property":"P180","hash":"a83bcd35f5bd70a205d9eabf429841a6a091d973","datavalue":{"value":{"entity-type":"item","numeric-id":192465,"id":"Q192465"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$c598e90e-44b9-6214-64aa-367e4b2415b6","rank":"normal"},{"mainsnak":{"snaktype":"value","property":"P180","hash":"988edf83d80d66fd97714b6c977f5f3097ee194d","datavalue":{"value":{"entity-type":"item","numeric-id":453406,"id":"Q453406"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$209cb38c-4471-7fc6-5a0e-8232ab7a506c","rank":"normal"}],"P571":[{"mainsnak":{"snaktype":"value","property":"P571","hash":"54625c04bd96974fbcc9eaafd896b65789e15321","datavalue":{"value":{"time":"+2014-07-25T00:00:00Z","timezone":0,"before":0,"after":0,"precision":11,"calendarmodel":"http://www.wikidata.org/entity/Q1985727"},"type":"time"}},"type":"statement","id":"M74698470$2CF35829-A88D-4104-98D7-FF3CC91851EC","rank":"normal"}],"P4082":[{"mainsnak":{"snaktype":"value","property":"P4082","hash":"8227ba960548c059dce2c79cb1fa18cceb0d1d11","datavalue":{"value":{"entity-type":"item","numeric-id":64962,"id":"Q64962"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$6F8D50B9-32DE-4CB4-B7EE-99B4E0184B77","rank":"normal"}],"P6216":[{"mainsnak":{"snaktype":"value","property":"P6216","hash":"5570347fdc76d2a80732f51ea10ee4b144a084e0","datavalue":{"value":{"entity-type":"item","numeric-id":50423863,"id":"Q50423863"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$2C4F3C48-03FC-4E21-9C3A-817E4AF0D7DE","rank":"normal"}],"P275":[{"mainsnak":{"snaktype":"value","property":"P275","hash":"ec6e754c5042e13b53376139e505ebd6708745a4","datavalue":{"value":{"entity-type":"item","numeric-id":18199165,"id":"Q18199165"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$80F83CD2-BE41-4352-BEA1-06DB1D5C3A74","rank":"normal"}],"P7482":[{"mainsnak":{"snaktype":"value","property":"P7482","hash":"83568a288a8b8b4714a68e7239d8406833762864","datavalue":{"value":{"entity-type":"item","numeric-id":66458942,"id":"Q66458942"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$D169279B-414F-4A4B-8283-DA8B82DEDCB4","rank":"normal"}],"P170":[{"mainsnak":{"snaktype":"somevalue","property":"P170","hash":"d3550e860f988c6675fff913440993f58f5c40c5"},"type":"statement","qualifiers":{"P3831":[{"snaktype":"value","property":"P3831","hash":"c5e04952fd00011abf931be1b701f93d9e6fa5d7","datavalue":{"value":{"entity-type":"item","numeric-id":33231,"id":"Q33231"},"type":"wikibase-entityid"}}],"P2093":[{"snaktype":"value","property":"P2093","hash":"d0bea75f2e24eb80feb7691e3e105bb0e8721837","datavalue":{"value":"Vidartereyes","type":"string"}}],"P4174":[{"snaktype":"value","property":"P4174","hash":"a4f30c83bf177b57b01d07f9d1b8fd05125fc075","datavalue":{"value":"Vidartereyes","type":"string"}}]},"qualifiers-order":["P3831","P2093","P4174"],"id":"M74698470$1C77D5CE-0C84-416C-B28B-4602B4D0FE7B","rank":"normal"}],"P276":[{"mainsnak":{"snaktype":"value","property":"P276","hash":"86162b532637cb4969378e50c865ad176b64dc9b","datavalue":{"value":{"entity-type":"item","numeric-id":2349872,"id":"Q2349872"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$0082e5e9-415a-97f2-2bd7-16334700e721","rank":"normal"}]}}},"success":1}
        """
        self.wd_entity_label_data_2 = """
        {"entities":{"Q192465":{"type":"item","id":"Q192465","labels":{"en":{"language":"en","value":"Chick Corea"}}},"Q453406":{"type":"item","id":"Q453406","labels":{"en":{"language":"en","value":"Stanley Clarke"}}}}}
        """
        self.test_wd_properties_data = """
        {"entities":{"P180":{"type":"property","datatype":"wikibase-item","id":"P180","labels":{"en":{"language":"en","value":"depicts"}}}},"success":1}
        """
        self.commons_wikitext_data = """
        {"parse":{"title":"File:Chick Corea & Stanley Clarke.jpg","pageid":74698470,"wikitext":{"*":"== {{int:filedesc}} =="}}}
        """
        self.extend_data_result = """
        {"meta":[{"id": "wikitext","name": "Wikitext"},{"id":"P180","name": "depicts"}],"rows":{"M74698470":{"P180":[{"id": "Q192465","name": "Chick Corea"},{"id": "Q453406","name": "Stanley Clarke"}],"wikitext": [{"str":"== {{int:filedesc}} =="}]},"M83241361":{"P180":[],"wikitext": ["== {{int:filedesc}} =="]}}}
        """
        self.suggest_mock_result = """{"search":[{"id": "P180", "label": "depicts", "description": "depicted entity"}]}"""
        self.suggest_endpoint_data_result = """{"result":[{"description": "depicted entity", "id": "P180", "name": "depicts"}]}"""

    # executed after each test
    def tearDown(self):
        pass


    # tests #


    def test_home_route(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


    def test_get_manifest_without_queries(self):
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
        with requests_mock.Mocker() as m:
            m.get('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&titles=File:Commons-logo.svg', text=self.commons_response)

            response = self.app.get('/en/api?queries={}'.format(json.dumps(self.fake_query)), follow_redirects=True)
            results = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(results['q0']['result'][0]['id'], 'M317966')
        self.assertEqual(results['q0']['result'][0]['name'], 'File:Commons-logo.svg')


    # def test_get_manifest_with_many_queries(self):

    #     with requests_mock.Mocker() as m:
    #         m.get('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&titles=File:Commons-logo.svg|File:Allah-green-transparent.svg',
    #               text=self.commons_response_many_files)

    #         response = self.app.get('/en/api?queries={}'.format(json.dumps(self.fake_queries)), follow_redirects=True)
    #         results = json.loads(response.data.decode('utf-8'))

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(results['q0']['result'][0]['id'], 'M317966')
    #     self.assertEqual(results['q0']['result'][0]['name'], 'File:Commons-logo.svg')
    #     self.assertEqual(results['q1']['result'][0]['id'], 'M74943657')
    #     self.assertEqual(results['q1']['result'][0]['name'], 'File:Allah-green-transparent.svg')


    def test_get_manifest_with_file_not_found(self):
        with requests_mock.Mocker() as m:
            m.get('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&titles=File:filenot found query.jpg',
                  text=self.commons_response_no_file)
            response = self.app.get('/en/api?queries={}'.format(json.dumps(self.file_not_found)), follow_redirects=True)
            results = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(results, self.fake_page_not_found_result)


    def test_extend_with_no_parameters(self):
        response = self.app.get('/en/api?extend={}'.format(json.dumps({})), follow_redirects=True)
        response_data = json.loads(response.data.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, {})


    def test_extend_with_data(self):
        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=wbgetentities&format=json&languages=en&ids=M74698470",
                  text=self.test_wmc_properties_data)
            m.get("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q192465|Q453406&format=json&languages=en&props=labels",
                  text=self.wd_entity_label_data_2)
            m.get("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=P180&format=json",
                  text=self.test_wd_properties_data)
            m.get("https://commons.wikimedia.org/w/api.php?action=parse&format=json&pageid=74698470&prop=wikitext",
                  text=self.commons_wikitext_data)

            response = self.app.get('/en/api?extend={}'.format(json.dumps(self.extend_data)), follow_redirects=True)
            response_data = json.loads(response.data.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['meta'], json.loads(self.extend_data_result)['meta'])
        self.assertEqual(response_data['rows']['M74698470']['P180'], json.loads(self.extend_data_result)['rows']['M74698470']['P180'])


    def test_suggest_properties_with_true_params(self):
        with requests_mock.Mocker() as m:
            m.get("https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=property&search=depicts",
                  text=self.suggest_mock_result)

            response = self.app.get("/en/api/suggest/properties?prefix=depicts", follow_redirects=True)
            response_data = json.loads(response.data.decode('utf8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, json.loads(self.suggest_endpoint_data_result))


if __name__ == '__main__':
    unittest.main()
