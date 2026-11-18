"""Carga datos de demostración. Uso: python -m app.seed  (borra los datos existentes)."""
import random
import uuid
from datetime import date, datetime, time, timedelta

from sqlalchemy import text

from .database import SessionLocal
from .models import Company, Route, Ticket, Trip, User
from .qr import sign
from .security import hash_password

USERS = [
    ("Administrador BusTrack", "admin@bustrack.co", "admin123", "admin"),
    ("Laura Gómez", "taquilla1@bustrack.co", "taquilla123", "taquillero"),
    ("Andrés Ríos", "taquilla2@bustrack.co", "taquilla123", "taquillero"),
]
COMPANIES = [
    ("Transportes del Valle", "900111222-1", "602 555 0101"),
    ("Expreso Andino", "900333444-2", "602 555 0202"),
    ("Rápido Pacífico", "900555666-3", "602 555 0303"),
]
ROUTES = [  # origen, destino, tarifa, minutos
    ("Cali", "Bogotá", 85000, 600),
    ("Cali", "Medellín", 78000, 540),
    ("Cali", "Popayán", 35000, 180),
    ("Cali", "Buga", 15000, 75),
    ("Cali", "Armenia", 32000, 210),
    ("Cali", "Pasto", 70000, 540),
    ("Bogotá", "Cali", 85000, 600),
    ("Buga", "Cali", 15000, 75),
]
NAMES = ["Carlos Pérez", "María López", "Juan Martínez", "Ana Torres", "Pedro Castro", "Sofía Ramírez",
         "Diego Herrera", "Valentina Ruiz", "Andrés Mora", "Camila Vargas", "Luis Ortiz", "Paula Rojas"]


def run():
    random.seed(7)
    db = SessionLocal()
    db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    for table in ("seat_holds", "tickets", "trips", "routes", "companies", "users"):
        db.execute(text(f"TRUNCATE TABLE {table}"))
    db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

    users = [User(name=n, email=e, password_hash=hash_password(p), role=r) for n, e, p, r in USERS]
    companies = [Company(name=n, nit=nit, phone=ph) for n, nit, ph in COMPANIES]
    routes = [Route(origin=o, destination=d, base_fare=f, duration_minutes=m) for o, d, f, m in ROUTES]
    db.add_all(users + companies + routes)
    db.flush()

    hours = [5, 7, 9, 11, 13, 15, 17, 19, 21]
    trips = []
    for offset in range(-1, 3):  # ayer, hoy y dos días más
        day = date.today() + timedelta(days=offset)
        for i, route in enumerate(routes):
            for j, h in enumerate(random.sample(hours, 3)):
                trips.append(Trip(
                    route_id=route.id,
                    company_id=companies[(i + j) % len(companies)].id,
                    departure_at=datetime.combine(day, time(h, random.choice([0, 15, 30, 45]))),
                    bus_capacity=random.choice([20, 32, 40]),
                    bus_plate=f"{random.choice(['VCK', 'SXT', 'WMN', 'TPQ'])}{random.randint(100, 999)}",
                    status="departed" if offset < 0 else "scheduled",
                ))
    db.add_all(trips)
    db.flush()

    route_by_id = {r.id: r for r in routes}
    for trip in trips:
        days_from_today = (trip.departure_at.date() - date.today()).days
        ratio = {-1: 0.8, 0: 0.45, 1: 0.2}.get(days_from_today, 0.05)
        for seat in random.sample(range(1, trip.bus_capacity + 1), int(trip.bus_capacity * ratio)):
            uid = str(uuid.uuid4())
            db.add(Ticket(
                uuid=uid, trip_id=trip.id, seat_number=seat,
                passenger_name=random.choice(NAMES), passenger_doc=str(random.randint(10_000_000, 1_199_999_999)),
                seller_id=random.choice(users[1:]).id, price=route_by_id[trip.route_id].base_fare,
                qr_signature=sign(uid, trip.id, seat), status="boarded" if days_from_today < 0 else "sold",
            ))
    db.commit()
    print(f"Datos cargados: {len(users)} usuarios, {len(companies)} empresas, {len(routes)} rutas, {len(trips)} viajes.")
    for n, e, p, r in USERS:
        print(f"  {r:<11} {e} / {p}")


if __name__ == "__main__":
    run()
