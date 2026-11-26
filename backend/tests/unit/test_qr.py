"""Unitarias de app/qr.py: firma HMAC del tiquete (RNF02) y generación de la imagen QR."""
import base64
import hashlib
import hmac

import pytest

from app import qr

UUID = "11111111-2222-3333-4444-555555555555"


def test_la_firma_es_determinista_y_de_32_caracteres_hex():
    a = qr.sign(UUID, 7, 12)
    assert a == qr.sign(UUID, 7, 12)
    assert len(a) == 32 and int(a, 16) >= 0


def test_la_firma_coincide_con_hmac_sha256_truncado():
    expected = hmac.new(qr.QR_SECRET.encode(), f"{UUID}|7|12".encode(), hashlib.sha256).hexdigest()[:32]
    assert qr.sign(UUID, 7, 12) == expected


@pytest.mark.parametrize("uuid,trip,seat", [
    ("99999999-2222-3333-4444-555555555555", 7, 12),  # otro tiquete
    (UUID, 8, 12),                                     # otro viaje
    (UUID, 7, 13),                                     # otro asiento
])
def test_cambiar_cualquier_dato_cambia_la_firma(uuid, trip, seat):
    assert qr.sign(uuid, trip, seat) != qr.sign(UUID, 7, 12)


def test_la_firma_depende_del_secreto_del_servidor(monkeypatch):
    original = qr.sign(UUID, 7, 12)
    monkeypatch.setattr(qr, "QR_SECRET", "otro-secreto-distinto-de-32-bytes-o-mas")
    assert qr.sign(UUID, 7, 12) != original


def test_formato_del_codigo():
    assert qr.build_code(UUID, "abc123") == f"{UUID}.abc123"


def test_la_imagen_qr_es_un_png_valido():
    data_url = qr.qr_data_url("contenido de prueba")
    prefix = "data:image/png;base64,"
    assert data_url.startswith(prefix)
    png = base64.b64decode(data_url[len(prefix):])
    assert png[:8] == b"\x89PNG\r\n\x1a\n"  # firma binaria de un archivo PNG
