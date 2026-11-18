"""HU03: la grilla muestra asientos reservados; la reserva temporal bloquea a las demás taquillas y expira sola."""
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import SeatHold


def hold(client, headers, trip_id, seat):
    return client.post(f"/api/trips/{trip_id}/holds", json={"seat_number": seat}, headers=headers)


def seat_status(client, trip_id, seat):
    return client.get(f"/api/trips/{trip_id}/seats").json()["seats"][seat - 1]["status"]


def test_reservar_asiento_lo_muestra_como_reservado(client, data, seller_headers):
    r = hold(client, seller_headers, data.trip_id, 8)
    assert r.status_code == 200
    assert r.json() == {"trip_id": data.trip_id, "seat_number": 8, "expires_in": 120}
    assert seat_status(client, data.trip_id, 8) == "reserved"


def test_otra_taquilla_no_puede_reservar_ni_vender_un_asiento_reservado(client, data, seller_headers, seller2_headers):
    hold(client, seller_headers, data.trip_id, 8)
    assert hold(client, seller2_headers, data.trip_id, 8).status_code == 409
    body = {"trip_id": data.trip_id, "seat_number": 8, "passenger_name": "Otra Persona", "passenger_doc": "99887766"}
    r = client.post("/api/tickets", json=body, headers=seller2_headers)
    assert r.status_code == 409
    assert "reservado por otra taquilla" in r.json()["detail"]


def test_quien_reserva_si_puede_vender_y_la_reserva_se_consume(client, data, seller_headers, sell):
    hold(client, seller_headers, data.trip_id, 8)
    assert sell(8).status_code == 201
    assert seat_status(client, data.trip_id, 8) == "sold"
    with SessionLocal() as db:
        assert db.get(SeatHold, (data.trip_id, 8)) is None


def test_reserva_expirada_ya_no_bloquea(client, data, seller_headers, seller2_headers):
    hold(client, seller_headers, data.trip_id, 8)
    with SessionLocal() as db:
        db.get(SeatHold, (data.trip_id, 8)).expires_at = datetime.now() - timedelta(seconds=1)
        db.commit()
    assert seat_status(client, data.trip_id, 8) == "free"
    assert hold(client, seller2_headers, data.trip_id, 8).status_code == 200


def test_liberar_reserva(client, data, seller_headers):
    hold(client, seller_headers, data.trip_id, 8)
    assert client.delete(f"/api/trips/{data.trip_id}/holds/8", headers=seller_headers).status_code == 204
    assert seat_status(client, data.trip_id, 8) == "free"


def test_un_taquillero_no_libera_la_reserva_de_otro(client, data, seller_headers, seller2_headers):
    hold(client, seller_headers, data.trip_id, 8)
    client.delete(f"/api/trips/{data.trip_id}/holds/8", headers=seller2_headers)
    assert seat_status(client, data.trip_id, 8) == "reserved"


def test_cambiar_de_asiento_libera_el_anterior(client, data, seller_headers):
    hold(client, seller_headers, data.trip_id, 8)
    hold(client, seller_headers, data.trip_id, 9)
    assert seat_status(client, data.trip_id, 8) == "free"
    assert seat_status(client, data.trip_id, 9) == "reserved"


def test_no_se_reserva_un_asiento_vendido_ni_fuera_de_rango(client, data, seller_headers, sell):
    sell(3)
    assert hold(client, seller_headers, data.trip_id, 3).status_code == 409
    assert hold(client, seller_headers, data.trip_id, 50).status_code == 422


def test_reservar_requiere_sesion(client, data):
    assert client.post(f"/api/trips/{data.trip_id}/holds", json={"seat_number": 1}).status_code == 401
