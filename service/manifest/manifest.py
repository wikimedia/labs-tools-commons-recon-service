from service import app


def get_api_manifest(lang, service_url):
    manifest = {
        "versions": ["0.2"],
        'name': app.config['SERVICE_NAME'] + (' (%s)' % lang),
        "identifierSpace": app.config['IDENTIFIER_SPACE'],
        "schemaSpace": app.config['SCHEMA_SPACE'],
        "view": {
            "url": app.config['VIEW_TEMPLATE'],
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
