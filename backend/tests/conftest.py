"""Configuración común de las pruebas.

tests/unit/         pruebas unitarias: cada módulo por separado, sin base de datos.
tests/integration/  pruebas de integración: la API completa contra MySQL (bustrack_test).

Ejecutar:  pytest              (todas)
           pytest -m unit      (solo unitarias: segundos, no requieren Docker)
           pytest -m integration
"""
import os

# Deben definirse ANTES de importar la aplicación (la configuración se lee al importar).
os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL", "mysql+pymysql://bustrack:bustrack@127.0.0.1:3307/bustrack_test?charset=utf8mb4"
)
os.environ["QR_SECRET"] = "secreto-qr-de-pruebas-con-32-bytes-o-mas"
os.environ["JWT_SECRET"] = "secreto-jwt-de-pruebas-con-32-bytes-o-mas"

import pytest  # noqa: E402


def pytest_collection_modifyitems(items):
    """Marca cada prueba como unit o integration según la carpeta donde está."""
    for item in items:
        parts = item.path.parts
        if "unit" in parts:
            item.add_marker(pytest.mark.unit)
        elif "integration" in parts:
            item.add_marker(pytest.mark.integration)
