"""CRUD de empresas y rutas con tarifa (RF01, RF02, HU02)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Company, Route, Trip
from ..schemas import CompanyIn, CompanyOut, RouteIn, RouteOut
from ..security import admin_only, staff

router = APIRouter(prefix="/api", tags=["Empresas y rutas"])


# ---------- Empresas ----------
@router.get("/companies", response_model=list[CompanyOut], dependencies=[Depends(staff)])
def list_companies(db: Session = Depends(get_db)):
    return db.scalars(select(Company).order_by(Company.name)).all()


@router.post("/companies", response_model=CompanyOut, status_code=201, dependencies=[Depends(admin_only)])
def create_company(data: CompanyIn, db: Session = Depends(get_db)):
    c = Company(**data.model_dump())
    db.add(c)
    db.commit()
    return c


@router.put("/companies/{cid}", response_model=CompanyOut, dependencies=[Depends(admin_only)])
def update_company(cid: int, data: CompanyIn, db: Session = Depends(get_db)):
    c = db.get(Company, cid)
    if not c:
        raise HTTPException(404, "Empresa no encontrada")
    for k, v in data.model_dump().items():
        setattr(c, k, v)
    db.commit()
    return c


@router.delete("/companies/{cid}", status_code=204, dependencies=[Depends(admin_only)])
def delete_company(cid: int, db: Session = Depends(get_db)):
    c = db.get(Company, cid)
    if not c:
        raise HTTPException(404, "Empresa no encontrada")
    if db.scalar(select(exists().where(Trip.company_id == cid))):
        raise HTTPException(409, "No se puede eliminar: la empresa tiene viajes registrados. Desactívala.")
    db.delete(c)
    db.commit()


# ---------- Rutas ----------
@router.get("/routes", response_model=list[RouteOut], dependencies=[Depends(staff)])
def list_routes(db: Session = Depends(get_db)):
    return db.scalars(select(Route).order_by(Route.origin, Route.destination)).all()


@router.post("/routes", response_model=RouteOut, status_code=201, dependencies=[Depends(admin_only)])
def create_route(data: RouteIn, db: Session = Depends(get_db)):
    r = Route(**data.model_dump())
    db.add(r)
    db.commit()
    return r


@router.put("/routes/{rid}", response_model=RouteOut, dependencies=[Depends(admin_only)])
def update_route(rid: int, data: RouteIn, db: Session = Depends(get_db)):
    r = db.get(Route, rid)
    if not r:
        raise HTTPException(404, "Ruta no encontrada")
    for k, v in data.model_dump().items():
        setattr(r, k, v)
    db.commit()
    return r


@router.delete("/routes/{rid}", status_code=204, dependencies=[Depends(admin_only)])
def delete_route(rid: int, db: Session = Depends(get_db)):
    r = db.get(Route, rid)
    if not r:
        raise HTTPException(404, "Ruta no encontrada")
    if db.scalar(select(exists().where(Trip.route_id == rid))):
        raise HTTPException(409, "No se puede eliminar una ruta con viajes programados")
    db.delete(r)
    db.commit()
