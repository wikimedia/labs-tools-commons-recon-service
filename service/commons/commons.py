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
        return None
    else:
        return data


def get_media_info_from_id(media_id):
    """ Query a commons image using id

        Parameters:
            id (str): Fueries file names

        Returns:
            file_name (str): Commons file name with id=media_id
    """

    PARAMS = {
        "action": "query",
        "pageids": media_id,
        "format": "json"
    }

    file_info = make_api_request(app.config["API_URL"], PARAMS)
    if "query" in file_info.keys() and "title" in file_info["query"]["pages"][media_id].keys():
        return file_info["query"]["pages"][media_id]["title"]
    else:
        return None


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


def get_page_wikitext(media_id):
    """ Fetch wikitext for a commons image.

        Parameters:
            media_id (str): ID of the commons image.

        Returns:
            wikitext (str): Wikitext of the requested page.
    """

    PARAMS = {
        "action": "parse",
        "format": "json",
        "prop": "wikitext",
        "language": "en",
        "pageid": media_id.split("M")[1]
    }

    page_data = make_api_request(app.config["API_URL"], PARAMS)
    return page_data["parse"]["wikitext"]["*"]


def get_media_preview_data(media_id):
    """Get the url of a Commons media file

    Args:
        media_id (str): ID of the media file

    Returns:
        url, title (str): strings of media file url and the media title
    """
    media_id = media_id.split("M")[1]
    PARAMS = {
        "action": "query",
        "pageids": media_id,
        "format": "json",
        "prop": "imageinfo",
        "iiprop": "url|size"
    }
    preview_data = {}
    media_data = make_api_request(app.config["API_URL"], PARAMS)

    if "query" in media_data.keys() and media_id in media_data["query"]["pages"].keys():
        preview_data["title"] = media_data["query"]["pages"][media_id]["title"]
        preview_data["url"] = media_data["query"]["pages"][media_id]["imageinfo"][0]["url"]
        preview_data["width"] = str(media_data["query"]["pages"][media_id]["imageinfo"][0]["width"])
        preview_data["height"] = str(media_data["query"]["pages"][media_id]["imageinfo"][0]["height"])
        preview_data["size"] = media_data["query"]["pages"][media_id]["imageinfo"][0]["size"]
        return preview_data
    else:
        return "", "File not Found"


def get_commons_file_captions(image_id):
    """Get file captions for a commons file with id:imageid

    Args:
        image_id (str): Image id of the file

    Returns:
        Obj: A dictionary of Captions(labels) in different languages
    """

    PARAMS = {
        "action": "wbgetentities",
        "format": "json",
        "sites": "commonswiki",
        "ids": image_id
    }
    page_data = make_api_request(app.config["API_URL"], PARAMS)
    return page_data["entities"][str(image_id)]["labels"]
