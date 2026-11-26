"""Viajes: búsqueda pública, viajes del día, grilla de asientos y CRUD (RF01, RF05, RF09)."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from ..clock import now, today
from ..database import get_db
from ..models import Company, Route, SeatHold, Ticket, Trip
from ..schemas import SeatOut, SeatsOut, TripIn, TripOut
from ..security import admin_only, staff
from ..services import day_range, sold_stats, trip_out, trips_out

router = APIRouter(prefix="/api/trips", tags=["Viajes"])


@router.get("/cities")
def cities(db: Session = Depends(get_db)):
    """Público: ciudades disponibles para los filtros de búsqueda."""
    return {
        "origins": db.scalars(select(Route.origin).distinct().order_by(Route.origin)).all(),
        "destinations": db.scalars(select(Route.destination).distinct().order_by(Route.destination)).all(),
    }


@router.get("/search", response_model=list[TripOut])
def search_available(
    origin: str | None = None,
    destination: str | None = None,
    day: date | None = Query(None, alias="date"),
    db: Session = Depends(get_db),
):
    """Trip.searchAvailable(origin, destination, date) — público, sin datos de pasajeros."""
    day = day or today()
    start, end = day_range(day)
    if day == today():
        start = max(start, now())  # solo viajes que aún no han salido
    q = (
        select(Trip).join(Route).join(Company)
        .where(Trip.departure_at >= start, Trip.departure_at < end, Trip.status == "scheduled")
    )
    if origin:
        q = q.where(Route.origin == origin)
    if destination:
        q = q.where(Route.destination == destination)
    return trips_out(db, db.scalars(q.order_by(Trip.departure_at)).all())


@router.get("/today", response_model=list[TripOut], dependencies=[Depends(staff)])
def today_trips(db: Session = Depends(get_db)):
    """Trip.getTodayTrips()"""
    return list_trips(today(), db)


@router.get("", response_model=list[TripOut], dependencies=[Depends(staff)])
def list_trips(day: date | None = Query(None, alias="date"), db: Session = Depends(get_db)):
    start, end = day_range(day or today())
    trips = db.scalars(
        select(Trip).where(Trip.departure_at >= start, Trip.departure_at < end).order_by(Trip.departure_at)
    ).all()
    return trips_out(db, trips)


@router.get("/{trip_id}/seats", response_model=SeatsOut)
def get_seats(trip_id: int, db: Session = Depends(get_db)):
    """Trip.getSeats(tripId) — estado de cada asiento en tiempo real."""
    trip = _get_trip(db, trip_id)
    taken = dict(
        db.execute(
            select(Ticket.seat_number, Ticket.status)
            .where(Ticket.trip_id == trip_id, Ticket.status != "cancelled")
        ).all()
    )
    held = set(db.scalars(
        select(SeatHold.seat_number).where(SeatHold.trip_id == trip_id, SeatHold.expires_at > now())
    ).all())
    seats = [
        SeatOut(number=n, status=taken.get(n) or ("reserved" if n in held else "free"))
        for n in range(1, trip.bus_capacity + 1)
    ]
    return SeatsOut(trip=trip_out(trip, len(taken), 0), seats=seats)


@router.post("", response_model=TripOut, status_code=201, dependencies=[Depends(admin_only)])
def create_trip(data: TripIn, db: Session = Depends(get_db)):
    if data.departure_at <= now():
        raise HTTPException(422, "La fecha y hora de salida deben ser posteriores al momento actual")
    _check_refs(db, data)
    trip = Trip(**data.model_dump())
    db.add(trip)
    db.commit()
    return trip_out(trip)


@router.put("/{trip_id}", response_model=TripOut, dependencies=[Depends(admin_only)])
def update_trip(trip_id: int, data: TripIn, db: Session = Depends(get_db)):
    trip = _get_trip(db, trip_id)
    _check_refs(db, data)
    max_seat = db.scalar(
        select(func.max(Ticket.seat_number)).where(Ticket.trip_id == trip_id, Ticket.status != "cancelled")
    )
    if max_seat and data.bus_capacity < max_seat:
        raise HTTPException(409, f"Ya hay tiquetes vendidos hasta el asiento {max_seat}")
    for k, v in data.model_dump().items():
        setattr(trip, k, v)
    db.commit()
    db.refresh(trip)
    sold, revenue = sold_stats(db, [trip.id]).get(trip.id, (0, 0.0))
    return trip_out(trip, sold, revenue)


@router.delete("/{trip_id}", status_code=204, dependencies=[Depends(admin_only)])
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = _get_trip(db, trip_id)
    if db.scalar(select(exists().where(Ticket.trip_id == trip_id))):
        raise HTTPException(409, "El viaje tiene tiquetes vendidos: cámbialo a 'Cancelado' en lugar de eliminarlo")
    db.delete(trip)
    db.commit()


def _get_trip(db: Session, trip_id: int) -> Trip:
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(404, "Viaje no encontrado")
    return trip


def _check_refs(db: Session, data: TripIn):
    if not db.get(Route, data.route_id):
        raise HTTPException(422, "La ruta no existe")
    company = db.get(Company, data.company_id)
    if not company or not company.is_active:
        raise HTTPException(422, "La empresa no existe o está inactiva")
