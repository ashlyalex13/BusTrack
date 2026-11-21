"""RNF03: endurecimiento de seguridad (fuerza bruta, secretos, zona horaria y cabeceras)."""
from datetime import datetime, timezone

import pytest

from app import config
from app.clock import now
from app.rate_limit import LoginLimiter
from tests.conftest import PASSWORD


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


def test_el_bloqueo_expira_con_el_tiempo(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr("app.rate_limit.time.monotonic", lambda: clock[0])
    limiter = LoginLimiter(max_attempts=3, window_seconds=60)
    for _ in range(3):
        limiter.register_failure("k")
    assert limiter.retry_after("k") > 0
    clock[0] += 61
    assert limiter.retry_after("k") == 0


@pytest.mark.parametrize("jwt,qr,env", [
    ("corto", "x" * 40, "development"),                                        # secreto débil
    (config._DEV_JWT_SECRET, config._DEV_QR_SECRET, "production"),             # valores de desarrollo en producción
])
def test_configuracion_insegura_impide_arrancar(monkeypatch, jwt, qr, env):
    monkeypatch.setattr(config, "JWT_SECRET", jwt)
    monkeypatch.setattr(config, "QR_SECRET", qr)
    monkeypatch.setattr(config, "APP_ENV", env)
    with pytest.raises(RuntimeError):
        config._validate_secrets()


def test_hora_de_la_terminal_es_la_de_colombia():
    utc = datetime.now(timezone.utc).replace(tzinfo=None)
    diff_hours = round((utc - now()).total_seconds() / 3600)
    assert diff_hours == 5  # Colombia es UTC-5 todo el año


def test_cabeceras_de_seguridad(client):
    headers = client.get("/api/health").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
