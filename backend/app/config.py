import os

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")  # development | production

DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://bustrack:bustrack@127.0.0.1:3307/bustrack?charset=utf8mb4"
)

# Secretos: mínimo 32 bytes (recomendación de RFC 7518 para HMAC-SHA256).
# Los valores por defecto solo sirven en desarrollo local; en producción son obligatorios.
_DEV_JWT_SECRET = "dev-jwt-secret-solo-para-desarrollo-local"
_DEV_QR_SECRET = "dev-qr-secret-solo-para-desarrollo-local"
JWT_SECRET = os.getenv("JWT_SECRET", _DEV_JWT_SECRET)
QR_SECRET = os.getenv("QR_SECRET", _DEV_QR_SECRET)
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

# Zona horaria de la terminal: los servidores en la nube suelen trabajar en UTC,
# y "los viajes de hoy" deben calcularse con la hora de Colombia.
APP_TIMEZONE = os.getenv("APP_TIMEZONE", "America/Bogota")

SEAT_HOLD_SECONDS = int(os.getenv("SEAT_HOLD_SECONDS", "120"))  # reserva temporal de asiento (2 min)

# Protección contra fuerza bruta en el inicio de sesión.
LOGIN_MAX_ATTEMPTS = int(os.getenv("LOGIN_MAX_ATTEMPTS", "5"))
LOGIN_LOCK_SECONDS = int(os.getenv("LOGIN_LOCK_SECONDS", "300"))

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")


def _validate_secrets() -> None:
    hint = 'Genera uno con: python -c "import secrets; print(secrets.token_urlsafe(48))"'
    weak = [name for name, value in (("JWT_SECRET", JWT_SECRET), ("QR_SECRET", QR_SECRET)) if len(value.encode()) < 32]
    if weak:
        raise RuntimeError(f"{', '.join(weak)} debe tener al menos 32 caracteres. {hint}")
    if APP_ENV == "production" and (JWT_SECRET == _DEV_JWT_SECRET or QR_SECRET == _DEV_QR_SECRET):
        raise RuntimeError(f"En producción JWT_SECRET y QR_SECRET deben definirse en el entorno. {hint}")


_validate_secrets()
