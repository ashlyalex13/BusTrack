from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .config import APP_ENV, APP_TIMEZONE, CORS_ORIGINS
from .logging_config import logger, setup_logging
from .routers import auth, catalog, holds, reports, tickets, trips

setup_logging()
logger.info("BusTrack API iniciando (entorno=%s, zona horaria=%s)", APP_ENV, APP_TIMEZONE)

app = FastAPI(
    title="BusTrack API",
    version="1.0.0",
    description="Sistema de gestión para terminales de transporte terrestre. "
    "Autenticación: POST /api/auth/login y usar el token como Bearer.",
)

app.add_middleware(
    CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Cabeceras básicas de seguridad para todas las respuestas."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.exception_handler(IntegrityError)
def integrity_error(request: Request, exc: IntegrityError):
    logger.warning("Conflicto de integridad en %s %s: %s", request.method, request.url.path, exc.orig)
    return JSONResponse(status_code=409, content={"detail": "El registro ya existe o está en uso por otros datos"})


@app.exception_handler(Exception)
def unexpected_error(request: Request, exc: Exception):
    """Cualquier error no previsto: se registra con su traza y el cliente recibe un mensaje claro, sin detalles internos."""
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Ocurrió un error interno. Intenta de nuevo; si persiste, contacta al administrador."})


for module in (auth, catalog, trips, holds, tickets, reports):
    app.include_router(module.router)


@app.get("/api/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
