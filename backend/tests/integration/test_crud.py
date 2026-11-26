"""RF01: ciclo completo de los CRUD del administrador (empresas, rutas, viajes y usuarios)."""
import pytest

from tests.integration.conftest import PASSWORD


# ---------------- Empresas ----------------
def test_crud_de_empresa(client, admin_headers):
    created = client.post("/api/companies", json={"name": "Nueva Empresa", "nit": "900-1", "phone": "555"},
                          headers=admin_headers)
    assert created.status_code == 201
    cid = created.json()["id"]

    updated = client.put(f"/api/companies/{cid}", json={"name": "Nueva Empresa SAS", "is_active": False},
                         headers=admin_headers).json()
    assert updated["name"] == "Nueva Empresa SAS" and updated["is_active"] is False

    names = [c["name"] for c in client.get("/api/companies", headers=admin_headers).json()]
    assert "Nueva Empresa SAS" in names

    assert client.delete(f"/api/companies/{cid}", headers=admin_headers).status_code == 204


def test_empresa_inactiva_no_recibe_viajes(client, admin_headers, data):
    client.put(f"/api/companies/{data.company_id}", json={"name": "Empresa Pruebas", "is_active": False},
               headers=admin_headers)
    body = {"route_id": data.route_id, "company_id": data.company_id, "departure_at": f"{data.date}T18:00"}
    assert client.post("/api/trips", json=body, headers=admin_headers).status_code == 422


def test_empresa_con_nombre_repetido(client, admin_headers, data):
    assert client.post("/api/companies", json={"name": "Empresa Pruebas"}, headers=admin_headers).status_code == 409


@pytest.mark.parametrize("method,url", [
    ("put", "/api/companies/99999"), ("delete", "/api/companies/99999"),
    ("put", "/api/routes/99999"), ("delete", "/api/routes/99999"),
    ("put", "/api/trips/99999"), ("delete", "/api/trips/99999"),
    ("put", "/api/users/99999"),
])
def test_registros_inexistentes_devuelven_404(client, admin_headers, data, method, url):
    bodies = {
        "companies": {"name": "X Empresa"},
        "routes": {"origin": "Cali", "destination": "Tuluá", "base_fare": 1000},
        "trips": {"route_id": data.route_id, "company_id": data.company_id, "departure_at": f"{data.date}T18:00"},
        "users": {"name": "Ana Torres", "email": "ana@test.co", "role": "taquillero"},
    }
    body = bodies[url.split("/")[2]] if method == "put" else None
    assert client.request(method.upper(), url, json=body, headers=admin_headers).status_code == 404


# ---------------- Viajes ----------------
def test_listar_y_actualizar_viajes(client, admin_headers, seller_headers, data):
    trips = client.get(f"/api/trips?date={data.date}", headers=seller_headers).json()
    assert [t["id"] for t in trips] == [data.trip_id]

    body = {"route_id": data.route_id, "company_id": data.company_id, "departure_at": f"{data.date}T11:30",
            "bus_capacity": 32, "bus_plate": "NEW999", "status": "scheduled"}
    updated = client.put(f"/api/trips/{data.trip_id}", json=body, headers=admin_headers).json()
    assert updated["bus_capacity"] == 32 and updated["bus_plate"] == "NEW999"
    assert updated["departure_at"].endswith("11:30:00")


def test_viajes_de_hoy(client, seller_headers, data):
    # El viaje base es de mañana: hoy no hay viajes.
    assert client.get("/api/trips/today", headers=seller_headers).json() == []


def test_ciudades_para_los_filtros(client, data):
    assert client.get("/api/trips/cities").json() == {"origins": ["Cali"], "destinations": ["Buga"]}


def test_grilla_de_viaje_inexistente(client, data):
    assert client.get("/api/trips/99999/seats").status_code == 404


# ---------------- Usuarios ----------------
def test_actualizar_usuario_sin_cambiar_contrasena(client, admin_headers, data):
    body = {"name": "Taquilla Renombrada", "email": "taquilla@test.co", "role": "taquillero"}
    assert client.put(f"/api/users/{data.seller_id}", json=body, headers=admin_headers).status_code == 200
    r = client.post("/api/auth/login", json={"email": "taquilla@test.co", "password": PASSWORD})
    assert r.json()["user"]["name"] == "Taquilla Renombrada"


def test_cambiar_contrasena_de_usuario(client, admin_headers, data):
    body = {"name": "Taquilla Pruebas", "email": "taquilla@test.co", "role": "taquillero", "password": "nueva-clave"}
    client.put(f"/api/users/{data.seller_id}", json=body, headers=admin_headers)
    assert client.post("/api/auth/login", json={"email": "taquilla@test.co", "password": PASSWORD}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "taquilla@test.co", "password": "nueva-clave"}).status_code == 200


def test_crear_usuario_exige_contrasena(client, admin_headers):
    body = {"name": "Sin Clave", "email": "sinclave@test.co", "role": "taquillero"}
    assert client.post("/api/users", json=body, headers=admin_headers).status_code == 422


def test_tiquete_inexistente(client, seller_headers, admin_headers, data):
    fake = "00000000-0000-0000-0000-000000000000"
    assert client.get(f"/api/tickets/{fake}", headers=seller_headers).status_code == 404
    assert client.post(f"/api/tickets/{fake}/cancel", headers=admin_headers).status_code == 404
