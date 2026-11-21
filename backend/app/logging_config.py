"""Registro de eventos (logs) de la aplicación.

Se registran las operaciones críticas (ventas, rechazos por concurrencia,
anulaciones, abordajes, QR rechazados e intentos de acceso fallidos) para poder
auditar la operación y diagnosticar errores. Por privacidad NO se registran
nombres ni documentos de pasajeros: solo identificadores.
"""
import logging
import os
import sys

logger = logging.getLogger("bustrack")


def setup_logging() -> None:
    if logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
