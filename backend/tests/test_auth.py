"""RF04 / RNF03 / Semana 7: autenticación con roles y permisos (un taquillero no accede a rutas de admin)."""
import pytest

from app.database import SessionLocal
from app.models import User
from tests.conftest import PASSWORD


def test_login_correcto_devuelve_token_y_rol(client, data):
    r = client.post("/api/auth/login", json={"email": "admin@test.co", "password": PASSWORD})
    assert r.status_code == 200
    body = r.json()
    assert body["access_token"]
    assert body["user"]["role"] == "admin"
    assert "password_hash" not in body["user"]


def test_login_es_insensible_a_mayusculas_en_el_correo(client, data):
    r = client.post("/api/auth/login", json={"email": "  ADMIN@test.co ", "password": PASSWORD})
    assert r.status_code == 200


@pytest.mark.parametrize("email,password", [("admin@test.co", "incorrecta"), ("noexiste@test.co", PASSWORD)])
def test_login_con_credenciales_invalidas_es_rechazado(client, data, email, password):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 401
    assert r.json()["detail"] == "Correo o contraseña incorrectos"


def test_usuario_inactivo_no_puede_ingresar(client, data):
    with SessionLocal() as db:
        db.get(User, data.seller_id).is_active = False
        db.commit()
    r = client.post("/api/auth/login", json={"email": "taquilla@test.co", "password": PASSWORD})
    assert r.status_code == 403


def test_contrasena_se_guarda_cifrada_con_bcrypt(data):
    with SessionLocal() as db:
        stored = db.get(User, data.admin_id).password_hash
    assert stored != PASSWORD
    assert stored.startswith("$2")  # prefijo de bcrypt


def test_me_requiere_token(client, data):
    assert client.get("/api/auth/me").status_code == 401


def test_token_alterado_es_rechazado(client, admin_headers):
    token = admin_headers["Authorization"] + "x"
    assert client.get("/api/auth/me", headers={"Authorization": token}).status_code == 401


def test_me_devuelve_el_usuario_autenticado(client, seller_headers):
    r = client.get("/api/auth/me", headers=seller_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "taquilla@test.co"


ADMIN_ONLY = [
    ("get", "/api/reports/daily"),
    ("get", "/api/users"),
    ("post", "/api/routes"),
    ("post", "/api/companies"),
    ("post", "/api/trips"),
    ("delete", "/api/routes/1"),
    ("post", "/api/tickets/00000000-0000-0000-0000-000000000000/cancel"),
]


@pytest.mark.parametrize("method,url", ADMIN_ONLY)
def test_taquillero_no_accede_a_funciones_de_admin(client, seller_headers, method, url):
    r = client.request(method.upper(), url, headers=seller_headers, json={})
    assert r.status_code == 403
    assert r.json()["detail"] == "No tienes permiso para esta acción"


@pytest.mark.parametrize("method,url", ADMIN_ONLY + [("post", "/api/tickets"), ("get", "/api/tickets/verify?code=x")])
def test_sin_sesion_no_hay_acceso(client, data, method, url):
    assert client.request(method.upper(), url, json={}).status_code == 401


def test_admin_si_accede_a_reportes_y_usuarios(client, admin_headers):
    assert client.get("/api/reports/daily", headers=admin_headers).status_code == 200
    assert client.get("/api/users", headers=admin_headers).status_code == 200


def test_admin_crea_taquillero_que_luego_puede_ingresar(client, admin_headers):
    nuevo = {"name": "Nueva Taquilla", "email": "nueva@test.co", "password": "segura123", "role": "taquillero"}
    assert client.post("/api/users", json=nuevo, headers=admin_headers).status_code == 201
    r = client.post("/api/auth/login", json={"email": "nueva@test.co", "password": "segura123"})
    assert r.status_code == 200


def test_portal_publico_funciona_sin_sesion_y_no_expone_pasajeros(client, data, sell):
    assert sell(3).status_code == 201
    trips = client.get(f"/api/trips/search?date={data.date}").json()
    assert len(trips) == 1
    seats = client.get(f"/api/trips/{data.trip_id}/seats").json()
    seat3 = seats["seats"][2]
    assert seat3 == {"number": 3, "status": "sold"}  # solo número y estado, sin nombre ni documento
    assert "Carlos" not in str(trips) + str(seats)
