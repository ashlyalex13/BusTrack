"""Verifica que el entorno de pruebas esté bien montado."""


def test_api_responde(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_datos_base_cargados(client, data):
    seats = client.get(f"/api/trips/{data.trip_id}/seats").json()
    assert seats["trip"]["origin"] == "Cali"
    assert len(seats["seats"]) == 20
    assert all(s["status"] == "free" for s in seats["seats"])
