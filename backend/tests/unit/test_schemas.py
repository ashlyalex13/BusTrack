"""Unitarias de app/schemas.py: reglas de validación de los datos que entran a la API."""
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas import RouteIn, TicketIn, TripIn, UserIn


# ---------- Rutas (HU02) ----------
def test_ruta_valida_y_limpia_espacios():
    r = RouteIn(origin="  Cali ", destination=" Buga  ", base_fare=15000)
    assert (r.origin, r.destination, r.duration_minutes) == ("Cali", "Buga", 60)


@pytest.mark.parametrize("data", [
    {"origin": "Cali", "destination": "CALI", "base_fare": 1000},   # mismo origen y destino
    {"origin": "Cali", "destination": "Buga", "base_fare": 0},      # tarifa no positiva
    {"origin": "Cali", "destination": "Buga", "base_fare": 1000, "duration_minutes": 0},
    {"origin": "C", "destination": "Buga", "base_fare": 1000},      # nombre muy corto
])
def test_ruta_invalida(data):
    with pytest.raises(ValidationError):
        RouteIn(**data)


# ---------- Tiquetes ----------
def ticket(**kw):
    data = {"trip_id": 1, "seat_number": 1, "passenger_name": "Ana Torres", "passenger_doc": "1010101"} | kw
    return TicketIn(**data)


def test_nombre_y_documento_se_normalizan():
    t = ticket(passenger_name="  José   Ñúñez ", passenger_doc=" ab-12345 ")
    assert t.passenger_name == "José Ñúñez"
    assert t.passenger_doc == "AB-12345"


@pytest.mark.parametrize("name", ["Ana2", "<b>Ana</b>", "...", "A"])
def test_nombre_invalido(name):
    with pytest.raises(ValidationError, match="nombre|at least"):
        ticket(passenger_name=name)


@pytest.mark.parametrize("doc", ["123", "12 345", "12345$", "1" * 21])
def test_documento_invalido(doc):
    with pytest.raises(ValidationError):
        ticket(passenger_doc=doc)


# ---------- Viajes ----------
@pytest.mark.parametrize("capacity", [3, 81])
def test_capacidad_del_bus_entre_4_y_80(capacity):
    with pytest.raises(ValidationError):
        TripIn(route_id=1, company_id=1, departure_at=datetime(2030, 1, 1, 8), bus_capacity=capacity)


def test_estado_de_viaje_desconocido():
    with pytest.raises(ValidationError):
        TripIn(route_id=1, company_id=1, departure_at=datetime(2030, 1, 1, 8), status="volando")


# ---------- Usuarios ----------
@pytest.mark.parametrize("email", ["sin-arroba", "a@b", "con espacio@x.co"])
def test_correo_invalido(email):
    with pytest.raises(ValidationError):
        UserIn(name="Ana Torres", email=email, password="clave123", role="taquillero")


def test_rol_inexistente():
    with pytest.raises(ValidationError):
        UserIn(name="Ana Torres", email="ana@x.co", password="clave123", role="superusuario")
