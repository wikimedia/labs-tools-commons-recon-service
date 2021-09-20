def get_api_manifest(lang):
    manifest = {
        "versions": ["0.2"],
        "name": "Wikimedia Commons",
        "identifierSpace": "https://commons.wikimedia.org/entity/",
        "schemaSpace": "http://www.wikidata.org/prop/direct/",
        "view": {
            "url": "https://commons.wikimedia.org/entity/{{id}}"
        }
    }
    return manifest