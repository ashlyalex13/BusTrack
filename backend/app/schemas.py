from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Auth / usuarios ----------
class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(ORM):
    id: int
    name: str
    email: str
    role: str
    is_active: bool


class UserIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: Optional[str] = Field(None, min_length=6)
    role: Literal["admin", "taquillero"]
    is_active: bool = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Empresas y rutas ----------
class CompanyIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    nit: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True


class CompanyOut(CompanyIn, ORM):
    id: int


class RouteIn(BaseModel):
    origin: str = Field(min_length=2, max_length=80)
    destination: str = Field(min_length=2, max_length=80)
    base_fare: float = Field(gt=0, description="Tarifa en COP, debe ser mayor a 0")
    duration_minutes: int = Field(60, gt=0)

    @model_validator(mode="after")
    def check_cities(self):
        self.origin, self.destination = self.origin.strip(), self.destination.strip()
        if self.origin.lower() == self.destination.lower():
            raise ValueError("El origen debe ser distinto del destino")
        return self


class RouteOut(RouteIn, ORM):
    id: int


# ---------- Viajes ----------
class TripIn(BaseModel):
    route_id: int
    company_id: int
    departure_at: datetime
    bus_capacity: int = Field(40, ge=4, le=80)
    bus_plate: Optional[str] = Field(None, max_length=10)
    status: Literal["scheduled", "departed", "cancelled"] = "scheduled"


class TripOut(BaseModel):
    id: int
    route_id: int
    company_id: int
    origin: str
    destination: str
    company_name: str
    departure_at: datetime
    duration_minutes: int
    bus_capacity: int
    bus_plate: Optional[str]
    status: str
    fare: float
    sold: int = 0
    available: int = 0
    revenue: float = 0


class SeatOut(BaseModel):
    number: int
    status: Literal["free", "reserved", "sold", "boarded"]


class HoldIn(BaseModel):
    seat_number: int


class HoldOut(BaseModel):
    trip_id: int
    seat_number: int
    expires_in: int  # segundos restantes (evita depender del reloj del navegador)


class SeatsOut(BaseModel):
    trip: TripOut
    seats: list[SeatOut]


# ---------- Tiquetes ----------
class TicketIn(BaseModel):
    trip_id: int
    seat_number: int
    passenger_name: str = Field(min_length=3, max_length=120)
    passenger_doc: str = Field(min_length=5, max_length=30)


class TicketOut(BaseModel):
    uuid: str
    trip_id: int
    seat_number: int
    passenger_name: str
    passenger_doc: str
    price: float
    status: str
    created_at: datetime
    boarded_at: Optional[datetime]
    seller_name: str
    code: str
    qr_image: Optional[str] = None
    trip: TripOut


class VerifyIn(BaseModel):
    code: str


class VerifyOut(BaseModel):
    valid: bool
    message: str
    ticket: Optional[TicketOut] = None
