import sys
import os
import json

from flask import Blueprint, request, jsonify

from service.manifest.manifest import get_api_manifest


manifest = Blueprint('manifest', __name__)


@manifest.route('/<string:lang>/api', methods=['GET', 'POST'])
def get_manifest(lang):
    query = request.args.get('query')
    print(query, file=sys.stderr)
    if query is None:
        return jsonify(get_api_manifest(lang))
    else:
        return "Failure"
