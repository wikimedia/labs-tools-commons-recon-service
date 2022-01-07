# !/usr/bin/env python3
# Authors: Eugene Egbe
# Process reconciliation query results


import re
from service import app
from service.commons import commons
from service.wikidata import wikidata
from service.reconcile import handlefile


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
    query_values = [handlefile.check_query_file_type(value["query"]) for value in query_data.values()]

    result_values = list(results.values())

    for i in range(0, len(result_values)):

        best_match_file = handlefile.find_best_match_file(query_values, result_values[i]["title"])
        element_index_in_results = query_values.index(best_match_file)

        if "pageid" in result_values[i]:

            # Files are sorted by commons api so we find the results index in query data\
            # we look for index of best_match string
            # In case where no file in our queries matches the result we return an empty set

            overall_query_object[query_labels[element_index_in_results]] = build_query_result_object(result_values[i])

        else:
            overall_query_object[query_labels[element_index_in_results]] = {"result": []}

    return overall_query_object


def build_extend_meta_info(properties, lang):
    """ Build meta info for data extension object.

        Parameters:
            properties (list): list of properties provided in extend data.
            lang (str): Language of the request api.

        Returns:
            meta (obj): meta info for data extension result.
    """

    wd_prop_check = False

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

        elif prop["id"].startswith("C"):
            caption_object = {}
            caption_object["id"] = prop["id"]
            caption_object["name"] = "Caption [" + prop["id"].split("C")[1] + "]"

            meta.append(caption_object)

        # case for Wikidata properties we will look for
        else:

            # Add the property to a list for one request with all props
            wd_request_properties.append(prop["id"])
            # Check for wikidata properties to make request

            wd_prop_check = True
    # If there was a WD property added then make request
    if wd_prop_check:
        wd_prop_request_data = wikidata.make_wd_properties_request(wd_request_properties, lang)
        if "entities" in wd_prop_request_data.keys():
            wd_properties_data = wd_prop_request_data["entities"]

            for prop in properties:
                if prop["id"] in wd_properties_data.keys():
                    property_object = {}
                    property_object["id"] = prop["id"]
                    property_object["name"] = wd_properties_data[prop["id"]]["labels"][lang]["value"]
                    meta.append(property_object)

    return meta


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
    captions_langs = []

    PARAMS = {
        "action": "wbgetentities",
        "format": "json",
        "languages": lang,
        "ids": "|".join(id for id in extend_ids)
    }

    properties = commons.make_api_request(app.config["API_URL"], PARAMS)

    if "entities" in properties.keys():
        extend_entities = properties["entities"]

    # Adjust rows object by already adding
    build_row_data(rows_data["rows"], extend_ids)

    # For each of the rows in the above data frame build the content
    for row_data in rows_data["rows"]:
        for prop in extend_properties:

            if prop["id"] == "wikitext":
                rows_data["rows"][row_data]["wikitext"] = []
                rows_data["rows"][row_data]["wikitext"].append({"str": commons.get_page_wikitext(row_data)})

            elif prop["id"].startswith("C"):
                captions_langs.append(prop["id"].split("C")[1])

                rows_data["rows"][row_data] = {}
                wmc_caption_data = commons.get_commons_file_captions(extend_ids[0])
                wmc_caption_data_keys = list(wmc_caption_data.keys())
                for lang_key in wmc_caption_data_keys:
                    if lang_key in captions_langs:
                        rows_data["rows"][row_data]["C" + lang_key] = []
                        caption_object = {}
                        caption_object['str'] = wmc_caption_data[lang_key]["value"]
                        rows_data["rows"][row_data]["C" + lang_key].append(caption_object)
            else:
                wd_items_list = []

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

                        elif statement["mainsnak"]["datavalue"]["type"] == "monolingualtext":
                            text = statement["mainsnak"]["datavalue"]["value"]['text']
                            text_lang = statement["mainsnak"]["datavalue"]["value"]["language"]
                            rows_data["rows"][row_data][prop["id"]] = []
                            rows_data["rows"][row_data][prop["id"]].append({"str": text + " [" + text_lang + "]"})

                        elif statement["mainsnak"]["datavalue"]["type"] == "quantity":
                            amount = statement["mainsnak"]["datavalue"]["value"]["amount"]
                            rows_data["rows"][row_data][prop["id"]] = []
                            rows_data["rows"][row_data][prop["id"]].append({"str": amount})

                        else:
                            wd_claim_object = {}
                            data_value = statement["mainsnak"]["datavalue"]
                            wd_claim_object = build_dataset_values({}, data_value)
                            rows_data["rows"][row_data][prop["id"]].append(wd_claim_object)

                # Make call to Wd to get the entitis info
                wd_items_and_labels = wikidata.get_wikidata_entity_label(wd_items_list, lang)
                if wd_items_and_labels is not None:
                    for item_id in wd_items_list:
                        wd_claim_object = {}
                        wd_claim_object["id"] = wd_items_and_labels[item_id]["id"]
                        wd_claim_object["name"] = wd_items_and_labels[item_id]["labels"][lang]["value"]
                        rows_data["rows"][row_data][prop["id"]].append(wd_claim_object)

    return rows_data["rows"]


def normalize_extend_ids(extend_ids):
    """ Get extend id from the string provided

        Parameters:
            extend_ids (obj): List of extend ids.

        Returns:
            normalized_ids (obj): Processed list of ids .
    """
    normalized_ids = []
    for id in extend_ids:
        if "http" in id:
            id = id.split("/")[-1]
            normalized_ids.append(id)
        else:
            normalized_ids.append(id)
    return normalized_ids


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
        normalized_ids = normalize_extend_ids(extend_ids)
        extend_properties = extend_data["properties"]

        meta_info = build_extend_meta_info(extend_properties, lang)
        rows_data = build_extend_rows_info(normalized_ids, extend_properties, lang)

        extend_results["meta"] = meta_info
        extend_results["rows"] = rows_data

        return extend_results
    else:
        return {}


def build_suggest_result(prefix, lang, wd_search_results):
    """ Build extend result set.

        Parameters:
            prefix (str): suggest prefix entery.
            wd_search_results (obj): Search result from Wikidata.

        Returns:
            extend_results (obj): Result for the data extension request.
    """

    suggest_result_data = {}
    suggest_result_data["result"] = []

    if prefix.startswith("C") or prefix.startswith("c") and len(prefix) > 1:
        caption_lang = prefix[1:]
        if bool(re.match("[a-zA-Z0-9-]", caption_lang)):
            result_item = {}
            result_item["id"] = "C" + caption_lang
            result_item["name"] = "Caption [" + caption_lang + "]"
            result_item["description"] = "Image Captions"
            suggest_result_data["result"].append(result_item)

    if "wikitext" in prefix.lower() or prefix.lower() in "wikitext":
        result_item = {}
        result_item["id"] = "wikitext"
        result_item["name"] = "Wikitext"
        result_item["description"] = "Text associated with the file, in wiki markup"

        # Criteria to get "notable" will be determined later
        suggest_result_data["result"].append(result_item)


    elif wd_search_results is not None:
        for result in wd_search_results:
            result_item = {}
            result_item["id"] = result["id"]
            result_item["name"] = result["label"]
            result_item["description"] = result["description"]

            # Criteria to get notables will be determined later
            suggest_result_data["result"].append(result_item)

    return suggest_result_data


def get_suggest_result(suggest_prefix, lang):
    """ Get suggest result data.

        Parameters:
            suggest_data (obj): suggest request object.
            lang (str): Request language.

        Returns:
            wd_search_result (obj): Suggest result data.
    """
    wd_search_result = wikidata.make_suggest_request(suggest_prefix, lang)

    return wd_search_result
