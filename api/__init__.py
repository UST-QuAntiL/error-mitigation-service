from flask import Flask
from config import config
from api.controller import register_blueprints
from flask_smorest import Api
from flask_cors import CORS, cross_origin


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # cors = CORS(app)
    # app.config['CORS_HEADERS'] = 'Content-Type'

    api = Api(app)
    register_blueprints(api)

    @app.route("/")
    def heartbeat():
        return '<h1>Quokka is running</h1> <h3>View the API Docs <a href="/api/swagger-ui">here</a></h3>'

    return app
