import os
import json
import sys

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from service.manifest.manifest import get_api_manifest
from service.api.utils import extract_file_names, make_commons_search, build_query_results, build_extend_result


manifest = Blueprint('manifest', __name__)


@manifest.route('/<string:lang>/api', methods=['GET', 'POST'])
@cross_origin()
def get_manifest(lang):

    service_url = request.host_url + 'en/api'

    api_results = {}
    action = []

    if request.method == "POST" and request.values:

        action = list(request.values.to_dict(flat=False).keys())
        data = request.values.get(action[0])

    elif request.method == "GET" and request.args:

        action = list(request.args.to_dict(flat=False).keys())
        data = request.args.get(action[0])

    # If the requet has an action.
    if action:

        # Action is queries
        if action[0] == 'queries':

            queries_data = json.loads(data)
            pages = make_commons_search(extract_file_names(queries_data))
            api_results = build_query_results(queries_data, pages)

        # Action is extend
        elif action[0] == 'extend':

            # return extend data here
            api_results = build_extend_result(json.loads(data), lang)

        # Action is not neither of the actions we support
        # Present service manifest
        else:

            api_results = get_api_manifest(lang, service_url)
    
    # No action is requested present service manifest
    else:

        api_results = get_api_manifest(lang, service_url)

    return jsonify(api_results)
