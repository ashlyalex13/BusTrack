"""Unitarias de app/services.py: cálculo de rangos de fecha y serialización de viajes/tiquetes."""
from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace

from app.services import day_range, ticket_out, trip_out


def make_trip(capacity=20, status="scheduled"):
    return SimpleNamespace(
        id=5, route_id=1, company_id=2, departure_at=datetime(2030, 5, 10, 14, 30), bus_capacity=capacity,
        bus_plate="ABC123", status=status,
        route=SimpleNamespace(origin="Cali", destination="Buga", base_fare=Decimal("15000.00"), duration_minutes=75),
        company=SimpleNamespace(name="Expreso Andino"),
    )


def test_day_range_cubre_el_dia_completo():
    start, end = day_range(date(2030, 5, 10))
    assert start == datetime(2030, 5, 10, 0, 0)
    assert end == datetime(2030, 5, 11, 0, 0)


def test_trip_out_calcula_disponibles_y_convierte_la_tarifa():
    out = trip_out(make_trip(capacity=20), sold=6, revenue=90000)
    assert out.available == 14
    assert out.fare == 15000.0 and isinstance(out.fare, float)
    assert (out.origin, out.destination, out.company_name) == ("Cali", "Buga", "Expreso Andino")
    assert out.revenue == 90000


def test_trip_out_nunca_reporta_disponibles_negativos():
    assert trip_out(make_trip(capacity=20), sold=25).available == 0


def test_ticket_out_arma_el_codigo_y_genera_qr_solo_si_se_pide():
    t = SimpleNamespace(
        uuid="11111111-2222-3333-4444-555555555555", qr_signature="f" * 32, trip_id=5, seat_number=3,
        passenger_name="Ana Torres", passenger_doc="1010101", price=Decimal("15000.00"), status="sold",
        created_at=datetime(2030, 5, 9, 10, 0), boarded_at=None,
        seller=SimpleNamespace(name="Laura Gómez"), trip=make_trip(),
    )
    plain = ticket_out(t)
    assert plain.code == f"{t.uuid}.{'f' * 32}"
    assert plain.qr_image is None
    assert plain.seller_name == "Laura Gómez" and plain.price == 15000.0
    assert ticket_out(t, with_qr=True).qr_image.startswith("data:image/png;base64,")
