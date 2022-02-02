
from service import app
from service.commons import commons


def get_property_suggest_results(lang):
    """Get property suggest results

    Args:
        lang (str): Language to return the property labels

    Returns:
        obj: Object of suggested properties
    """


    prop_keys = app.config.get('properties', None)

    suggest_properties = {
        "type": "mediafile"
    }
    suggest_properties["properties"] = []
    valid_wd_prop_ids = []
    for key in prop_keys:
        if key == "wikitext":
            suggest_properties["properties"].append({"id": "wikitext", "name": "Wikitext"})
        else:
            valid_wd_prop_ids.append(key)

    PARAMS = {
        "action": "wbgetentities",
        "format": "json",
        "languages": lang,
        "props": "labels",
        "ids": "|".join(id for id in valid_wd_prop_ids)
    }

    data = commons.make_api_request(app.config["WD_API_URL"], PARAMS)
    if "entities" in data.keys():
        for prop in valid_wd_prop_ids:
            prop_entry = {}
            prop_entry["id"] = prop
            prop_entry["name"] = data["entities"][prop]["labels"][lang]["value"]
            suggest_properties["properties"].append(prop_entry)
    return suggest_properties
