"""Escenarios de prueba para el health check usado por Beanstalk."""


def test_health_responde_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_raiz_responde_ok(client):
    assert client.get("/").status_code == 200


def test_ruta_inexistente_retorna_404(client):
    assert client.get("/no-existe").status_code == 404
