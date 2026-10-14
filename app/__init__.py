import click
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return {"message": "Token invalido."}, 401

    @jwt.unauthorized_loader
    def missing_token(reason):
        return {"message": "Falta el token de autorizacion."}, 401

    @jwt.expired_token_loader
    def expired_token(header, payload):
        return {"message": "Token expirado."}, 401

    from app.resources import register_routes

    register_routes(Api(app))

    with app.app_context():
        from app import models  # noqa: F401

        try:
            db.create_all()
        except Exception as exc:
            app.logger.warning("create_all fallo: %s", exc)

    @app.cli.command("create-token")
    def create_token():
        """Genera el token estatico (sin expiracion) para usar como Bearer."""
        click.echo(create_access_token(identity="blacklist-client", expires_delta=False))

    return app
