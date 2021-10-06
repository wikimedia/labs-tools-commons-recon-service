import os
import json

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from service.manifest.manifest import get_api_manifest
from service.api.utils import extract_file_names, make_commons_search, build_results


manifest = Blueprint('manifest', __name__)


@manifest.route('/<string:lang>/api', methods=['GET', 'POST'])
@cross_origin()
def get_manifest(lang):

    if request.method == "POST":

        queries = request.values.get('queries')

    else:

        queries = request.args.get('queries')

    if queries is None:

        return jsonify(get_api_manifest(lang))

    else:

        queries_data = json.loads(queries)
        pages = make_commons_search(extract_file_names(queries_data))

        return jsonify(build_results(queries_data, pages))
