# API de BusTrack (FastAPI + SQLAlchemy)
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias primero: Docker reutiliza esta capa si solo cambia el código.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Se ejecuta sin privilegios de administrador.
RUN useradd --create-home --uid 1000 bustrack && chown -R bustrack /app
USER bustrack

EXPOSE 8000

# 1) espera a MySQL y carga datos demo si la base está vacía; 2) inicia la API.
# --proxy-headers: la IP real del cliente llega desde nginx (límite de intentos de login).
CMD ["sh", "-c", "python -m app.startup && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'"]
