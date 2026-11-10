"""Funciones compartidas para serializar viajes y tiquetes."""
from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Ticket, Trip
from .qr import build_code, qr_data_url
from .schemas import TicketOut, TripOut


def day_range(d: date) -> tuple[datetime, datetime]:
    start = datetime.combine(d, time.min)
    return start, start + timedelta(days=1)


def sold_stats(db: Session, trip_ids: list[int]) -> dict[int, tuple[int, float]]:
    """{trip_id: (tiquetes activos, recaudo)}"""
    if not trip_ids:
        return {}
    rows = db.execute(
        select(Ticket.trip_id, func.count(), func.coalesce(func.sum(Ticket.price), 0))
        .where(Ticket.trip_id.in_(trip_ids), Ticket.status != "cancelled")
        .group_by(Ticket.trip_id)
    ).all()
    return {r[0]: (int(r[1]), float(r[2])) for r in rows}


def trip_out(trip: Trip, sold: int = 0, revenue: float = 0) -> TripOut:
    return TripOut(
        id=trip.id,
        route_id=trip.route_id,
        company_id=trip.company_id,
        origin=trip.route.origin,
        destination=trip.route.destination,
        company_name=trip.company.name,
        departure_at=trip.departure_at,
        duration_minutes=trip.route.duration_minutes,
        bus_capacity=trip.bus_capacity,
        bus_plate=trip.bus_plate,
        status=trip.status,
        fare=float(trip.route.base_fare),
        sold=sold,
        available=max(trip.bus_capacity - sold, 0),
        revenue=revenue,
    )


def trips_out(db: Session, trips: list[Trip]) -> list[TripOut]:
    stats = sold_stats(db, [t.id for t in trips])
    return [trip_out(t, *stats.get(t.id, (0, 0.0))) for t in trips]


def ticket_out(t: Ticket, with_qr: bool = False) -> TicketOut:
    code = build_code(t.uuid, t.qr_signature)
    return TicketOut(
        uuid=t.uuid,
        trip_id=t.trip_id,
        seat_number=t.seat_number,
        passenger_name=t.passenger_name,
        passenger_doc=t.passenger_doc,
        price=float(t.price),
        status=t.status,
        created_at=t.created_at,
        boarded_at=t.boarded_at,
        seller_name=t.seller.name,
        code=code,
        qr_image=qr_data_url(code) if with_qr else None,
        trip=trip_out(t.trip),
    )
