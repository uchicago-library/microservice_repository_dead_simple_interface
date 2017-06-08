from flask import Flask
from .blueprint import BLUEPRINT
from flask_env import MetaFlaskEnv


class Configuration(metaclass=MetaFlaskEnv):
    ENV_PREFIX = "DEAD_SIMPLE_INTERFACE_"
    DEBUG = False
    DEFER_CONFIG = False


app = Flask(__name__)

app.config.from_object(Configuration)

app.register_blueprint(BLUEPRINT)
