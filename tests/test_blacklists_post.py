"""Escenarios de prueba para POST /blacklists."""
from src.models import Blacklist


def test_agrega_email_valido(client, auth_headers, valid_payload, app):
    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)

    assert response.status_code == 201
    body = response.get_json()
    assert body["created"] is True
    assert body["email"] == "cliente@ejemplo.com"
    assert "created_at" in body

    with app.app_context():
        entry = Blacklist.query.filter_by(email="cliente@ejemplo.com").one()
        assert entry.ip_address  # se guarda la IP de origen
        assert entry.created_at is not None  # y la fecha/hora


def test_guarda_ip_de_x_forwarded_for(client, auth_headers, valid_payload, app):
    headers = {**auth_headers, "X-Forwarded-For": "200.1.2.3, 10.0.0.1"}
    client.post("/blacklists", json=valid_payload, headers=headers)

    with app.app_context():
        assert Blacklist.query.one().ip_address == "200.1.2.3"


def test_motivo_es_opcional(client, auth_headers, valid_payload):
    del valid_payload["blocked_reason"]
    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)
    assert response.status_code == 201


def test_normaliza_email_a_minusculas(client, auth_headers, valid_payload):
    valid_payload["email"] = "Cliente@Ejemplo.COM"
    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)
    assert response.get_json()["email"] == "cliente@ejemplo.com"


def test_rechaza_sin_token(client, valid_payload):
    response = client.post("/blacklists", json=valid_payload)
    assert response.status_code == 401


def test_rechaza_token_invalido(client, valid_payload):
    headers = {"Authorization": "Bearer token-falso"}
    response = client.post("/blacklists", json=valid_payload, headers=headers)
    assert response.status_code == 422


def test_rechaza_sin_email(client, auth_headers, valid_payload):
    del valid_payload["email"]
    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)
    assert response.status_code == 400
    assert response.get_json()["created"] is False


def test_rechaza_email_mal_formado(client, auth_headers, valid_payload):
    valid_payload["email"] = "no-es-un-email"
    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)
    assert response.status_code == 400


def test_rechaza_sin_app_uuid(client, auth_headers, valid_payload):
    del valid_payload["app_uuid"]
    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)
    assert response.status_code == 400


def test_rechaza_app_uuid_invalido(client, auth_headers, valid_payload):
    valid_payload["app_uuid"] = "1234"
    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)
    assert response.status_code == 400


def test_rechaza_motivo_mayor_a_255(client, auth_headers, valid_payload):
    valid_payload["blocked_reason"] = "x" * 256
    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)
    assert response.status_code == 400


def test_rechaza_cuerpo_vacio(client, auth_headers):
    response = client.post("/blacklists", headers=auth_headers)
    assert response.status_code == 400
