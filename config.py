import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    API_TITLE = "Readout Error Mitigation Service API"
    API_VERSION = "0.1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/api"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_VERSION = "3.24.2"
    OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/"

    API_SPEC_OPTIONS = {
        "info": {
            "description": "This is the API Specification of the Readout Error Mitigation Service",
        },
        "license": {"name": "Apache v2 License"},
    }

    MINIO_ENDPOINT = os.environ.get("MINIO_URL") or "localhost:9000"
    MINIO_USER = "minio"
    MINIO_PASSWORD = "minio123"
    MINIO_SECURITY = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    pass


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
