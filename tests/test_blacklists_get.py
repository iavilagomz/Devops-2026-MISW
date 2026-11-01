"""Escenarios de prueba para GET /blacklists/<email>."""


def test_email_en_lista_negra(client, auth_headers, valid_payload):
    client.post("/blacklists", json=valid_payload, headers=auth_headers)

    response = client.get("/blacklists/cliente@ejemplo.com", headers=auth_headers)

    assert response.status_code == 200
    body = response.get_json()
    assert body["blacklisted"] is True
    assert body["blocked_reason"] == "Solicitud del cliente"


def test_email_no_esta_en_lista_negra(client, auth_headers):
    response = client.get("/blacklists/libre@ejemplo.com", headers=auth_headers)

    assert response.status_code == 200
    body = response.get_json()
    assert body["blacklisted"] is False
    assert body["blocked_reason"] is None


def test_consulta_no_distingue_mayusculas(client, auth_headers, valid_payload):
    client.post("/blacklists", json=valid_payload, headers=auth_headers)
    response = client.get("/blacklists/CLIENTE@Ejemplo.com", headers=auth_headers)
    assert response.get_json()["blacklisted"] is True


def test_retorna_el_motivo_mas_reciente(client, auth_headers, valid_payload):
    client.post("/blacklists", json=valid_payload, headers=auth_headers)
    valid_payload["blocked_reason"] = "Segundo motivo"
    client.post("/blacklists", json=valid_payload, headers=auth_headers)

    response = client.get("/blacklists/cliente@ejemplo.com", headers=auth_headers)
    assert response.get_json()["blocked_reason"] == "Segundo motivo"


def test_get_rechaza_sin_token(client):
    response = client.get("/blacklists/cliente@ejemplo.com")
    assert response.status_code == 401
