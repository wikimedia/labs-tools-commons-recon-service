# commons-recon-service
A reconciliation service for structured data on Wikimedia Commons.

## Quick start guide

#. Create a virtual environment, activate and install requirements using the following command

```
* python -m venv service/venv
* source service/venv/bin/activate
* pip install -r requirements.txt
```

#. Create a config file /service/config.yaml with the following content:

```
SECRET_KEY: <flask secreat key>
```

#. Run the flask application

```
python app.py
```