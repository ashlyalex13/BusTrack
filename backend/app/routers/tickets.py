"""Venta con control de concurrencia y verificación de QR (RF06, RF07, RF10, RNF01)."""
import hmac
import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..clock import now, today
from ..database import get_db
from ..models import Ticket, User
from ..qr import sign
from .holds import active_hold, ensure_on_sale, lock_trip
from ..schemas import TicketIn, TicketOut, VerifyIn, VerifyOut
from ..security import admin_only, staff
from ..services import day_range, ticket_out

router = APIRouter(prefix="/api/tickets", tags=["Tiquetes"])


@router.post("", response_model=TicketOut, status_code=201)
def sell(data: TicketIn, db: Session = Depends(get_db), user: User = Depends(staff)):
    """Ticket.sell(): 201 con el tiquete o 409 si el asiento ya está ocupado.

    1. Bloquea la fila del viaje (SELECT ... FOR UPDATE): las ventas del mismo
       viaje se serializan; la segunda espera a que la primera confirme.
    2. Vuelve a comprobar el asiento con una lectura bloqueante.
    3. UNIQUE(trip_id, active_seat) en la BD es la red de seguridad final.
    """
    trip = lock_trip(db, data.trip_id)
    ensure_on_sale(trip, data.seat_number)

    taken = db.scalars(
        select(Ticket.uuid)
        .where(Ticket.trip_id == trip.id, Ticket.seat_number == data.seat_number, Ticket.status != "cancelled")
        .with_for_update()
    ).first()
    if taken:
        raise HTTPException(409, f"El asiento {data.seat_number} ya fue vendido")
    hold = active_hold(db, trip.id, data.seat_number)
    if hold and hold.user_id != user.id:
        raise HTTPException(409, f"El asiento {data.seat_number} está reservado por otra taquilla")

    ticket_uuid = str(uuid.uuid4())
    ticket = Ticket(
        uuid=ticket_uuid,
        trip_id=trip.id,
        seat_number=data.seat_number,
        passenger_name=data.passenger_name.strip(),
        passenger_doc=data.passenger_doc.strip(),
        seller_id=user.id,
        price=trip.route.base_fare,
        qr_signature=sign(ticket_uuid, trip.id, data.seat_number),
        status="sold",
    )
    db.add(ticket)
    if hold:
        db.delete(hold)  # la reserva se consume con la venta
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, f"El asiento {data.seat_number} ya fue vendido")
    db.refresh(ticket)
    return ticket_out(ticket, with_qr=True)


@router.get("", response_model=list[TicketOut], dependencies=[Depends(staff)])
def list_tickets(
    trip_id: int | None = None,
    day: date | None = Query(None, alias="date"),
    db: Session = Depends(get_db),
):
    q = select(Ticket)
    if trip_id:
        q = q.where(Ticket.trip_id == trip_id)
    else:
        start, end = day_range(day or today())
        q = q.where(Ticket.created_at >= start, Ticket.created_at < end)
    return [ticket_out(t) for t in db.scalars(q.order_by(Ticket.seat_number)).all()]


@router.get("/search", response_model=list[TicketOut], dependencies=[Depends(staff)])
def search_tickets(q: str = Query(..., min_length=3, description="Documento o parte del nombre del pasajero"),
                   db: Session = Depends(get_db)):
    """Busca tiquetes por documento exacto o por nombre (para reimprimir, anular o atender reclamos)."""
    term = q.strip()
    query = (
        select(Ticket)
        .where(or_(Ticket.passenger_doc == term, Ticket.passenger_name.ilike(f"%{term}%")))
        .order_by(Ticket.created_at.desc())
        .limit(50)
    )
    return [ticket_out(t) for t in db.scalars(query).all()]


@router.get("/verify", response_model=VerifyOut, dependencies=[Depends(staff)])
def verify(code: str, db: Session = Depends(get_db)):
    """Ticket.verify(code): solo consulta, no marca abordaje."""
    return _verify(db, code, board=False)


@router.post("/verify", response_model=VerifyOut, dependencies=[Depends(staff)])
def verify_and_board(data: VerifyIn, db: Session = Depends(get_db)):
    """Valida el QR y marca el tiquete como 'abordado' (un solo uso)."""
    return _verify(db, data.code, board=True)


@router.get("/{ticket_uuid}", response_model=TicketOut, dependencies=[Depends(staff)])
def get_ticket(ticket_uuid: str, db: Session = Depends(get_db)):
    t = db.get(Ticket, ticket_uuid)
    if not t:
        raise HTTPException(404, "Tiquete no encontrado")
    return ticket_out(t, with_qr=True)


@router.post("/{ticket_uuid}/cancel", response_model=TicketOut, dependencies=[Depends(admin_only)])
def cancel_ticket(ticket_uuid: str, db: Session = Depends(get_db)):
    t = db.get(Ticket, ticket_uuid)
    if not t:
        raise HTTPException(404, "Tiquete no encontrado")
    if t.status != "sold":
        raise HTTPException(409, "Solo se pueden anular tiquetes vendidos que no hayan abordado")
    t.status = "cancelled"
    db.commit()
    return ticket_out(t)


def _verify(db: Session, code: str, board: bool) -> VerifyOut:
    code = code.strip()
    if "." not in code:
        return VerifyOut(valid=False, message="Formato de código inválido")
    ticket_uuid, signature = code.split(".", 1)
    q = select(Ticket).where(Ticket.uuid == ticket_uuid)
    t = db.scalars(q.with_for_update() if board else q).first()
    if not t:
        return VerifyOut(valid=False, message="El tiquete no existe")
    expected = sign(t.uuid, t.trip_id, t.seat_number)
    if not hmac.compare_digest(expected, signature) or not hmac.compare_digest(expected, t.qr_signature):
        return VerifyOut(valid=False, message="Firma inválida: el código fue alterado")
    if t.status == "cancelled":
        return VerifyOut(valid=False, message="El tiquete fue anulado", ticket=ticket_out(t))
    if t.status == "boarded":
        when = t.boarded_at.strftime("%d/%m/%Y %H:%M") if t.boarded_at else ""
        return VerifyOut(valid=False, message=f"El tiquete ya fue usado ({when})", ticket=ticket_out(t))
    if board:
        t.status, t.boarded_at = "boarded", now()
        db.commit()
        return VerifyOut(valid=True, message="Abordaje registrado correctamente", ticket=ticket_out(t))
    return VerifyOut(valid=True, message="Tiquete válido", ticket=ticket_out(t))
