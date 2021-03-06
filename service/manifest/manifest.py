def get_api_manifest(lang, service_url):
    manifest = {
        "versions": ["0.2"],
        'name': "Wikimedia Commons" + (' (%s)' % lang),
        "identifierSpace": "https://commons.wikimedia.org/entity/",
        "schemaSpace": "http://www.wikidata.org/prop/direct/",
        "view": {
            "url": "https://commons.wikimedia.org/entity/{{id}}"
        },
        "preview": {
            "url": service_url + "/preview?id={{id}}",
            "width": 500,
            "height": 60
        },
        "extend": {
            "propose_properties": {
                "service_path": "/properties",
                "service_url": service_url
            }
        },
        "suggest": {
            "property": {
                "service_path": "/suggest/properties",
                "service_url": service_url
            },
            "entity": {
                "service_path": "/suggest",
                "service_url": service_url
            }
        }
    }
    return manifest
