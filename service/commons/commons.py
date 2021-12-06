#!/usr/bin/env python3

# Authors: Eugene Egbe
# Functions which interract with Wikimedia Commons


import requests

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


def get_image_info_from_id(image_id):
    """ Query a commons image using id

        Parameters:
            id (str): Fueries file names

        Returns:
            file_name (str): Commons file name with id=image_id
    """

    PARAMS = {
        "action": "query",
        "pageids": image_id,
        "format": "json"
    }

    file_info = make_api_request(app.config["API_URL"], PARAMS)
    return file_info["query"]["pages"][image_id]["title"]



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
