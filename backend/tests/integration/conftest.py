"""Pruebas de integración: API + base de datos MySQL aislada (bustrack_test).

Requiere MySQL en ejecución (docker compose up -d db).
Cada prueba arranca con las tablas vacías y un juego mínimo de datos conocido.
"""
from datetime import datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.clock import today
from app.database import SessionLocal, engine
from app.main import app
from app.models import Company, Route, Trip, User
from app.security import hash_password

# bustrack/database/schema.sql (en Docker: /database/schema.sql, montado en el contenedor)
SCHEMA = Path(__file__).resolve().parents[3] / "database" / "schema.sql"
TABLES = ("seat_holds", "tickets", "trips", "routes", "companies", "users")
PASSWORD = "clave123"
PASSWORD_HASH = hash_password(PASSWORD)  # se calcula una sola vez (bcrypt es lento a propósito)
TOMORROW = today() + timedelta(days=1)  # hora de la terminal, no la del servidor


@pytest.fixture(scope="session", autouse=True)
def schema():
    """Crea las tablas de prueba a partir del mismo schema.sql de producción."""
    lines = [line for line in SCHEMA.read_text(encoding="utf-8").splitlines() if not line.strip().startswith("--")]
    statements = [s.strip() for s in "\n".join(lines).split(";") if s.strip()]
    with engine.begin() as conn:
        conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 0")
        for table in TABLES:
            conn.exec_driver_sql(f"DROP TABLE IF EXISTS {table}")
        conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 1")
        for sql in statements:
            conn.exec_driver_sql(sql)


@pytest.fixture
def data():
    """Datos base: 1 admin, 1 taquillero, 1 empresa, 1 ruta y 1 viaje de 20 asientos para mañana."""
    with engine.begin() as conn:  # DELETE es mucho más rápido que TRUNCATE en tablas pequeñas
        for table in TABLES:
            conn.exec_driver_sql(f"DELETE FROM {table}")

    with SessionLocal() as db:
        admin = User(name="Admin Pruebas", email="admin@test.co", password_hash=PASSWORD_HASH, role="admin")
        seller = User(name="Taquilla Pruebas", email="taquilla@test.co", password_hash=PASSWORD_HASH, role="taquillero")
        seller2 = User(name="Taquilla Dos", email="taquilla2@test.co", password_hash=PASSWORD_HASH, role="taquillero")
        company = Company(name="Empresa Pruebas")
        route = Route(origin="Cali", destination="Buga", base_fare=15000, duration_minutes=75)
        db.add_all([admin, seller, seller2, company, route])
        db.flush()
        trip = Trip(route_id=route.id, company_id=company.id, bus_capacity=20, bus_plate="TST123",
                    departure_at=datetime.combine(TOMORROW, time(10, 0)))
        db.add(trip)
        db.commit()
        return SimpleNamespace(
            admin_id=admin.id, seller_id=seller.id, company_id=company.id, route_id=route.id,
            trip_id=trip.id, fare=15000.0, date=TOMORROW.isoformat(),
        )


@pytest.fixture(autouse=True)
def reset_login_limiter():
    """Cada prueba arranca sin intentos fallidos acumulados."""
    from app.rate_limit import login_limiter
    login_limiter.reset()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def login(client, email):
    r = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def admin_headers(client, data):
    return login(client, "admin@test.co")


@pytest.fixture
def seller_headers(client, data):
    return login(client, "taquilla@test.co")


@pytest.fixture
def seller2_headers(client, data):
    return login(client, "taquilla2@test.co")


@pytest.fixture
def sell(client, data, seller_headers):
    """Atajo para vender un tiquete del viaje base: sell(asiento) -> respuesta HTTP."""
    def _sell(seat, name="Carlos Pérez", doc="1144556677", trip_id=None):
        body = {"trip_id": trip_id or data.trip_id, "seat_number": seat, "passenger_name": name, "passenger_doc": doc}
        return client.post("/api/tickets", json=body, headers=seller_headers)
    return _sell
