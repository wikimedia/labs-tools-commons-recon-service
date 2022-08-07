import os

import yaml
from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

config_file = 'config.yaml'

__dir__ = os.path.dirname(__file__)
config_path = os.path.join(__dir__, config_file)

if os.path.isfile(config_path):
    # Load configuration from YAML file
    app.config.update(
        yaml.safe_load(open(config_path)))

else:
    app.config.update(
        yaml.safe_load(open(os.path.join(__dir__, 'test_config.yaml'))))

# Another secret key will be generated later
app.config['SECRET_KEY']
app.config['CORS_HEADERS']

# we import all our blueprint routes here
from service.reconcile.reconcile import reconcile

# Here we register the various blue_prints of our app
app.register_blueprint(reconcile)
