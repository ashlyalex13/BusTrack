"""HU03 / RNF01 / RF06: venta de tiquetes sin doble venta, incluida la venta concurrente."""
import threading

import pytest
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import Ticket, Trip, User
from app.qr import sign
from app.routers.tickets import sell as sell_endpoint
from app.schemas import TicketIn


def test_venta_exitosa_devuelve_tiquete_con_qr(sell, data):
    r = sell(7)
    assert r.status_code == 201
    t = r.json()
    assert t["seat_number"] == 7
    assert t["price"] == data.fare  # la tarifa sale de la ruta (RF02)
    assert t["status"] == "sold"
    assert t["seller_name"] == "Taquilla Pruebas"
    assert t["qr_image"].startswith("data:image/png;base64,")
    uuid, signature = t["code"].split(".")
    assert len(uuid) == 36 and len(signature) == 32


def test_asiento_vendido_aparece_ocupado_en_la_grilla(client, sell, data):
    sell(7)
    seats = client.get(f"/api/trips/{data.trip_id}/seats").json()
    assert seats["seats"][6]["status"] == "sold"
    assert seats["trip"]["available"] == 19


def test_no_se_puede_vender_dos_veces_el_mismo_asiento(sell):
    assert sell(7).status_code == 201
    r = sell(7, name="Otra Persona", doc="99887766")
    assert r.status_code == 409
    assert r.json()["detail"] == "El asiento 7 ya fue vendido"


@pytest.mark.parametrize("seat", [0, 21, -3])
def test_asiento_fuera_de_rango_es_rechazado(sell, seat):
    assert sell(seat).status_code == 422


def test_viaje_inexistente(sell):
    assert sell(1, trip_id=999999).status_code == 404


@pytest.mark.parametrize("status", ["cancelled", "departed"])
def test_no_se_vende_en_viajes_cancelados_o_despachados(sell, data, status):
    with SessionLocal() as db:
        db.get(Trip, data.trip_id).status = status
        db.commit()
    assert sell(1).status_code == 409


@pytest.mark.parametrize("field,value", [("passenger_name", "Al"), ("passenger_doc", "123")])
def test_datos_del_pasajero_se_validan(client, data, seller_headers, field, value):
    body = {"trip_id": data.trip_id, "seat_number": 1, "passenger_name": "Carlos Pérez", "passenger_doc": "1144556677"}
    body[field] = value
    assert client.post("/api/tickets", json=body, headers=seller_headers).status_code == 422


def test_venta_concurrente_solo_una_tiene_exito(data):
    """Semana 7: N taquilleros venden el MISMO asiento en el mismo instante → exactamente 1 éxito."""
    n = 15
    barrier = threading.Barrier(n)
    results, lock = [], threading.Lock()

    def attempt(i):
        db = SessionLocal()
        try:
            seller = db.get(User, data.seller_id)
            body = TicketIn(trip_id=data.trip_id, seat_number=5, passenger_name=f"Pasajero {chr(65 + i)}", passenger_doc=f"1000{i:04d}")
            barrier.wait()  # todos los hilos salen al mismo tiempo
            sell_endpoint(body, db, seller)
            outcome = 201
        except HTTPException as e:
            outcome = e.status_code
        finally:
            db.close()
        with lock:
            results.append(outcome)

    threads = [threading.Thread(target=attempt, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count(201) == 1
    assert results.count(409) == n - 1
    with SessionLocal() as db:
        count = db.scalar(select(func.count()).select_from(Ticket).where(Ticket.trip_id == data.trip_id, Ticket.seat_number == 5))
    assert count == 1


def test_restriccion_unique_de_la_bd_es_red_de_seguridad(data):
    """Aunque se salte la lógica del servicio, la BD impide dos tiquetes activos en el mismo asiento."""
    def ticket(uid):
        return Ticket(uuid=uid, trip_id=data.trip_id, seat_number=9, passenger_name="X Y Z", passenger_doc="11111",
                      seller_id=data.seller_id, price=15000, qr_signature=sign(uid, data.trip_id, 9))

    with SessionLocal() as db:
        db.add(ticket("11111111-1111-1111-1111-111111111111"))
        db.commit()
        db.add(ticket("22222222-2222-2222-2222-222222222222"))
        with pytest.raises(IntegrityError):
            db.commit()


def test_asiento_de_tiquete_anulado_se_puede_volver_a_vender(client, sell, admin_headers):
    first = sell(4).json()
    r = client.post(f"/api/tickets/{first['uuid']}/cancel", headers=admin_headers)
    assert r.status_code == 200 and r.json()["status"] == "cancelled"
    assert sell(4, name="Nuevo Pasajero").status_code == 201


def test_solo_se_anulan_tiquetes_vendidos(client, sell, admin_headers):
    t = sell(4).json()
    client.post("/api/tickets/verify", json={"code": t["code"]}, headers=admin_headers)  # aborda
    assert client.post(f"/api/tickets/{t['uuid']}/cancel", headers=admin_headers).status_code == 409


def test_lista_de_pasajeros_del_viaje(client, sell, data, seller_headers):
    sell(2, name="Ana Torres")
    sell(1, name="Luis Ortiz")
    r = client.get(f"/api/tickets?trip_id={data.trip_id}", headers=seller_headers).json()
    assert [t["seat_number"] for t in r] == [1, 2]
    assert r[0]["passenger_name"] == "Luis Ortiz"
