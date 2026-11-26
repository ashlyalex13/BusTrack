"""Unitarias de app/security.py: contraseñas (bcrypt), tokens JWT y control de roles."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from fastapi import HTTPException

from app import security
from app.config import JWT_EXPIRE_MINUTES, JWT_SECRET


def test_la_contrasena_se_guarda_cifrada_y_se_verifica():
    hashed = security.hash_password("clave-segura")
    assert hashed != "clave-segura" and hashed.startswith("$2")
    assert security.verify_password("clave-segura", hashed)
    assert not security.verify_password("otra-clave", hashed)


def test_cada_hash_usa_una_sal_distinta():
    assert security.hash_password("misma") != security.hash_password("misma")


def test_el_token_lleva_usuario_rol_y_expiracion():
    token = security.create_token(SimpleNamespace(id=42, role="taquillero"))
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    assert payload["sub"] == "42" and payload["role"] == "taquillero"
    minutes = (datetime.fromtimestamp(payload["exp"], timezone.utc) - datetime.now(timezone.utc)).total_seconds() / 60
    assert JWT_EXPIRE_MINUTES - 1 <= minutes <= JWT_EXPIRE_MINUTES


def test_token_expirado_es_invalido():
    expired = jwt.encode({"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)}, JWT_SECRET, algorithm="HS256")
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(expired, JWT_SECRET, algorithms=["HS256"])


def test_token_firmado_con_otro_secreto_es_invalido():
    forged = jwt.encode({"sub": "1"}, "secreto-falso-de-al-menos-32-bytes-xx", algorithm="HS256")
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(forged, JWT_SECRET, algorithms=["HS256"])


def test_require_roles_permite_el_rol_correcto():
    admin = SimpleNamespace(role="admin")
    assert security.require_roles("admin")(user=admin) is admin
    assert security.staff(user=admin) is admin


def test_require_roles_rechaza_otro_rol_con_403():
    with pytest.raises(HTTPException) as exc:
        security.admin_only(user=SimpleNamespace(role="taquillero"))
    assert exc.value.status_code == 403
