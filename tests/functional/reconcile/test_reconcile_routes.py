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
        self.extend_caption_data = {"ids": ["M86236603"], "properties": [{"id": "Cen"}]}

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
        self.sample_caption_file_info = """{"batchcomplete": "","query": {"pages": {"86236603": {"pageid": 86236603,"ns": 6,"title": "File:COVID-19_Outbreak_World_Map.svg"}}}}"""
        self.suggest_mock_result = """{"search":[{"id": "P180", "label": "depicts", "description": "depicted entity"}]}"""
        self.suggest_endpoint_data_result = """{"result":[{"description": "depicted entity", "id": "P180", "name": "depicts"}]}"""
        self.sample_commons_captions_data = """{"entities":{"M86236603":{"labels":{"en":{"language":"en","value": "World map of total cumulative confirmed COVID-19 cases by country."}}}}}"""
        self.caption_extend_data_result = """{"meta":[{"id":"Cen","name":"Caption [en]"}],"rows":{"M86236603":{"Cen":[{"str": "World map of total cumulative confirmed COVID-19 cases by country."}]}}}"""

        self.commons_id_page_query_data = """{"batchcomplete":"","query":{"pages":{"317966":{"pageid":317966,"ns":6,"title":"File:Commons-logo.svg"}}}}"""
        self.commons_media_url_query_data = """{"continue":{"iistart":"2014-04-10T10:05:06Z"},"query":{"pages":{"317966":{"pageid":317966,"title":"File:Commons-logo.svg","imageinfo":[{"url":"https://upload.wikimedia.org/wikipedia/commons/4/4a/Commons-logo.svg"}]}}}}"""

        self.monolingual_extend_mock_data = """{"entities":{"M3630407": {"statements":{"P9533":[{"mainsnak":{"datavalue": {"value": {"text": "Idiot","language": "de"},"type": "monolingualtext"}}}]}}}}"""
        self.wd_monolingual_extend_mock_data = """{"entities":{"P9533":{"type": "property","datatype": "monolingualtext","id":"P9533","labels":{"en": {"language": "en","value": "audio transcription"}}}}}"""
        self.exted_monolingual_text_result = """{"meta":[{"id":"P9533","name":"audio transcription"}],"rows":{"M3630407":{"P9533":[{"str": "Idiot [de]"}]}}}"""
        self.mono_lingual_query_extend_data = {"ids": ["M3630407"], "properties": [{"id": "P9533"}]}

        self.extend_data_for_quantity = {"ids": ["M83698127"], "properties": [{"id": "P6790"}]}
        self.quantity_extend_mock_data = """{"entities":{"M83698127": {"statements":{"P6790":[{"mainsnak":{"datavalue":{"value": {"amount": "+1.9"},"type": "quantity"}}}]}}}}"""
        self.quantity_wd_mock_data = """{"entities":{"P6790":{"type":"property","datatype":"quantity","id":"P6790","labels":{"en":{"language":"en","value":"f-number"}}}},"success":1}"""
        self.exted_quantity_result = """{"meta":[{"id": "P6790", "name": "f-number"}],"rows":{"M83698127":{"P6790":[{"str": "+1.9"}]}}}"""

        self.entity_suggest_mock_data = """{"query":{"searchinfo": {"totalhits": 124800},"search":[{"title":"File:Parboiled rice with chicken, peppers, cucurbita, peas and tomato.jpg","pageid": 60008323}]}}"""
        self.entity_suggest_sample_result = """{"result":[{"id":"M60008323","name": "File:Parboiled rice with chicken, peppers, cucurbita, peas and tomato.jpg"}]}"""

        self.media_preview_mock_data = """{"query": {"pages": {"317966": {"title": "File:Commons-logo.svg","imageinfo": [{"size": 932,"width": 1024,"height": 1376,"url": "https://upload.wikimedia.org/wikipedia/commons/4/4a/Commons-logo.svg"}]}}}}"""
        self.sample_media_preview_result = """<div width='1024' height='100px' style='position: fixed; overflow:hidden; width:400px'> <span style='float: left'><img style='padding-right: 5px' src=https://upload.wikimedia.org/wikipedia/commons/4/4a/Commons-logo.svg width=100                 height=50 style='float: left'></span><span style='float: left; margin-top: -10px'><p style='color: #11c; font-weight: bold; position: fixed; font-size: 10px; font-family: Arial, sans-serif'>File:Commons-logo.svg </p></span><span style='float: left; margin-top:20px'><p style='font-size: 10px;'>1024 x 1376; 932.0 B</p></span></div>"""

        self.media_preview_audio_file_mock_data = """{"query": {"pages": {"112471826": {"title": "File:LL-Q105(lns)-Mndetatsin-mónlè(Lundi).wav","imageinfo": [{"size": 212016,"width": 0,"height": 0,"url": "https://upload.wikimedia.org/wikipedia/commons/0/03/LL-Q105%28lns%29-Mndetatsin-m%C3%B3nl%C3%A8%28Lundi%29.wav"}]}}}}"""
        self.sample_media_audio_preview_result = """<div width='1024' height='100px' style='position: fixed; overflow:hidden; width:400px'> <span style='float: left'><audio style='width: 175px; height:30px' controls><source src=https://upload.wikimedia.org/wikipedia/commons/0/03/LL-Q105%28lns%29-Mndetatsin-m%C3%B3nl%C3%A8%28Lundi%29.wav type='audio/wav'></span><span style='float: left; margin-top: -5px; margin-left: 5px'><p style=' color: #11c; font-weight: bold; position: fixed; font-size: 10px; font-family: Arial, sans-serif'>File:LL-Q105(lns)-Mndetatsin-mónlè(Lundi).wav </p></span><span style='float: left; margin-top:10px; margin-left: 5px'><p style='font-size: 10px;'>207.05 KB</p></span></div>"""

        self.media_preview_video_file_mock_data = """{"query": {"pages": {"5762062": {"title": "File:Aljazeeraasset-WarOnGazaDay18793.ogv","imageinfo": [{"size": 84801115,"width": 720,"height": 576,"url": "https://upload.wikimedia.org/wikipedia/commons/f/f1/Aljazeeraasset-WarOnGazaDay18793.ogv"}]}}}}"""
        self.sample_media_video_preview_result = """<div width='1024' height='100px' style='position: fixed; overflow:hidden; width:400px'> <span style='float: left'><video style='width: 200px; height:60px' controls><source src=https://upload.wikimedia.org/wikipedia/commons/f/f1/Aljazeeraasset-WarOnGazaDay18793.ogv type='video/ogv'></span><span style='float: left; margin-top: -5px; margin-left: 10px'><p style=' color: #11c; font-weight: bold; position: fixed; font-size: 10px; font-family: Arial, sans-serif'>File:Aljazeeraasset-WarOnGazaDay18793.ogv </p></span><span style='float: left; margin-top:10px; margin-left: 10px'><p style='font-size: 10px;'>80.87 MB</p></span></div>"""
        self.properties_suggest_result = """{"properties": [{"id": "wikitext","name": "Wikitext"},{"id": "P180","name": "depicts"},{"id": "P6243","name": "digital representation of"},{"id": "P921","name": "main subject"},{"id": "P170","name": "creator"},{"id": "P571","name": "inception"},{"id": "P1071","name": "location of creation"},{"id": "P195","name": "collection"},{"id": "P7482","name": "source of file"},{"id": "P6216","name": "copyright status"},{"id": "P275","name": "copyright license"},{"id": "P1259","name": "coordinates of the point of view"}],"type": "mediafile"}"""
        self.properties_suggest_mock_data = """{"entities": {"P180": {"type": "property", "datatype": "wikibase-item", "id": "P180", "labels": {"en": {"language": "en", "value": "depicts"}}}, "P6243": {"type": "property", "datatype": "wikibase-item", "id": "P6243", "labels": {"en": {"language": "en", "value": "digital representation of"}}}, "P921": {"type": "property", "datatype": "wikibase-item", "id": "P921", "labels": {"en": {"language": "en", "value": "main subject"}}}, "P170": {"type": "property", "datatype": "wikibase-item", "id": "P170", "labels": {"en": {"language": "en", "value": "creator"}}}, "P571": {"type": "property", "datatype": "time", "id": "P571", "labels": {"en": {"language": "en", "value": "inception"}}}, "P1071": {"type": "property", "datatype": "wikibase-item", "id": "P1071", "labels": {"en": {"language": "en", "value": "location of creation"}}}, "P195": {"type": "property", "datatype": "wikibase-item", "id": "P195", "labels": {"en": {"language": "en", "value": "collection"}}}, "P7482": {"type": "property", "datatype": "wikibase-item", "id": "P7482", "labels": {"en": {"language": "en", "value": "source of file"}}}, "P6216": {"type": "property", "datatype": "wikibase-item", "id": "P6216", "labels": {"en": {"language": "en", "value": "copyright status"}}}, "P275": {"type": "property", "datatype": "wikibase-item", "id": "P275", "labels": {"en": {"language": "en", "value": "copyright license"}}}, "P1259": {"type": "property", "datatype": "globe-coordinate", "id": "P1259", "labels": {"en": {"language": "en", "value": "coordinates of the point of view"}}}}, "success": 1}"""

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


    def test_extend_for_captions(self):
        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=query&pageids=86236603&format=json",
                  text=self.sample_caption_file_info)
            m.get("https://commons.wikimedia.org/w/api.php?action=wbgetentities&format=json&sites=commonswiki&ids=M86236603",
                  text=self.sample_commons_captions_data)
            m.get("https://commons.wikimedia.org/w/api.php?action=wbgetentities&format=json&languages=en&ids=M86236603",
                  text=self.sample_commons_captions_data)

            response = self.app.get('/en/api?extend={}'.format(json.dumps(self.extend_caption_data)), follow_redirects=True)
            response_data = json.loads(response.data.decode('utf8'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_data['meta'], json.loads(self.caption_extend_data_result)['meta'])
            self.assertEqual(response_data['rows'], json.loads(self.caption_extend_data_result)['rows'])


    def test_get_entity_suggest(self):
        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=food&srnamespace=6&srlimit=10&format=json",
                  text=self.entity_suggest_mock_data)
            response = self.app.get('/en/api/suggest?prefix=food', follow_redirects=True)
            response_data = json.loads(response.data.decode('utf8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["result"][0]["id"], json.loads(self.entity_suggest_sample_result)["result"][0]["id"])
        self.assertEqual(response_data["result"][0]["name"], json.loads(self.entity_suggest_sample_result)["result"][0]["name"])


    def test_preview_media_file_image(self):
        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=query&pageids=317966&format=json&prop=imageinfo&iiprop=url%7Csize",
                  text=self.media_preview_mock_data)

            response = self.app.get("/en/api/preview?id=M317966", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode("utf-8") , self.sample_media_preview_result)


    def test_preview_media_file_audio(self):
        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=query&pageids=112471826&format=json&prop=imageinfo&iiprop=url%7Csize",
                  text=self.media_preview_audio_file_mock_data)

            response = self.app.get("/en/api/preview?id=M112471826", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode("utf-8") , self.sample_media_audio_preview_result)


    def test_preview_media_file_video(self):
        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=query&pageids=5762062&format=json&prop=imageinfo&iiprop=url%7Csize",
                  text=self.media_preview_video_file_mock_data)

            response = self.app.get("/en/api/preview?id=M5762062", follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode("utf-8") , self.sample_media_video_preview_result)


    def test_suggest_properties(self):
        with requests_mock.Mocker() as m:
            m.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&languages=en&props=labels&ids=P180|P6243|P921|P170|P571|P1071|P195|P7482|P6216|P275|P1259",
                  text=self.properties_suggest_mock_data)
            response = self.app.get('en/api/properties?type=', follow_redirects=True)
            response_data = json.loads(response.data.decode('utf8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, json.loads(self.properties_suggest_result))


if __name__ == '__main__':
    unittest.main()
