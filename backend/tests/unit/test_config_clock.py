"""Unitarias de app/config.py (secretos) y app/clock.py (hora oficial de la terminal)."""
from datetime import datetime, timezone

import pytest

from app import config
from app.clock import now, today


@pytest.mark.parametrize("jwt,qr,env", [
    ("corto", "x" * 40, "development"),                             # secreto débil
    ("x" * 40, "corto", "development"),
    (config._DEV_JWT_SECRET, config._DEV_QR_SECRET, "production"),  # valores de desarrollo en producción
])
def test_configuracion_insegura_impide_arrancar(monkeypatch, jwt, qr, env):
    monkeypatch.setattr(config, "JWT_SECRET", jwt)
    monkeypatch.setattr(config, "QR_SECRET", qr)
    monkeypatch.setattr(config, "APP_ENV", env)
    with pytest.raises(RuntimeError):
        config._validate_secrets()


def test_configuracion_segura_en_produccion_es_aceptada(monkeypatch):
    monkeypatch.setattr(config, "JWT_SECRET", "j" * 48)
    monkeypatch.setattr(config, "QR_SECRET", "q" * 48)
    monkeypatch.setattr(config, "APP_ENV", "production")
    config._validate_secrets()  # no lanza error


def test_hora_de_la_terminal_es_la_de_colombia_sin_importar_el_servidor():
    utc = datetime.now(timezone.utc).replace(tzinfo=None)
    assert round((utc - now()).total_seconds() / 3600) == 5  # Colombia es UTC-5 todo el año


def test_now_es_compatible_con_datetime_de_mysql():
    current = now()
    assert current.tzinfo is None and current.microsecond == 0
    assert today() == current.date()
