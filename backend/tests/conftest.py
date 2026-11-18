"""Configuración de pytest: base de datos aislada (bustrack_test) y datos base por prueba.

Requiere el contenedor de MySQL en ejecución (docker compose up -d).
Cada prueba arranca con las tablas vacías y un juego mínimo de datos conocido.
"""
import os

# Debe definirse ANTES de importar la aplicación: la conexión se crea al importar app.database.
os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL", "mysql+pymysql://bustrack:bustrack@127.0.0.1:3307/bustrack_test?charset=utf8mb4"
)
os.environ["QR_SECRET"] = "secreto-qr-de-pruebas"
os.environ["JWT_SECRET"] = "secreto-jwt-de-pruebas"

from datetime import date, datetime, time, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402
from types import SimpleNamespace  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Company, Route, Trip, User  # noqa: E402
from app.security import hash_password  # noqa: E402

SCHEMA = Path(__file__).resolve().parents[2] / "database" / "schema.sql"
TABLES = ("tickets", "trips", "routes", "companies", "users")
PASSWORD = "clave123"
PASSWORD_HASH = hash_password(PASSWORD)  # se calcula una sola vez (bcrypt es lento a propósito)
TOMORROW = date.today() + timedelta(days=1)


@pytest.fixture(scope="session", autouse=True)
def schema():
    """Crea las tablas de prueba a partir del mismo schema.sql de producción."""
    statements = []
    for chunk in SCHEMA.read_text(encoding="utf-8").split(";"):
        sql = "\n".join(line for line in chunk.splitlines() if not line.strip().startswith("--")).strip()
        if sql:
            statements.append(sql)
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
    with engine.begin() as conn:
        conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 0")
        for table in TABLES:
            conn.exec_driver_sql(f"TRUNCATE TABLE {table}")
        conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 1")

    with SessionLocal() as db:
        admin = User(name="Admin Pruebas", email="admin@test.co", password_hash=PASSWORD_HASH, role="admin")
        seller = User(name="Taquilla Pruebas", email="taquilla@test.co", password_hash=PASSWORD_HASH, role="taquillero")
        company = Company(name="Empresa Pruebas")
        route = Route(origin="Cali", destination="Buga", base_fare=15000, duration_minutes=75)
        db.add_all([admin, seller, company, route])
        db.flush()
        trip = Trip(route_id=route.id, company_id=company.id, bus_capacity=20, bus_plate="TST123",
                    departure_at=datetime.combine(TOMORROW, time(10, 0)))
        db.add(trip)
        db.commit()
        return SimpleNamespace(
            admin_id=admin.id, seller_id=seller.id, company_id=company.id, route_id=route.id,
            trip_id=trip.id, fare=15000.0, date=TOMORROW.isoformat(),
        )


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
def sell(client, data, seller_headers):
    """Atajo para vender un tiquete del viaje base: sell(asiento) -> respuesta HTTP."""
    def _sell(seat, name="Carlos Pérez", doc="1144556677", trip_id=None):
        body = {"trip_id": trip_id or data.trip_id, "seat_number": seat, "passenger_name": name, "passenger_doc": doc}
        return client.post("/api/tickets", json=body, headers=seller_headers)
    return _sell
