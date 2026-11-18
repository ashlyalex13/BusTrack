"""Gestión de tiquetes: búsqueda de pasajero y anulación (solo administrador)."""


def search(client, headers, q):
    return client.get("/api/tickets/search", params={"q": q}, headers=headers)


def test_buscar_por_documento_exacto(client, sell, seller_headers):
    sell(1, name="Ana Torres", doc="1010101010")
    sell(2, name="Luis Ortiz", doc="2020202020")
    r = search(client, seller_headers, "1010101010").json()
    assert [t["passenger_name"] for t in r] == ["Ana Torres"]


def test_buscar_por_parte_del_nombre_sin_importar_mayusculas(client, sell, seller_headers):
    sell(1, name="Ana Torres", doc="1010101010")
    sell(2, name="Mariana López", doc="2020202020")
    names = {t["passenger_name"] for t in search(client, seller_headers, "ana").json()}
    assert names == {"Ana Torres", "Mariana López"}


def test_busqueda_sin_resultados(client, sell, seller_headers):
    sell(1)
    assert search(client, seller_headers, "9999999999").json() == []


def test_busqueda_requiere_al_menos_3_caracteres_y_sesion(client, data, seller_headers):
    assert search(client, seller_headers, "ab").status_code == 422
    assert client.get("/api/tickets/search", params={"q": "abc"}).status_code == 401


def test_admin_anula_tiquete_y_el_asiento_queda_libre(client, sell, data, admin_headers):
    t = sell(6).json()
    r = client.post(f"/api/tickets/{t['uuid']}/cancel", headers=admin_headers)
    assert r.json()["status"] == "cancelled"
    seats = client.get(f"/api/trips/{data.trip_id}/seats").json()["seats"]
    assert seats[5]["status"] == "free"


def test_taquillero_no_puede_anular(client, sell, seller_headers):
    t = sell(6).json()
    assert client.post(f"/api/tickets/{t['uuid']}/cancel", headers=seller_headers).status_code == 403
