"""Hora oficial de la terminal.

Todas las fechas se guardan sin zona horaria (DATETIME de MySQL) en la hora local
de la terminal. Usar siempre estas funciones en lugar de datetime.now()/date.today(),
que dependen de la zona del servidor (en la nube suele ser UTC, 5 horas adelante).
"""
from datetime import date, datetime
from zoneinfo import ZoneInfo

from .config import APP_TIMEZONE

TZ = ZoneInfo(APP_TIMEZONE)


def now() -> datetime:
    return datetime.now(TZ).replace(tzinfo=None, microsecond=0)


def today() -> date:
    return now().date()
