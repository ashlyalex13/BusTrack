"""HU04 / RF10 / RNF02 / Semana 7: el QR alterado, inexistente o ya usado debe ser rechazado."""
import uuid

from app.qr import sign


def verify(client, headers, code):
    return client.get("/api/tickets/verify", params={"code": code}, headers=headers).json()


def board(client, headers, code):
    return client.post("/api/tickets/verify", json={"code": code}, headers=headers).json()


def test_qr_valido_muestra_pasajero_viaje_y_asiento(client, sell, seller_headers):
    code = sell(12).json()["code"]
    r = verify(client, seller_headers, code)
    assert r["valid"] is True
    assert r["message"] == "Tiquete válido"
    assert r["ticket"]["passenger_name"] == "Carlos Pérez"
    assert r["ticket"]["seat_number"] == 12
    assert r["ticket"]["trip"]["destination"] == "Buga"


def test_consultar_no_marca_abordaje(client, sell, seller_headers):
    code = sell(12).json()["code"]
    verify(client, seller_headers, code)
    assert verify(client, seller_headers, code)["valid"] is True


def test_qr_con_firma_alterada_es_rechazado(client, sell, seller_headers):
    code = sell(12).json()["code"]
    tampered = code[:-1] + ("0" if code[-1] != "0" else "1")
    r = verify(client, seller_headers, tampered)
    assert r["valid"] is False
    assert "alterado" in r["message"]


def test_qr_con_uuid_inventado_es_rechazado(client, data, seller_headers):
    fake = str(uuid.uuid4())
    r = verify(client, seller_headers, f"{fake}.{sign(fake, data.trip_id, 1)}")
    assert r == {"valid": False, "message": "El tiquete no existe", "ticket": None}


def test_firma_de_otro_tiquete_no_sirve(client, sell, seller_headers):
    """No basta con conocer un UUID: la firma está atada a ese tiquete, viaje y asiento."""
    a = sell(1).json()["code"]
    b = sell(2).json()["code"]
    mixed = a.split(".")[0] + "." + b.split(".")[1]
    assert verify(client, seller_headers, mixed)["valid"] is False


def test_firma_generada_sin_el_secreto_del_servidor_es_rechazada(client, sell, seller_headers):
    import hashlib
    import hmac
    t = sell(3).json()
    forged = hmac.new(b"otro-secreto", f"{t['uuid']}|{t['trip_id']}|3".encode(), hashlib.sha256).hexdigest()[:32]
    assert verify(client, seller_headers, f"{t['uuid']}.{forged}")["valid"] is False


def test_codigo_sin_formato_es_rechazado(client, data, seller_headers):
    assert verify(client, seller_headers, "texto-cualquiera")["message"] == "Formato de código inválido"


def test_abordaje_valido_y_reuso_rechazado(client, sell, seller_headers):
    code = sell(15).json()["code"]
    first = board(client, seller_headers, code)
    assert first["valid"] is True
    assert first["ticket"]["status"] == "boarded"
    second = board(client, seller_headers, code)
    assert second["valid"] is False
    assert "ya fue usado" in second["message"]


def test_tiquete_anulado_es_rechazado(client, sell, seller_headers, admin_headers):
    t = sell(16).json()
    client.post(f"/api/tickets/{t['uuid']}/cancel", headers=admin_headers)
    r = verify(client, seller_headers, t["code"])
    assert r["valid"] is False and r["message"] == "El tiquete fue anulado"


def test_asiento_abordado_se_ve_en_la_grilla(client, sell, data, seller_headers):
    board(client, seller_headers, sell(18).json()["code"])
    seats = client.get(f"/api/trips/{data.trip_id}/seats").json()["seats"]
    assert seats[17]["status"] == "boarded"
