import os

import yaml
from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))

# Another secret key will be generated later
app.config['SECRET_KEY']


# we import all our blueprint routes here
from service.main.routes import main


# Here we register the various blue_prints of our app
app.register_blueprint(main)
