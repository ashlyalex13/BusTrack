import math

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..logging_config import logger
from ..models import User
from ..rate_limit import login_limiter
from ..schemas import LoginIn, TokenOut, UserIn, UserOut
from ..security import admin_only, create_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api", tags=["Autenticación y usuarios"])


@router.post("/auth/login", response_model=TokenOut)
def login(data: LoginIn, request: Request, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    key = f"{email}|{request.client.host if request.client else 'desconocido'}"
    wait = login_limiter.retry_after(key)
    if wait:
        logger.warning("Login bloqueado por intentos fallidos: %s", key)
        minutes = math.ceil(wait / 60)
        raise HTTPException(
            429, f"Demasiados intentos fallidos. Intenta de nuevo en {minutes} minuto{'s' if minutes > 1 else ''}.",
            headers={"Retry-After": str(wait)},
        )

    user = db.scalars(select(User).where(User.email == email)).first()
    if not user or not verify_password(data.password, user.password_hash):
        login_limiter.register_failure(key)
        logger.warning("Login fallido: %s", key)
        raise HTTPException(401, "Correo o contraseña incorrectos")
    login_limiter.reset(key)
    if not user.is_active:
        raise HTTPException(403, "Usuario inactivo")
    logger.info("Login: usuario=%s rol=%s", user.id, user.role)
    return TokenOut(access_token=create_token(user), user=user)


@router.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/users", response_model=list[UserOut], dependencies=[Depends(admin_only)])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.name)).all()


@router.post("/users", response_model=UserOut, status_code=201, dependencies=[Depends(admin_only)])
def create_user(data: UserIn, db: Session = Depends(get_db)):
    if not data.password:
        raise HTTPException(422, "La contraseña es obligatoria (mínimo 6 caracteres)")
    user = User(
        name=data.name, email=data.email.lower(), role=data.role,
        is_active=data.is_active, password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    return user


@router.put("/users/{user_id}", response_model=UserOut, dependencies=[Depends(admin_only)])
def update_user(user_id: int, data: UserIn, db: Session = Depends(get_db)):
    user = db.get(User, user_id) or _404()
    user.name, user.email, user.role, user.is_active = data.name, data.email.lower(), data.role, data.is_active
    if data.password:
        user.password_hash = hash_password(data.password)
    db.commit()
    return user


def _404():
    raise HTTPException(404, "Usuario no encontrado")
