"""Entidades del sistema. El schema real vive en database/schema.sql."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .clock import now
from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))  # admin | taquillero
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    nit: Mapped[Optional[str]] = mapped_column(String(30))
    phone: Mapped[Optional[str]] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Route(Base):
    __tablename__ = "routes"
    id: Mapped[int] = mapped_column(primary_key=True)
    origin: Mapped[str] = mapped_column(String(80))
    destination: Mapped[str] = mapped_column(String(80))
    base_fare: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Trip(Base):
    __tablename__ = "trips"
    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    departure_at: Mapped[datetime] = mapped_column(DateTime)
    bus_capacity: Mapped[int] = mapped_column(Integer, default=40)
    bus_plate: Mapped[Optional[str]] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    route: Mapped[Route] = relationship()
    company: Mapped[Company] = relationship()


class Ticket(Base):
    __tablename__ = "tickets"
    uuid: Mapped[str] = mapped_column(String(36), primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"))
    seat_number: Mapped[int] = mapped_column(Integer)
    passenger_name: Mapped[str] = mapped_column(String(120))
    passenger_doc: Mapped[str] = mapped_column(String(30))
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    qr_signature: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="sold")  # sold | boarded | cancelled
    # Hora de la terminal (no la del servidor de BD, que en la nube puede estar en UTC).
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, server_default=func.now())
    boarded_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    trip: Mapped[Trip] = relationship()
    seller: Mapped[User] = relationship()


class SeatHold(Base):
    """Reserva temporal de un asiento por un taquillero (HU03)."""
    __tablename__ = "seat_holds"
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), primary_key=True)
    seat_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
