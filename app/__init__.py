from flask import Flask
from config import config
from app.controller import register_blueprints
from flask_smorest import Api


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # cors = CORS(app)
    # app.config['CORS_HEADERS'] = 'Content-Type'

    api = Api(app)
    register_blueprints(api)

    @app.route("/")
    def heartbeat():
        return '<h1>The Error-Mitigation Service is Running</h1> <h3>View the API Docs <a href="/api/swagger-ui">here</a></h3>'

    return app
