"""Reportes: viajes del día y recaudo (RF03, HU05)."""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..clock import today
from ..database import get_db
from ..models import Ticket, Trip, User
from ..security import admin_only
from ..services import day_range, trips_out

router = APIRouter(prefix="/api/reports", tags=["Reportes"])


@router.get("/daily", dependencies=[Depends(admin_only)])
def daily_report(day: date | None = Query(None, alias="date"), db: Session = Depends(get_db)):
    day = day or today()
    start, end = day_range(day)
    trips = trips_out(
        db,
        db.scalars(
            select(Trip).where(Trip.departure_at >= start, Trip.departure_at < end).order_by(Trip.departure_at)
        ).all(),
    )
    active = [t for t in trips if t.status != "cancelled"]
    capacity = sum(t.bus_capacity for t in active)
    sold = sum(t.sold for t in trips)

    by_company: dict[str, dict] = {}
    for t in trips:
        c = by_company.setdefault(t.company_name, {"company": t.company_name, "trips": 0, "tickets": 0, "revenue": 0.0})
        c["trips"] += 1
        c["tickets"] += t.sold
        c["revenue"] += t.revenue

    # Recaudo por taquillero: tiquetes activos de los viajes del día, agrupados por vendedor.
    seller_rows = db.execute(
        select(User.name, func.count(Ticket.uuid), func.coalesce(func.sum(Ticket.price), 0))
        .join(Ticket, Ticket.seller_id == User.id)
        .join(Trip, Trip.id == Ticket.trip_id)
        .where(Trip.departure_at >= start, Trip.departure_at < end, Ticket.status != "cancelled")
        .group_by(User.id, User.name)
    ).all()
    by_seller = sorted(
        ({"seller": name, "tickets": int(count), "revenue": float(total)} for name, count, total in seller_rows),
        key=lambda s: -s["revenue"],
    )

    return {
        "date": day,
        "by_seller": by_seller,
        "trips_count": len(trips),
        "tickets_sold": sold,
        "revenue": sum(t.revenue for t in trips),
        "occupancy": round(sold * 100 / capacity, 1) if capacity else 0,
        "trips": trips,
        "by_company": sorted(by_company.values(), key=lambda c: -c["revenue"]),
    }
