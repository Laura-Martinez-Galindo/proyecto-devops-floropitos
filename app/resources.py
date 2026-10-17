from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import BlacklistEntry
from app.schemas import BlacklistCreateSchema

create_schema = BlacklistCreateSchema()


def client_ip():
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr


class HealthResource(Resource):
    def get(self):
        return {"status": "ok"}, 200


class BlacklistListResource(Resource):
    @jwt_required()
    def post(self):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return {"message": "El cuerpo debe ser un JSON valido."}, 400

        try:
            data = create_schema.load(payload)
        except ValidationError as err:
            return {
                "message": "No se pudo agregar el email a la lista negra.",
                "errors": err.messages,
            }, 400

        email = data["email"].strip().lower()

        if BlacklistEntry.query.filter_by(email=email).first():
            return {"message": "El email ya estaba en la lista negra global."}, 409

        entry = BlacklistEntry(
            email=email,
            app_uuid=str(data["app_uuid"]),
            blocked_reason=data["blocked_reason"],
            ip_address=client_ip(),
        )
        db.session.add(entry)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "El email ya estaba en la lista negra global."}, 409

        return {"message": "El email fue agregado a la lista negra global."}, 201


class BlacklistDetailResource(Resource):
    @jwt_required()
    def get(self, email):
        clean_email = email.strip().lower()
        entry = BlacklistEntry.query.filter_by(email=clean_email).first()
        if entry:
            return {"is_blocked": True, "blocked_reason": entry.blocked_reason}, 200
        return {"is_blocked": False, "blocked_reason": None}, 200


def register_routes(api):
    api.add_resource(HealthResource, "/health")
    api.add_resource(BlacklistListResource, "/blacklists")
    api.add_resource(BlacklistDetailResource, "/blacklists/<string:email>")
