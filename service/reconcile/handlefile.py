# !/usr/bin/env python3
# Authors: Eugene Egbe
# Handle operations on file names of the reconciliation service


from service.commons import commons
from service import app

def check_query_file_type(file_name):
    """ Check file type from query data

        Parameters:
            file_name (str): File name in query data

        Returns:
            file_name (str): Processed file name ready for query
    """

    # handle links
    if 'http' in file_name:
        # case of just file ids given
        if 'entity/' in file_name:

            media_id = file_name.split('entity/M')[1]
            file_name = commons.get_media_info_from_id(media_id)
            return file_name

        else:
            if 'Special:FilePath' in file_name:
                file_name = file_name.split('Special:FilePath/')[1]
            else:
                # split with wiki/ as point
                file_name = file_name.split('wiki/')[1]

    # check for File: in file_name
    if "File:" not in file_name:
        file_name = "File:" + file_name
    
    # We have to capitalize first letter after "File:prefix"
    first_letter = file_name.split(":")[1][0]
    file_name = file_name.replace(first_letter, first_letter.upper(), 1)

    return file_name.replace("_", " ")


def find_best_match_file(query_values, file_name):
    """ Find match in list of files which was provided as queries

        Parameters:
            query_values (lst): Fueries file names
            file_name (str): File returned from commons search

        Returns:
            match (obj): Matched file or original file if not matched
    """
    for value in query_values:
        if file_name == value:
            return value
        else:
            return file_name


def extract_file_names(query_data):
    """ Extract file name from the queries data.

        Parameters:
            query_data (obj): The queries data object.

        Returns:
            query_string (str): A concatenated string of file names.
    """

    return "|".join(check_query_file_type(entry["query"]) for entry in query_data.values())
