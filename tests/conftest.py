"""Fixtures compartidas: app Flask con SQLite en memoria y token JWT de prueba.

Las pruebas no dependen de PostgreSQL/RDS: DATABASE_URL apunta a SQLite en
memoria, de modo que corren igual en local y dentro de AWS CodeBuild.
"""
import pytest
from flask_jwt_extended import create_access_token

from src import create_app
from src.models import db

VALID_UUID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("JWT_SECRET_KEY", "clave-de-pruebas")
    app = create_app()
    app.config["TESTING"] = True
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="blacklist-service")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valid_payload():
    return {
        "email": "cliente@ejemplo.com",
        "app_uuid": VALID_UUID,
        "blocked_reason": "Solicitud del cliente",
    }
