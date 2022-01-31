#!/usr/bin/env python3

# Author: Eugene Egbe
# Unit tests for the api utility functions in the reconciliation service


from sys import prefix
import unittest
from unittest import result
import requests_mock
import json

from service import app
from service.commons.commons import make_api_request, get_page_wikitext, get_media_preview_url
from service.reconcile import handlefile
from service.reconcile import processresults


class TestApiUtils(unittest.TestCase):
    """Test utility functions in the api blueprint."""

    def setUp(self):

        self.fake_arbitrary_data = """
        {"file": "SomeFIle.png"}
        """

        self.file_not_found = {
            "q0": {
                "query": "File:Filenot_found_query.jpg"
            }
        }
        self.fake_page_not_found = {
            "-1": {
                "ns": 6,
                "title": "File:Filenot found query.jpg",
                "missing": "",
                "imagerepository": ""
            }
        }

        self.fake_page_not_found_result = {
            "q0": {
                "result": []
            }
        }

        self.fake_query = {
            "q0": {
                "query": "File:Commons-logo.svg"
            }
        }

        self.fake_page = {
            "317966": {
                "pageid": 317966,
                "ns": 6,
                "title": "File:Commons-logo.svg",
                "imagerepository": "local",
                "imageinfo": [
                    {
                        "timestamp": "2014-06-03T13:43:45Z",
                        "user": "Steinsplitter"
                    }
                ]
            }
        }

        self.query_string = handlefile.extract_file_names(self.fake_query)

        self.fake_queries = {
            "q0": {
                "query": "File:Commons-logo.svg"
            },
            "q1": {
                "query": "File:Hudson Commons (95051).jpg"
            }
        }

        self.fake_query_result_object = {
            "result": [
                {
                    "id": "M317966",
                    "name": "File:Commons-logo.svg",
                    "score": 100,
                    "match": True
                }
            ]
        }

        self.fake_pages = {
            "317966": {
                "pageid": 317966,
                "ns": 6,
                "title": "File:Commons-logo.svg",
                "imagerepository": "local",
                "imageinfo": [
                    {
                        "timestamp": "2014-06-03T13:43:45Z",
                        "user": "Steinsplitter"
                    }
                ]
            },
            "83241361": {
                "pageid": 83241361,
                "ns": 6,
                "title": "File:Hudson Commons (95051).jpg",
                "imagerepository": "local",
                "imageinfo": [
                    {
                        "timestamp": "2019-10-21T00:01:07Z",
                        "user": "Rhododendrites"
                    }
                ]
            }
        }
        self.fake_result = {
            "q0": {
                "result": [
                    {
                        "id": "M317966",
                        "name": "File:Commons-logo.svg",
                        "score": 100,
                        "match": True
                    }
                ]
            }
        }
        self.fake_results = {
            "q0": {
                "result": [
                    {
                        "id": "M317966",
                        "name": "File:Commons-logo.svg",
                        "score": 100,
                        "match": True
                    }
                ]
            },
            "q1": {
                "result": [
                    {
                        "id": "M83241361",
                        "name": "File:Hudson Commons (95051).jpg",
                        "score": 100,
                        "match": True
                    }
                ]
            }
        }

        self.sample_arbitrary_url = "https://test.com/path"
        self.sample_arbitrary_params = {"action": "fetch", "file": "file.jpg"}
        self.test_api_request_data = """
        {"fetch":"file.jpg", "data": [{"name":"File"}, {"type": "JPG"}]}
        """
        self.extend_data_result = """
        {"meta":[{"id": "wikitext","name": "Wikitext"},{"id":"P180","name": "depicts"}],"rows":{"M74698470":{"P180":[{"id": "Q192465","name": "Chick Corea"},{"id": "Q453406","name": "Stanley Clarke"}],"wikitext": ["== {{int:filedesc}} =="]},"M83241361":{"P180":[],"wikitext": ["== {{int:filedesc}} =="]}}}
        """
        self.extend_data = """
        {"ids":["M74698470"],"properties": [{"id": "P180"}, {"id": "wikitext"}]}
        """
        self.extend_data_value_test = """{"value": {"time": "+2009-06-23T00:00:00Z"}, "type": "time"}"""
        self.extend_data_string_test = """{"value": "572106", "type": "string"}"""
        self.extend_data_geocordinates_test = """{"value": {"latitude": 54.43941, "longitude": -2.972027}, "type": "globecoordinate"}"""
        self.test_wmc_properties_data = """
        {"entities":{"M74698470":{"pageid":74698470,"ns":6,"title":"File:Chick Corea & Stanley Clarke.jpg","lastrevid":590206738,"modified":"2021-09-10T13:54:13Z","type":"mediainfo","id":"M74698470","labels":{"en":{"language":"en","value":"Chick Corea and Stanley Clarke playing at the San Sebastian Jazz Festival"}},"descriptions":{},"statements":{"P180":[{"mainsnak":{"snaktype":"value","property":"P180","hash":"a83bcd35f5bd70a205d9eabf429841a6a091d973","datavalue":{"value":{"entity-type":"item","numeric-id":192465,"id":"Q192465"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$c598e90e-44b9-6214-64aa-367e4b2415b6","rank":"normal"},{"mainsnak":{"snaktype":"value","property":"P180","hash":"988edf83d80d66fd97714b6c977f5f3097ee194d","datavalue":{"value":{"entity-type":"item","numeric-id":453406,"id":"Q453406"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$209cb38c-4471-7fc6-5a0e-8232ab7a506c","rank":"normal"}],"P571":[{"mainsnak":{"snaktype":"value","property":"P571","hash":"54625c04bd96974fbcc9eaafd896b65789e15321","datavalue":{"value":{"time":"+2014-07-25T00:00:00Z","timezone":0,"before":0,"after":0,"precision":11,"calendarmodel":"http://www.wikidata.org/entity/Q1985727"},"type":"time"}},"type":"statement","id":"M74698470$2CF35829-A88D-4104-98D7-FF3CC91851EC","rank":"normal"}],"P4082":[{"mainsnak":{"snaktype":"value","property":"P4082","hash":"8227ba960548c059dce2c79cb1fa18cceb0d1d11","datavalue":{"value":{"entity-type":"item","numeric-id":64962,"id":"Q64962"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$6F8D50B9-32DE-4CB4-B7EE-99B4E0184B77","rank":"normal"}],"P6216":[{"mainsnak":{"snaktype":"value","property":"P6216","hash":"5570347fdc76d2a80732f51ea10ee4b144a084e0","datavalue":{"value":{"entity-type":"item","numeric-id":50423863,"id":"Q50423863"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$2C4F3C48-03FC-4E21-9C3A-817E4AF0D7DE","rank":"normal"}],"P275":[{"mainsnak":{"snaktype":"value","property":"P275","hash":"ec6e754c5042e13b53376139e505ebd6708745a4","datavalue":{"value":{"entity-type":"item","numeric-id":18199165,"id":"Q18199165"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$80F83CD2-BE41-4352-BEA1-06DB1D5C3A74","rank":"normal"}],"P7482":[{"mainsnak":{"snaktype":"value","property":"P7482","hash":"83568a288a8b8b4714a68e7239d8406833762864","datavalue":{"value":{"entity-type":"item","numeric-id":66458942,"id":"Q66458942"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$D169279B-414F-4A4B-8283-DA8B82DEDCB4","rank":"normal"}],"P170":[{"mainsnak":{"snaktype":"somevalue","property":"P170","hash":"d3550e860f988c6675fff913440993f58f5c40c5"},"type":"statement","qualifiers":{"P3831":[{"snaktype":"value","property":"P3831","hash":"c5e04952fd00011abf931be1b701f93d9e6fa5d7","datavalue":{"value":{"entity-type":"item","numeric-id":33231,"id":"Q33231"},"type":"wikibase-entityid"}}],"P2093":[{"snaktype":"value","property":"P2093","hash":"d0bea75f2e24eb80feb7691e3e105bb0e8721837","datavalue":{"value":"Vidartereyes","type":"string"}}],"P4174":[{"snaktype":"value","property":"P4174","hash":"a4f30c83bf177b57b01d07f9d1b8fd05125fc075","datavalue":{"value":"Vidartereyes","type":"string"}}]},"qualifiers-order":["P3831","P2093","P4174"],"id":"M74698470$1C77D5CE-0C84-416C-B28B-4602B4D0FE7B","rank":"normal"}],"P276":[{"mainsnak":{"snaktype":"value","property":"P276","hash":"86162b532637cb4969378e50c865ad176b64dc9b","datavalue":{"value":{"entity-type":"item","numeric-id":2349872,"id":"Q2349872"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$0082e5e9-415a-97f2-2bd7-16334700e721","rank":"normal"}]}}},"success":1}
        """
        self.wd_entity_label_data_2 = """
        {"entities":{"Q192465":{"type":"item","id":"Q192465","labels":{"en":{"language":"en","value":"Chick Corea"}}},"Q453406":{"type":"item","id":"Q453406","labels":{"en":{"language":"en","value":"Stanley Clarke"}}}}}
        """
        self.commons_wikitext_data = """
        {"parse":{"title":"File:Chick Corea & Stanley Clarke.jpg","pageid":74698470,"wikitext":{"*":"== {{int:filedesc}} =="}}}
        """
        self.extend_rows_info_data = """
        {"M74698470":{"P180": [{"id": "Q192465","name": "Chick Corea"},{"id": "Q453406","name": "Stanley Clarke"}],"wikitext": ["== {{int:filedesc}} =="]}}
        """
        self.test_wmc_properties_data = """
        {"entities":{"M74698470":{"pageid":74698470,"ns":6,"title":"File:Chick Corea & Stanley Clarke.jpg","lastrevid":590206738,"modified":"2021-09-10T13:54:13Z","type":"mediainfo","id":"M74698470","labels":{"en":{"language":"en","value":"Chick Corea and Stanley Clarke playing at the San Sebastian Jazz Festival"}},"descriptions":{},"statements":{"P180":[{"mainsnak":{"snaktype":"value","property":"P180","hash":"a83bcd35f5bd70a205d9eabf429841a6a091d973","datavalue":{"value":{"entity-type":"item","numeric-id":192465,"id":"Q192465"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$c598e90e-44b9-6214-64aa-367e4b2415b6","rank":"normal"},{"mainsnak":{"snaktype":"value","property":"P180","hash":"988edf83d80d66fd97714b6c977f5f3097ee194d","datavalue":{"value":{"entity-type":"item","numeric-id":453406,"id":"Q453406"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$209cb38c-4471-7fc6-5a0e-8232ab7a506c","rank":"normal"}],"P571":[{"mainsnak":{"snaktype":"value","property":"P571","hash":"54625c04bd96974fbcc9eaafd896b65789e15321","datavalue":{"value":{"time":"+2014-07-25T00:00:00Z","timezone":0,"before":0,"after":0,"precision":11,"calendarmodel":"http://www.wikidata.org/entity/Q1985727"},"type":"time"}},"type":"statement","id":"M74698470$2CF35829-A88D-4104-98D7-FF3CC91851EC","rank":"normal"}],"P4082":[{"mainsnak":{"snaktype":"value","property":"P4082","hash":"8227ba960548c059dce2c79cb1fa18cceb0d1d11","datavalue":{"value":{"entity-type":"item","numeric-id":64962,"id":"Q64962"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$6F8D50B9-32DE-4CB4-B7EE-99B4E0184B77","rank":"normal"}],"P6216":[{"mainsnak":{"snaktype":"value","property":"P6216","hash":"5570347fdc76d2a80732f51ea10ee4b144a084e0","datavalue":{"value":{"entity-type":"item","numeric-id":50423863,"id":"Q50423863"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$2C4F3C48-03FC-4E21-9C3A-817E4AF0D7DE","rank":"normal"}],"P275":[{"mainsnak":{"snaktype":"value","property":"P275","hash":"ec6e754c5042e13b53376139e505ebd6708745a4","datavalue":{"value":{"entity-type":"item","numeric-id":18199165,"id":"Q18199165"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$80F83CD2-BE41-4352-BEA1-06DB1D5C3A74","rank":"normal"}],"P7482":[{"mainsnak":{"snaktype":"value","property":"P7482","hash":"83568a288a8b8b4714a68e7239d8406833762864","datavalue":{"value":{"entity-type":"item","numeric-id":66458942,"id":"Q66458942"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$D169279B-414F-4A4B-8283-DA8B82DEDCB4","rank":"normal"}],"P170":[{"mainsnak":{"snaktype":"somevalue","property":"P170","hash":"d3550e860f988c6675fff913440993f58f5c40c5"},"type":"statement","qualifiers":{"P3831":[{"snaktype":"value","property":"P3831","hash":"c5e04952fd00011abf931be1b701f93d9e6fa5d7","datavalue":{"value":{"entity-type":"item","numeric-id":33231,"id":"Q33231"},"type":"wikibase-entityid"}}],"P2093":[{"snaktype":"value","property":"P2093","hash":"d0bea75f2e24eb80feb7691e3e105bb0e8721837","datavalue":{"value":"Vidartereyes","type":"string"}}],"P4174":[{"snaktype":"value","property":"P4174","hash":"a4f30c83bf177b57b01d07f9d1b8fd05125fc075","datavalue":{"value":"Vidartereyes","type":"string"}}]},"qualifiers-order":["P3831","P2093","P4174"],"id":"M74698470$1C77D5CE-0C84-416C-B28B-4602B4D0FE7B","rank":"normal"}],"P276":[{"mainsnak":{"snaktype":"value","property":"P276","hash":"86162b532637cb4969378e50c865ad176b64dc9b","datavalue":{"value":{"entity-type":"item","numeric-id":2349872,"id":"Q2349872"},"type":"wikibase-entityid"}},"type":"statement","id":"M74698470$0082e5e9-415a-97f2-2bd7-16334700e721","rank":"normal"}]}}},"success":1}
        """
        self.test_wd_properties_data = """
        {"entities":{"P180":{"type":"property","datatype":"wikibase-item","id":"P180","labels":{"en":{"language":"en","value":"depicts"}}}},"success":1}
        """
        self.test_lang = "en"
        self.extend_properties = [{"id": "P180"}, {"id": "wikitext"}]
        self.results_for_date_extend = """{"date": "2009-06-23"}"""
        self.results_for_string_extend = """{"str": "572106"}"""
        self.result_for_geocordinates = """{"str": "54.43941,-2.972027"}"""
        self.commons_id_page_query_data = """{"continue":{"iistart":"2014-04-10T10:05:06Z","continue":"||"},"query":{"pages":{"317966":{"pageid":317966,"ns":6,"title":"File:Commons-logo.svg","imagerepository":"local","imageinfo":[{"url":"https://upload.wikimedia.org/wikipedia/commons/4/4a/Commons-logo.svg"}]}}}}"""

        self.entity_suggest_mock_data = """{"query":{"searchinfo": {"totalhits": 124800},"search":[{"title":"File:Parboiled rice with chicken, peppers, cucurbita, peas and tomato.jpg","pageid": 60008323}]}}"""
        self.entity_suggest_sample_result = """{"result":[{"id":"M60008323","name": "File:Parboiled rice with chicken, peppers, cucurbita, peas and tomato.jpg"}]}"""

    def tearDown(self):
        pass


    def test_extract_file_names(self):
        self.assertEqual(self.query_string, "File:Commons-logo.svg")


    def test_build_query_results(self):
        query_result = processresults.build_query_results(self.fake_query, self.fake_page)
        self.assertEqual(query_result, self.fake_result)


    def test_build_query_results_with_many_queries(self):
        fake_build_objects = processresults.build_query_results(self.fake_queries, self.fake_pages)
        self.assertEqual(fake_build_objects, self.fake_results)


    def test_build_query_results_with_file_not_found(self):
        fake_build_object = processresults.build_query_results(self.file_not_found, self.fake_page_not_found)
        self.assertEqual(fake_build_object, self.fake_page_not_found_result)


    def test_build_query_result_object(self):
        query_result = processresults.build_query_result_object(self.fake_page["317966"])
        self.assertEqual(query_result, self.fake_query_result_object)


    def test_make_api_request(self):
        with requests_mock.Mocker() as m:
            m.get("https://test.com/path?action=fetch&file=file.jpg", text=self.test_api_request_data)
            response = make_api_request(self.sample_arbitrary_url, self.sample_arbitrary_params)

        self.assertEqual(response, json.loads(self.test_api_request_data))


    def test_get_page_wikitext(self):
        image_id = "M74698470"
        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=parse&format=json&pageid=74698470&prop=wikitext",
                  text=self.commons_wikitext_data)
            response = get_page_wikitext(image_id)

        self.assertEqual(response, json.loads(self.commons_wikitext_data)["parse"]["wikitext"]["*"])


    def test_build_row_data(self):
        sample_ids = ["M74698470", "M83241361"]
        sample_row_object = {}
        processresults.build_row_data(sample_row_object, sample_ids)

        self.assertEqual(sample_row_object, {"M74698470": {}, "M83241361": {}})


    def test_build_dataset_values_for_date(self):
        self.assertEqual(json.loads(self.results_for_date_extend), processresults.build_dataset_values({}, json.loads(self.extend_data_value_test)))


    def test_build__dataset_values_for_string(self):
        self.assertEqual(json.loads(self.results_for_string_extend), processresults.build_dataset_values({}, json.loads(self.extend_data_string_test)))


    def test_build__dataset_values_for_geocordinates(self):
        self.assertEqual(json.loads(self.result_for_geocordinates), processresults.build_dataset_values({}, json.loads(self.extend_data_geocordinates_test)))


    def test_build_extend_result(self):
        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=wbgetentities&format=json&languages=en&ids=M74698470",
                  text=self.test_wmc_properties_data)
            m.get("https://commons.wikimedia.org/w/api.php?action=parse&format=json&pageid=74698470&prop=wikitext",
                  text=self.commons_wikitext_data)
            m.get("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q192465|Q453406&format=json&languages=en&props=labels",
                  text=self.wd_entity_label_data_2)
            m.get("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=P180&format=json",
                  text=self.test_wd_properties_data)

            extend_result = processresults.build_extend_result(json.loads(self.extend_data), self.test_lang)

        self.assertEqual(extend_result["meta"], json.loads(self.extend_data_result)["meta"])
        self.assertEqual(extend_result["rows"]["M74698470"]["P180"], json.loads(self.extend_data_result)["rows"]["M74698470"]["P180"])


    def test_build_extend_rows_info(self):
        extend_ids = ["M74698470"]

        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=wbgetentities&format=json&languages=en&ids=M74698470",
                  text=self.test_wmc_properties_data)
            m.get("https://commons.wikimedia.org/w/api.php?action=parse&format=json&pageid=74698470&prop=wikitext",
                  text=self.commons_wikitext_data)
            m.get("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q192465|Q453406&format=json&languages=en&props=labels",
                  text=self.wd_entity_label_data_2)

            response = processresults.build_extend_rows_info(extend_ids, self.extend_properties, self.test_lang)

        self.assertEqual(response["M74698470"]["P180"], json.loads(self.extend_rows_info_data)["M74698470"]["P180"])

    def test_find_best_match_for_match(self):
        match_result = handlefile.find_best_match_file(['File:Commons-logo.svg'], "File:Commons-logo.svg")
        self.assertEqual(match_result, "File:Commons-logo.svg")


    def test_find_best_match_for_no_match(self):
        match_result = handlefile.find_best_match_file(['File:Commons-logo.svg'], self.file_not_found["q0"]["query"])
        self.assertEqual(match_result, self.file_not_found["q0"]["query"])


    def test_check_query_file_type_link(self):
        check_result = handlefile.check_query_file_type('https://commons.wikimedia.org/wiki/File:Commons-logo.svg')
        self.assertEqual(check_result, "File:Commons-logo.svg")


    def test_check_query_file_type_without_prefix(self):
        check_result = handlefile.check_query_file_type('Commons-logo.svg')
        self.assertEqual(check_result, "File:Commons-logo.svg")


    def test_check_query_file_type_with_prefix(self):
        check_result = handlefile.check_query_file_type('File:Commons-logo.svg')
        self.assertEqual(check_result, "File:Commons-logo.svg")


    def test_check_query_file_type_with_image_id(self):
        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=query&format=json&pageids=317966",
                  text=self.commons_id_page_query_data)
            response = handlefile.check_query_file_type('https://commons.wikimedia.org/entity/M317966')
        self.assertEqual(response, "File:Commons-logo.svg")


    def test_normalize_extend_ids(self):
        normalized_extends = processresults.normalize_extend_ids(["M83241361", "https://commons.wikimedia.org/entity/M93645431"])
        self.assertEqual(normalized_extends, ["M83241361", "M93645431"])


    def test_get_media_preview_url(self):
        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=query&pageids=317966&format=json&prop=imageinfo&iiprop=url",
                  text=self.commons_id_page_query_data)

            media_url, media_title = get_media_preview_url('M317966')
        self.assertEqual(media_url, "https://upload.wikimedia.org/wikipedia/commons/4/4a/Commons-logo.svg")
        self.assertEqual(media_title, "File:Commons-logo.svg")


    def test_get_entity_suggest_result(self):
        with requests_mock.Mocker() as m:
            m.get("https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=food&srnamespace=6&srlimit=10&format=json",
                  text=self.entity_suggest_mock_data)
            entity_suggest_result = processresults.get_entity_suggest_result('food', self.test_lang)

        self.assertEqual(entity_suggest_result, json.loads(self.entity_suggest_sample_result))


if __name__ == "__main__":
    unittest.main()
