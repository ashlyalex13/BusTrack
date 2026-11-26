"""RNF03: seguridad de punta a punta (bloqueo de login por fuerza bruta y cabeceras HTTP)."""
from tests.integration.conftest import PASSWORD


def bad_login(client, email="admin@test.co"):
    return client.post("/api/auth/login", json={"email": email, "password": "incorrecta"})


def test_bloqueo_tras_5_intentos_fallidos(client, data):
    for _ in range(5):
        assert bad_login(client).status_code == 401
    r = bad_login(client)
    assert r.status_code == 429
    assert "Demasiados intentos" in r.json()["detail"]
    assert int(r.headers["Retry-After"]) > 0


def test_bloqueado_ni_siquiera_con_la_clave_correcta(client, data):
    for _ in range(5):
        bad_login(client)
    r = client.post("/api/auth/login", json={"email": "admin@test.co", "password": PASSWORD})
    assert r.status_code == 429


def test_el_bloqueo_es_por_cuenta_no_afecta_a_otros_usuarios(client, data):
    for _ in range(5):
        bad_login(client, "admin@test.co")
    r = client.post("/api/auth/login", json={"email": "taquilla@test.co", "password": PASSWORD})
    assert r.status_code == 200


def test_login_correcto_reinicia_el_contador(client, data):
    for _ in range(4):
        bad_login(client)
    assert client.post("/api/auth/login", json={"email": "admin@test.co", "password": PASSWORD}).status_code == 200
    for _ in range(4):
        assert bad_login(client).status_code == 401  # vuelve a tener 5 intentos


def test_cabeceras_de_seguridad(client):
    headers = client.get("/api/health").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
