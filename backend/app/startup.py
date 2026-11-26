"""Preparación al arrancar el contenedor de la API.

1. Espera a que MySQL acepte conexiones (además del healthcheck de Docker).
2. Si SEED_DEMO=true y la base está vacía, carga los datos de demostración.
   Si ya hay datos, no toca nada: reiniciar el contenedor nunca borra información.

Uso: python -m app.startup  (lo ejecuta el Dockerfile antes de iniciar uvicorn)
"""
import os
import time

from sqlalchemy import text

from .database import engine
from .logging_config import logger, setup_logging


def wait_for_db(timeout_seconds: int = 90) -> None:
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except Exception as exc:  # MySQL todavía iniciando
            if time.monotonic() > deadline:
                raise RuntimeError("No fue posible conectarse a MySQL") from exc
            logger.info("Esperando a que MySQL esté disponible...")
            time.sleep(2)


def seed_if_empty() -> None:
    with engine.connect() as conn:
        users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
    if users:
        logger.info("La base de datos ya tiene información: no se cargan datos de demostración")
        return
    from . import seed
    seed.run()
    logger.info("Datos de demostración cargados")


def main() -> None:
    setup_logging()
    wait_for_db()
    if os.getenv("SEED_DEMO", "false").lower() == "true":
        seed_if_empty()


if __name__ == "__main__":
    main()
