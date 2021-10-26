#!/usr/bin/env python3

# Authors: Eugene Egbe
# Utility functions for api blueprint

import sys
import requests
import json
from service import app


def make_api_request(url, PARAMS):
    """ Makes request to an end point to get data

        Parameters:
            url (str): The Api url end point
            PARAMS (obj): The parameters to be used as arguments

        Returns:
            data (obj): Json object of the recieved data.
    """

    S = requests.Session()
    r = S.get(url=url, params=PARAMS)
    data = r.json()

    if data is None:
        return {}
    else:
        return data


def extract_file_names(query_data):
    """ Extract file name from the queries data.

        Parameters:
            query_data (obj): The queries data object.

        Returns:
            query_string (str): A concatenated string of file names.
    """

    return "|".join(entry["query"] for entry in query_data.values())


def make_commons_search(query_string):
    """ Makes request to commons API to get images info

        Parameters:
            query_string (str): The concatenated file names.

        Returns:
            pages (obj): Json object of image inforamtion.
    """

    PARAMS = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "titles": query_string
    }

    data = make_api_request(app.config["API_URL"], PARAMS)
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

    result_object["id"] = "M" + str(page["pageid"])
    result_object["name"] = page["title"]
    result_object["score"] = 100
    result_object["match"] = True

    result_array.append(result_object)
    query_result_object["result"] = result_array

    return query_result_object


def build_query_results(query_data, results):
    """ Builds result using image search results.

        Parameters:
            query_data (obj): Query data from api request.
            results (obj): Results from image search from wmc api.

        Returns:
            overall_query_object (obj): Reconciliation api result for queries.
    """

    overall_query_object = {}

    query_labels = list(query_data.keys())
    query_values = [value["query"] for value in query_data.values()]
    result_values = list(results.values())

    for i in range(0, len(result_values)):

        if "pageid" in result_values[i]:

            # Files are sorted by commons api so we find the results index in query data
            element_index_in_results = query_values.index(result_values[i]["title"])
            overall_query_object[query_labels[element_index_in_results]] = build_query_result_object(result_values[i])

        else:
            overall_query_object[query_labels[i]] = {"result": []}

    return overall_query_object


def make_wd_properties_request(wd_properties_list, lang):
    """ Makes request to Wikidata to get properties.

        Parameters:
            wd_properties_list (list): list of properties.

        Returns:
            data (obj): Entities which represent the properties.
    """

    PARAMS = {
        "action": "wbgetentities",
        "format": "json",
        "languages": lang,
        "props": "labels",
        "ids": "|".join(id for id in wd_properties_list)
    }

    data = make_api_request(app.config["WD_API_URL"], PARAMS)

    return data



def build_extend_meta_info(properties, lang):
    """ Build meta info for data extension object.

        Parameters:
            properties (list): list of properties provided in extend data.
            lang (str): Language of the request api.

        Returns:
            meta (obj): meta info for data extension result.
    """

    meta = {}
    meta = []

    wd_request_properties = []
    for prop in properties:

        # We wont check Wikidata for this property
        if prop["id"] == "wikitext":
            wikitext_boject = {}
            wikitext_boject["id"] = "wikitext"
            wikitext_boject["name"] = "Wikitext"
            meta.append(wikitext_boject)

        # case for Wikidata properties we will look for
        else:

            # Add the property to a list for one request with all props
            wd_request_properties.append(prop["id"])

    wd_properties_data = make_wd_properties_request(wd_request_properties, lang)["entities"]

    for prop in properties:
        if prop["id"] in wd_properties_data.keys():
            property_object = {}
            property_object["id"] = prop["id"]
            property_object["name"] = wd_properties_data[prop["id"]]["labels"][lang]["value"]
            meta.append(property_object)
    return meta


def get_page_wikitext(image_id):
    """ Fetch wikitext for a commons image.

        Parameters:
            image_id (str): ID of the commons image.

        Returns:
            wikitext (str): Wikitext of the requested page.
    """

    PARAMS = {
        "action": "parse",
        "format": "json",
        "prop": "wikitext",
        "language": "en",
        "pageid": image_id.split("M")[1]
    }

    page_data = make_api_request(app.config["API_URL"], PARAMS)

    return page_data["parse"]["wikitext"]["*"]


def get_wikidata_entity_label(wd_ids, lang):
    """ Fetch the lable of a Wikidata entity.

        Parameters:
            wd_id (str): WD id of the entity.
            lang (str): language of the label.

        Returns:
            label (str): label of wikidata item with ID wd_id.
    """

    PARAMS = {
        "action": "wbgetentities",
        "format": "json",
        "props": "labels",
        "languages": lang,
        "ids": "|".join(id for id in wd_ids)
    }

    if len(wd_ids) != 0:
    
        entityies_data = make_api_request(app.config["WD_API_URL"], PARAMS)
        return entityies_data["entities"]
    else:
        return None


def build_row_data(row_object, extend_ids):
    """ Add image ids to rows object of extend result.

        Parameters:
            row_object (obj): Row object of data extension result.
            extend_ids (list): List of image ids.

        Returns:
            None
    """

    for image_id in extend_ids:
        row_object[image_id] = {}


def build_dataset_values(claim_object, data_value):
    """ Build results with different datasets.

        Parameters:
            claim_object (obj): Onject to modify and add to rows .
            data_value (obj): result object
        Returns:
            Modified claim_boject according to data_value.type
    """

    if data_value["type"] == "globecoordinate":
        claim_object["str"] = str(data_value["value"]["latitude"]) + "," + str(data_value["value"]["longitude"])

    elif data_value["type"] == "time":
        claim_object["date"] = data_value["value"]["time"].split("T")[0].split("+")[1]

    elif data_value["type"] == "string":
        claim_object["str"] = data_value["value"]
    else:
        pass

    return claim_object


def build_extend_rows_info(extend_ids, extend_properties, lang):
    """ Build extend object of the data extension result.

        Parameters:
            extend_ids (obj): List of image ids.
            extend_properties (obj): Properties to be checked.
            lang (str): Language of the result set.

        Returns:
            rows (obj): Row information for the data extension results.
    """
    # Make an api request with the list of ids to get metadata properties

    rows_data = {}
    rows_data["rows"] = {}
    wd_items_list = []

    PARAMS = {
        "action": "wbgetentities",
        "format": "json",
        "languages": lang,
        "ids": "|".join(id for id in extend_ids)
    }

    properties = make_api_request(app.config["API_URL"], PARAMS)

    extend_entities = properties["entities"]

    # Adjust rows object by already adding
    build_row_data(rows_data["rows"], extend_ids)

    # For each of the rows in the above data frame build the content
    for row_data in rows_data["rows"]:
        for prop in extend_properties:

            if prop["id"] == "wikitext":
                rows_data["rows"][row_data]["wikitext"] = []
                rows_data["rows"][row_data]["wikitext"].append(get_page_wikitext(row_data))

            else:
                # Holds entry object for properties of an image
                rows_data["rows"][row_data][prop["id"]] = []

                # Check if property has been added to Commons image
                if prop["id"] not in extend_entities[row_data]["statements"].keys():
                    pass

                else:
                    # Iterate every statement in the claim and get the valus
                    for statement in extend_entities[row_data]["statements"][prop["id"]]:

                        # we check for statements which do not have same dataset
                        if statement["mainsnak"]["datavalue"]["type"] == "wikibase-entityid":
                            wd_items_list.append(statement["mainsnak"]["datavalue"]["value"]["id"])

                        else:
                            wd_claim_object = {}
                            data_value = statement["mainsnak"]["datavalue"]
                            wd_claim_object = build_dataset_values({}, data_value)
                            rows_data["rows"][row_data][prop["id"]].append(wd_claim_object)

                # Make call to Wd to get the entitis info
                wd_items_and_labels = get_wikidata_entity_label(wd_items_list, lang)
                if wd_items_and_labels is not None:
                    for item_id in wd_items_list:
                        wd_claim_object = {}
                        wd_claim_object["id"] = wd_items_and_labels[item_id]["id"]
                        wd_claim_object["name"] = wd_items_and_labels[item_id]["labels"][lang]["value"]
                        rows_data["rows"][row_data][prop["id"]].append(wd_claim_object)

    return rows_data["rows"]


def build_extend_result(extend_data, lang):
    """ Combine meta and rows data to make data extension results.

        Parameters:
            extend_data (obj): Data in extension request.
            lang (str): Language of api request.

        Returns:
            extend_results (obj): Result for the data extension request.
    """
    extend_results = {}

    if extend_data:
        extend_ids = extend_data["ids"]
        extend_properties = extend_data["properties"]

        meta_info = build_extend_meta_info(extend_properties, lang)
        rows_data = build_extend_rows_info(extend_ids, extend_properties, lang)

        extend_results["meta"] = meta_info
        extend_results["rows"] = rows_data

        return extend_results
    else:
        return {}


def build_suggest_result(prefix, wd_search_results):
    """ Build extend result set.

        Parameters:
            prefix (str): suggest prefix entery.
            wd_search_results (obj): Search result from Wikidata.

        Returns:
            extend_results (obj): Result for the data extension request.
    """

    suggest_result_data = {}
    suggest_result_data["result"] = []
    if "wikitext" in prefix.lower() or prefix.lower() in "wikitext":
        result_item = {}
        result_item["id"] = "wikitext"
        result_item["name"] = "Wikitext"
        result_item["description"] = "Text associated with the file, in wiki markup"

        # Criteria to get "notable" will be determined later
        suggest_result_data["result"].append(result_item)

    if wd_search_results is not None:
        for result in wd_search_results:
            result_item = {}
            result_item["id"] = result["id"]
            result_item["name"] = result["label"]
            result_item["description"] = result["description"]

            # Criteria to get notables will be determined later
            suggest_result_data["result"].append(result_item)

    return suggest_result_data


def make_suggest_request(suggest_prefix, lang):
    """ Make request to Wikidata for property suggestions.

        Parameters:
            suggest_prefix (str): suggest prefix entery.
            lang (obj): Language for the search.

        Returns:
            extend_results (obj): Result for the data extension request.
    """

    PARAMS = {
        "action": "wbsearchentities",
        "format": "json",
        "language": lang,
        "type": "property",
        "search": suggest_prefix
    }

    wd_search_results = make_api_request(app.config['WD_API_URL'], PARAMS)
    suggest_result_data = build_suggest_result(suggest_prefix, wd_search_results['search'])

    return suggest_result_data


def get_suggest_result(suggest_prefix, lang):
    """ Get suggest result data.

        Parameters:
            suggest_data (obj): suggest request object.
            lang (str): Request language.

        Returns:
            wd_search_result (obj): Suggest result data.
    """
    wd_search_result = make_suggest_request(suggest_prefix, lang)

    return wd_search_result
