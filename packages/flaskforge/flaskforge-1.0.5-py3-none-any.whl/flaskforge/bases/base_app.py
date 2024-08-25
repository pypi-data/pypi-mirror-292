from os import environ

from flask import Flask
from apispec import APISpec
from flask_apispec import FlaskApiSpec
from flask_jwt_extended import JWTManager
from apispec.ext.marshmallow import MarshmallowPlugin

app = Flask(__name__)


app.config.update(
    {
        "APISPEC_SPEC": APISpec(
            title=environ.get("SWAGGER_TITLE", "FlaskForge"),
            version=environ.get("API_VERSION", "1.0.0"),
            openapi_version="2.0",
            plugins=[MarshmallowPlugin()],
        ),
        "APISPEC_SWAGGER_UI_URL": f"""/{environ.get("SWAGGER_UI_URL", "documents")}/""",
        "APISPEC_SWAGGER_URL": "/json/",
        "JWT_SECRET_KEY": environ.get("JWT_SECRET_KEY"),
        "JWT_TOKEN_LOCATION": [environ.get("JWT_TOKEN_LOCATION", "cookies")],
        "JWT_COOKIE_CSRF_PROTECT": environ.get("JWT_COOKIE_CSRF_PROTECT", False),
    }
)

spec = FlaskApiSpec(app)

jwt = JWTManager(app)
