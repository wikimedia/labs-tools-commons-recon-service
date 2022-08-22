# commons-recon-service
A reconciliation service designed for Wikimedia Commons, to support its integration in OpenRefine.

This service can also be deployed on other MediaWiki instances to enable file upload and wikitext editing on that instance.

## Quick start guide

#. Create a virtual environment, activate and install requirements using the following command

```
* python -m venv service/venv
* source service/venv/bin/activate
* pip install -r requirements.txt
```

#. Create a config file /service/config.yaml with the following content:

This assumes that your wiki is running at `https://my-great-wiki.com/wiki/` and that this reconciliation service is deployed at `https://media-recon.my-great-wiki.com`.

```
SECRET_KEY: '$(python -c "import os; print repr(os.urandom(24))")'
SERVICE_NAME: "Bubbletea"
IDENTIFIER_SPACE: "http://my-great-wiki.com/entity/"
SCHEMA_SPACE: "http://my-great-wiki.com/prop/direct/"
VIEW_TEMPLATE: "https://media-recon.my-great-wiki.com/redirect_entity?id={{id}}"
API_URL: "https://my-great-wiki.com/w/api.php"
INDEX_URL: "https://my-great-wiki.com/w/index.php"
CORS_HEADERS: 'application/json'
WD_API_URL: "https://www.wikidata.org/w/api.php"
SERVICE_URL: "https://media-recon.my-great-wiki.com"
MEDIA_PREV_W: 100
MEDIA_PREV_H: 50
properties: [ "wikitext" ]
```

Here are some explanations about each of those settings:
* `SECRET_KEY`: a value used internally in Flask. Because the application is stateless, this does not need to persist after restarts.
* `SERVICE_NAME`: the name of the reconciliation service (which should probably be the name of the wiki)
* `IDENTIFIER_SPACE`: the RDF serialization prefix for entities in the Wikibase instance. This should match the value present in your Wikibase manifest
* `SCHEMA_SPACE`: the RDF serialization prefix for properties (used as direct statements) in the Wikibase instance. This should match the value present in your Wikibase manifest.
* `VIEW_TEMPLATE`: this is a route provided by the reconciliation endpoint to translate Mids to URLs of the corresponding files. For wikikis which support MediaInfo, this can be replaced by `https://my-great-wiki.com/entity/`.
* `API_URL`: the MediaWiki API URL of your wiki
* `INDEX_URL` the `index.php` URL of your wiki
* `WD_API_URL` is only used on wikis with MediaInfo support and is the API endpoint of the Wikibase instance which stores properties and items used in the MediaInfo entities
* `SERVICE_URL`: the URL at which the service is deployed
* `MEDIA_PREV_W` and `MEDIA_PREV_H`: dimensions for thumbnails in the previews served by the service
* `properties` is the list of properties which are suggested by default in the "Add columns from reconciled values" dialog. For wikis which support MediaInfo entities, this can contain Wikibase property ids. Otherwise, only "wikitext" is supported.

#. Run the flask application

In development settings, one can run the application with:
```
python app.py
```
For production settings, the `service/__init__.py` file can be used for WSGI deployment.
