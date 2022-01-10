def get_api_manifest(lang, service_url):
    manifest = {
        "versions": ["0.2"],
        'name': "Wikimedia Commons" + (' (%s)' % lang),
        "identifierSpace": "https://commons.wikimedia.org/entity/",
        "schemaSpace": "http://www.wikidata.org/prop/direct/",
        "view": {
            "url": "https://commons.wikimedia.org/entity/{{id}}"
        },
        "extend": {},
        "suggest": {
            "property": {
                "service_path": "/suggest/properties",
                "service_url": service_url
            }
        }
    }
    return manifest
