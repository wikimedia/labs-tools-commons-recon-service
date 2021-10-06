import os

import yaml
from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

config_file = 'config.yaml'

if os.path.isfile(config_file):
    # Load configuration from YAML file
    __dir__ = os.path.dirname(__file__)
    app.config.update(
        yaml.safe_load(open(os.path.join(__dir__, config_file))))

else:
    __dir__ = os.path.dirname(__file__)
    app.config.update(
        yaml.safe_load(open(os.path.join(__dir__, 'test_config.yaml'))))

# Another secret key will be generated later
app.config['SECRET_KEY']
app.config['CORS_HEADERS']

# we import all our blueprint routes here
from service.main.routes import main
from service.api.routes import manifest

# Here we register the various blue_prints of our app
app.register_blueprint(main)
app.register_blueprint(manifest)
