#!/usr/bin/env python3

# Authors: Eugene Egbe
# Functions which interract with Wikidata


from service import app
from service.commons import commons
from service.reconcile import processresults


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

    data = commons.make_api_request(app.config["WD_API_URL"], PARAMS)

    return data


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

        entityies_data = commons.make_api_request(app.config["WD_API_URL"], PARAMS)
        return entityies_data["entities"]
    else:
        return None


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

    wd_search_results = commons.make_api_request(app.config['WD_API_URL'], PARAMS)
    suggest_result_data = processresults.build_suggest_result(suggest_prefix, wd_search_results['search'])

    return suggest_result_data
