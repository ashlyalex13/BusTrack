"""Registro de operaciones críticas y manejo de errores inesperados."""
import logging

from fastapi.testclient import TestClient

from app.main import app


def test_la_venta_queda_registrada_sin_datos_personales(sell, caplog):
    with caplog.at_level(logging.INFO, logger="bustrack"):
        t = sell(4, name="Ana Torres", doc="1010101010").json()
    log = caplog.text
    assert f"Venta: tiquete={t['uuid']}" in log
    assert "Ana Torres" not in log and "1010101010" not in log  # privacidad del pasajero


def test_rechazo_por_asiento_ocupado_queda_registrado(sell, caplog):
    sell(4)
    with caplog.at_level(logging.INFO, logger="bustrack"):
        sell(4, name="Otra Persona")
    assert "Venta rechazada" in caplog.text


def test_qr_alterado_queda_registrado(client, sell, seller_headers, caplog):
    code = sell(4).json()["code"]
    with caplog.at_level(logging.WARNING, logger="bustrack"):
        client.get("/api/tickets/verify", params={"code": code[:-1] + "x"}, headers=seller_headers)
    assert "QR rechazado (Firma inválida" in caplog.text


def test_login_fallido_queda_registrado_sin_la_clave(client, data, caplog):
    with caplog.at_level(logging.WARNING, logger="bustrack"):
        client.post("/api/auth/login", json={"email": "admin@test.co", "password": "clave-secreta-mala"})
    assert "Login fallido: admin@test.co" in caplog.text
    assert "clave-secreta-mala" not in caplog.text


def test_error_inesperado_devuelve_500_con_mensaje_claro(caplog):
    def boom():
        raise RuntimeError("detalle interno que no debe filtrarse")

    app.add_api_route("/api/_prueba_error", boom)
    try:
        with TestClient(app, raise_server_exceptions=False) as c, caplog.at_level(logging.ERROR, logger="bustrack"):
            r = c.get("/api/_prueba_error")
        assert r.status_code == 500
        assert "error interno" in r.json()["detail"]
        assert "detalle interno" not in r.text
        assert "Error no controlado en GET /api/_prueba_error" in caplog.text
    finally:
        app.router.routes = [rt for rt in app.router.routes if getattr(rt, "path", "") != "/api/_prueba_error"]
