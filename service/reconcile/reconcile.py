import json

from flask import Blueprint, request, jsonify, render_template, make_response
from flask_cors import cross_origin

from service.commons.commons import make_commons_search
from service.manifest.manifest import get_api_manifest
from service.properties.property_suggest import get_property_suggest_results
from service.reconcile.processresults import (build_extend_result, build_query_results, get_suggest_result, get_entity_suggest_result)
from service.reconcile.handlefile import extract_file_names
from service.reconcile.media_preview import build_preview_content


reconcile = Blueprint('reconcile', __name__)


@cross_origin()
@reconcile.route('/', methods=['GET', 'POST'])
def home():
    return render_template('main/home.html',
                           host=request.host_url + 'en/api',
                           title='Home')


@reconcile.route('/<string:lang>/api', methods=['GET', 'POST'])
@cross_origin()
def get_manifest(lang):

    service_url = request.host_url + lang + '/api'

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


@reconcile.route('/<string:lang>/api/suggest/properties', methods=['GET'])
@cross_origin()
def get_suggest(lang):
    prefix = request.args.get("prefix", None)
    if prefix:
        suggest_results = get_suggest_result(prefix, lang)
        return jsonify(suggest_results)
    else:
        return "specify a prefix"


@reconcile.route('/<string:lang>/api/properties', methods=['GET'])
@cross_origin()
def get_property_suggestions(lang):
    if "type" in request.args:
        property_suggest_results = get_property_suggest_results(lang)
        return jsonify(property_suggest_results)
    else:
        return make_response(jsonify({
            "error": "error",
            "message": "Missing prefix type"
        }), 400)


@reconcile.route('/<string:lang>/api/suggest', methods=['GET'])
@cross_origin()
def get_entity_suggest(lang):
    prefix = request.args.get("prefix", None)
    if prefix:
        suggest_results = get_entity_suggest_result(prefix, lang)
        return jsonify(suggest_results)
    else:
        return make_response(jsonify({
            "error": "error",
            "message": "Missing prefix argument"
        }), 400)


@reconcile.route('/<string:lang>/api/preview', methods=['GET'])
@cross_origin()
def preview_media_file(lang):
    media_id = request.args.get("id", None)

    preview_content = build_preview_content(media_id)
    return preview_content
