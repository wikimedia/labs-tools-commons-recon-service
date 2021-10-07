def get_api_manifest(lang, service_url):
    manifest = {
        "versions": ["0.2"],
        "name": "Wikimedia Commons",
        "identifierSpace": "https://commons.wikimedia.org/entity/",
        "schemaSpace": "http://www.wikidata.org/prop/direct/",
        "view": {
            "url": "https://commons.wikimedia.org/entity/{{id}}"
        },
        "extend": {}
    }
    return manifest
