def get_api_manifest(lang, service_url):
    print(service_url)
    manifest = {
        "versions": ["0.2"],
        "name": "Wikimedia Commons",
        "identifierSpace": "https://commons.wikimedia.org/entity/",
        "schemaSpace": "http://www.wikidata.org/prop/direct/",
        "view": {
            "url": "https://commons.wikimedia.org/entity/{{id}}"
        },
        "preview": {
            "url": service_url + "/preview?id={{id}}",
            "width": 200,
            "height": 100
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
