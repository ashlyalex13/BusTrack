"""HU02 (rutas y tarifas), RF01 (viajes) y HU05 (reportes: el recaudo coincide con la suma de tiquetes)."""
import time

import pytest


# ---------------- HU02: rutas y tarifas ----------------
def test_crear_ruta_valida(client, admin_headers):
    r = client.post("/api/routes", json={"origin": "Cali", "destination": "Tuluá", "base_fare": 22000, "duration_minutes": 120},
                    headers=admin_headers)
    assert r.status_code == 201
    assert r.json()["base_fare"] == 22000


@pytest.mark.parametrize("body", [
    {"origin": "Cali", "destination": "cali", "base_fare": 10000},    # origen = destino
    {"origin": "Cali", "destination": "Palmira", "base_fare": 0},     # tarifa no positiva
    {"origin": "Cali", "destination": "Palmira", "base_fare": -500},
    {"origin": "", "destination": "Palmira", "base_fare": 10000},
])
def test_validaciones_de_ruta(client, admin_headers, body):
    assert client.post("/api/routes", json=body, headers=admin_headers).status_code == 422


def test_ruta_duplicada_es_rechazada(client, admin_headers):
    r = client.post("/api/routes", json={"origin": "Cali", "destination": "Buga", "base_fare": 9000}, headers=admin_headers)
    assert r.status_code == 409


def test_no_se_elimina_ruta_con_viajes_programados(client, admin_headers, data):
    r = client.delete(f"/api/routes/{data.route_id}", headers=admin_headers)
    assert r.status_code == 409
    assert "viajes programados" in r.json()["detail"]


def test_ruta_sin_viajes_si_se_elimina(client, admin_headers):
    rid = client.post("/api/routes", json={"origin": "Buga", "destination": "Tuluá", "base_fare": 8000},
                      headers=admin_headers).json()["id"]
    assert client.delete(f"/api/routes/{rid}", headers=admin_headers).status_code == 204


def test_cambio_de_tarifa_aplica_a_nuevas_ventas(client, admin_headers, data, sell):
    client.put(f"/api/routes/{data.route_id}", headers=admin_headers,
               json={"origin": "Cali", "destination": "Buga", "base_fare": 18000, "duration_minutes": 75})
    assert sell(1).json()["price"] == 18000


# ---------------- RF01: empresas y viajes ----------------
def test_no_se_elimina_empresa_con_viajes(client, admin_headers, data):
    assert client.delete(f"/api/companies/{data.company_id}", headers=admin_headers).status_code == 409


def test_programar_viaje(client, admin_headers, data):
    body = {"route_id": data.route_id, "company_id": data.company_id, "departure_at": f"{data.date}T15:30",
            "bus_capacity": 32, "bus_plate": "ABC123"}
    r = client.post("/api/trips", json=body, headers=admin_headers)
    assert r.status_code == 201
    assert r.json()["available"] == 32


def test_viaje_con_ruta_inexistente(client, admin_headers, data):
    body = {"route_id": 99999, "company_id": data.company_id, "departure_at": f"{data.date}T15:30"}
    assert client.post("/api/trips", json=body, headers=admin_headers).status_code == 422


def test_no_se_reduce_capacidad_por_debajo_de_asientos_vendidos(client, admin_headers, data, sell):
    sell(18)
    body = {"route_id": data.route_id, "company_id": data.company_id, "departure_at": f"{data.date}T10:00", "bus_capacity": 10}
    assert client.put(f"/api/trips/{data.trip_id}", json=body, headers=admin_headers).status_code == 409


def test_no_se_elimina_viaje_con_tiquetes(client, admin_headers, data, sell):
    sell(1)
    assert client.delete(f"/api/trips/{data.trip_id}", headers=admin_headers).status_code == 409


# ---------------- HU05: reportes ----------------
def test_recaudo_coincide_con_la_suma_de_tiquetes(client, admin_headers, data, sell):
    tickets = [sell(s).json() for s in (1, 2, 3, 4)]
    client.post(f"/api/tickets/{tickets[0]['uuid']}/cancel", headers=admin_headers)  # anulado: no suma
    client.post("/api/tickets/verify", json={"code": tickets[1]["code"]}, headers=admin_headers)  # abordado: sí suma

    report = client.get(f"/api/reports/daily?date={data.date}", headers=admin_headers).json()
    assert report["tickets_sold"] == 3
    assert report["revenue"] == 3 * data.fare
    assert report["trips_count"] == 1
    assert report["occupancy"] == 15.0  # 3 de 20 asientos
    assert report["by_company"][0]["revenue"] == 3 * data.fare


def test_recaudo_por_taquillero(client, admin_headers, data, sell, seller2_headers):
    sell(1)
    sell(2)
    body = {"trip_id": data.trip_id, "seat_number": 3, "passenger_name": "Otra Persona", "passenger_doc": "99887766"}
    client.post("/api/tickets", json=body, headers=seller2_headers)

    by_seller = client.get(f"/api/reports/daily?date={data.date}", headers=admin_headers).json()["by_seller"]
    assert by_seller == [
        {"seller": "Taquilla Pruebas", "tickets": 2, "revenue": 2 * data.fare},
        {"seller": "Taquilla Dos", "tickets": 1, "revenue": data.fare},
    ]


def test_reporte_filtra_por_fecha(client, admin_headers, data, sell):
    sell(1)
    report = client.get("/api/reports/daily?date=2020-01-01", headers=admin_headers).json()
    assert report["trips_count"] == 0 and report["revenue"] == 0


# ---------------- RNF04: rendimiento ----------------
def test_busqueda_y_grilla_responden_en_menos_de_2_segundos(client, data):
    for url in (f"/api/trips/search?date={data.date}", f"/api/trips/{data.trip_id}/seats"):
        start = time.perf_counter()
        assert client.get(url).status_code == 200
        assert time.perf_counter() - start < 2
