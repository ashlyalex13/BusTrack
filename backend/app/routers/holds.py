"""Reserva temporal de asientos (HU03, sección 5.1 de la planeación).

Mientras un taquillero registra los datos del pasajero, el asiento queda
reservado a su nombre durante SEAT_HOLD_SECONDS. Las demás taquillas lo ven
como "reservado" y no pueden venderlo. La reserva expira sola, se libera al
cambiar de asiento o de viaje y se consume al vender.

La garantía contra la doble venta sigue estando en Ticket.sell (FOR UPDATE +
UNIQUE); la reserva es una mejora de experiencia para no llenar datos en vano.
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..clock import now
from ..config import SEAT_HOLD_SECONDS
from ..database import get_db
from ..models import SeatHold, Ticket, Trip, User
from ..schemas import HoldIn, HoldOut
from ..security import staff

router = APIRouter(prefix="/api/trips", tags=["Reserva de asientos"])


def lock_trip(db: Session, trip_id: int) -> Trip:
    """Bloquea la fila del viaje: reservas y ventas del mismo viaje se procesan una a la vez."""
    trip = db.scalars(select(Trip).where(Trip.id == trip_id).with_for_update()).first()
    if not trip:
        raise HTTPException(404, "Viaje no encontrado")
    return trip


def ensure_on_sale(trip: Trip, seat_number: int) -> None:
    """Reglas comunes de reserva y venta: viaje programado, que no haya salido y asiento válido."""
    if trip.status != "scheduled":
        raise HTTPException(409, "El viaje no está disponible para la venta")
    if trip.departure_at <= now():
        raise HTTPException(409, "El viaje ya salió: no se pueden vender ni reservar asientos")
    if not 1 <= seat_number <= trip.bus_capacity:
        raise HTTPException(422, f"El asiento debe estar entre 1 y {trip.bus_capacity}")


def purge_expired(db: Session, trip_id: int) -> None:
    db.execute(delete(SeatHold).where(SeatHold.trip_id == trip_id, SeatHold.expires_at <= now()))


def active_hold(db: Session, trip_id: int, seat_number: int) -> SeatHold | None:
    hold = db.get(SeatHold, (trip_id, seat_number))
    return hold if hold and hold.expires_at > now() else None


@router.post("/{trip_id}/holds", response_model=HoldOut)
def hold_seat(trip_id: int, data: HoldIn, db: Session = Depends(get_db), user: User = Depends(staff)):
    trip = lock_trip(db, trip_id)
    seat = data.seat_number
    ensure_on_sale(trip, seat)

    purge_expired(db, trip_id)
    sold = db.scalar(
        select(Ticket.uuid).where(Ticket.trip_id == trip_id, Ticket.seat_number == seat, Ticket.status != "cancelled")
    )
    if sold:
        raise HTTPException(409, f"El asiento {seat} ya fue vendido")
    existing = db.get(SeatHold, (trip_id, seat))
    if existing and existing.user_id != user.id:
        raise HTTPException(409, f"El asiento {seat} está reservado por otra taquilla")

    # Un taquillero tiene como máximo un asiento reservado por viaje.
    db.execute(delete(SeatHold).where(
        SeatHold.trip_id == trip_id, SeatHold.user_id == user.id, SeatHold.seat_number != seat
    ))
    expires_at = now() + timedelta(seconds=SEAT_HOLD_SECONDS)
    if existing:
        existing.expires_at = expires_at
    else:
        db.add(SeatHold(trip_id=trip_id, seat_number=seat, user_id=user.id, expires_at=expires_at))
    db.commit()
    return HoldOut(trip_id=trip_id, seat_number=seat, expires_in=SEAT_HOLD_SECONDS)


@router.delete("/{trip_id}/holds/{seat_number}", status_code=204)
def release_seat(trip_id: int, seat_number: int, db: Session = Depends(get_db), user: User = Depends(staff)):
    db.execute(delete(SeatHold).where(
        SeatHold.trip_id == trip_id, SeatHold.seat_number == seat_number, SeatHold.user_id == user.id
    ))
    db.commit()
