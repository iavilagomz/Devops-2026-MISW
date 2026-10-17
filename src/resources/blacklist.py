import re
from uuid import UUID

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from ..models import Blacklist, db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_REASON_LENGTH = 255


def client_ip():
    """IP de origen de la solicitud, respetando el balanceador de Beanstalk."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def validate_payload(payload):
    """Retorna la lista de errores de validacion del cuerpo del POST."""
    errors = []

    email = payload.get("email")
    if not email or not isinstance(email, str):
        errors.append("El campo email es obligatorio.")
    elif not EMAIL_RE.match(email):
        errors.append("El campo email no tiene un formato valido.")

    app_uuid = payload.get("app_uuid")
    if not app_uuid or not isinstance(app_uuid, str):
        errors.append("El campo app_uuid es obligatorio.")
    else:
        try:
            UUID(app_uuid)
        except ValueError:
            errors.append("El campo app_uuid debe ser un UUID valido.")

    blocked_reason = payload.get("blocked_reason")
    if blocked_reason is not None:
        if not isinstance(blocked_reason, str):
            errors.append("El campo blocked_reason debe ser texto.")
        elif len(blocked_reason) > MAX_REASON_LENGTH:
            errors.append(
                f"El campo blocked_reason admite maximo {MAX_REASON_LENGTH} caracteres."
            )

    return errors


class BlacklistResource(Resource):
    """POST /blacklists - agrega un email a la lista negra global."""

    @jwt_required()
    def post(self):
        payload = request.get_json(silent=True) or {}

        errors = validate_payload(payload)
        if errors:
            return {"created": False, "errors": errors}, 400

        entry = Blacklist(
            email=payload["email"].strip().lower(),
            app_uuid=payload["app_uuid"],
            blocked_reason=payload.get("blocked_reason"),
            ip_address=client_ip(),
        )
        db.session.add(entry)
        db.session.commit()

        return {
            "created": True,
            "message": "El email fue agregado a la lista negra global.",
            "id": entry.id,
            "email": entry.email,
            "created_at": entry.created_at.isoformat(),
        }, 201


class BlacklistCheckResource(Resource):
    """GET /blacklists/<email> - consulta si un email esta en la lista negra."""

    @jwt_required()
    def get(self, email):
        entry = (
            db.session.query(Blacklist)
            .filter_by(email=email.strip().lower())
            .order_by(Blacklist.created_at.desc())
            .first()
        )

        if entry is None:
            return {"email": email, "blacklisted": False, "blocked_reason": None}, 200

        return {
            "email": entry.email,
            "blacklisted": True,
            "blocked_reason": entry.blocked_reason,
        }, 200
