"""Arranque del contenedor (app/startup.py) y datos de demostración (app/seed.py)."""
from sqlalchemy import func, select

from app import startup
from app.database import SessionLocal, engine
from app.models import Ticket, Trip, User


def count(model):
    with SessionLocal() as db:
        return db.scalar(select(func.count()).select_from(model))


def empty_database():
    with engine.begin() as conn:
        for table in ("seat_holds", "tickets", "trips", "routes", "companies", "users"):
            conn.exec_driver_sql(f"DELETE FROM {table}")


def test_espera_a_la_base_de_datos_y_la_encuentra():
    startup.wait_for_db(timeout_seconds=5)  # no lanza error


def test_con_base_vacia_carga_los_datos_de_demostracion():
    empty_database()
    startup.seed_if_empty()
    assert count(User) == 3
    assert count(Trip) == 96
    assert count(Ticket) > 0


def test_con_datos_existentes_no_borra_nada(data):
    users_before = count(User)
    startup.seed_if_empty()
    assert count(User) == users_before  # no se recargó ni se borró información


def test_main_respeta_la_variable_seed_demo(monkeypatch):
    empty_database()
    monkeypatch.setenv("SEED_DEMO", "false")
    startup.main()
    assert count(User) == 0
    monkeypatch.setenv("SEED_DEMO", "true")
    startup.main()
    assert count(User) == 3
