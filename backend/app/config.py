import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://bustrack:bustrack@127.0.0.1:3307/bustrack?charset=utf8mb4"
)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-change-me")
QR_SECRET = os.getenv("QR_SECRET", "dev-qr-secret-change-me")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))
SEAT_HOLD_SECONDS = int(os.getenv("SEAT_HOLD_SECONDS", "120"))  # reserva temporal de asiento (2 min)
CORS_ORIGINS =os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
