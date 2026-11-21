"""Validaciones de negocio: no se vende en viajes que ya salieron y los datos del pasajero son coherentes."""
from datetime import timedelta

import pytest

from app.clock import now
from app.database import SessionLocal
from app.models import Trip


def depart_now(trip_id, minutes_ago=1):
    with SessionLocal() as db:
        db.get(Trip, trip_id).departure_at = now() - timedelta(minutes=minutes_ago)
        db.commit()


def test_no_se_vende_en_un_viaje_cuya_hora_de_salida_ya_paso(sell, data):
    depart_now(data.trip_id)
    r = sell(1)
    assert r.status_code == 409
    assert "ya salió" in r.json()["detail"]


def test_no_se_reserva_en_un_viaje_que_ya_salio(client, data, seller_headers):
    depart_now(data.trip_id)
    r = client.post(f"/api/trips/{data.trip_id}/holds", json={"seat_number": 1}, headers=seller_headers)
    assert r.status_code == 409


def test_no_se_programan_viajes_en_el_pasado(client, admin_headers, data):
    past = (now() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
    body = {"route_id": data.route_id, "company_id": data.company_id, "departure_at": past}
    r = client.post("/api/trips", json=body, headers=admin_headers)
    assert r.status_code == 422
    assert "posteriores" in r.json()["detail"]


@pytest.mark.parametrize("name", ["Juan123", "@@@ ###", "...", "Ana<script>"])
def test_nombre_de_pasajero_invalido(sell, name):
    r = sell(1, name=name)
    assert r.status_code == 422
    assert "nombre" in str(r.json()["detail"])


@pytest.mark.parametrize("doc", ["12 34 56", "1144-55'6", "123$4567", "x" * 21])
def test_documento_invalido(sell, doc):
    assert sell(1, doc=doc).status_code == 422


def test_nombres_con_tildes_y_enie_son_validos(sell):
    assert sell(1, name="José Ñúñez O'Neil").status_code == 201


def test_datos_del_pasajero_se_normalizan(sell):
    t = sell(1, name="  María    del   Mar  ", doc=" pa-12345 ").json()
    assert t["passenger_name"] == "María del Mar"
    assert t["passenger_doc"] == "PA-12345"
