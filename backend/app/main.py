from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .config import CORS_ORIGINS
from .routers import auth, catalog, reports, tickets, trips

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


@app.exception_handler(IntegrityError)
def integrity_error(_: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "El registro ya existe o está en uso por otros datos"})


for module in (auth, catalog, trips, tickets, reports):
    app.include_router(module.router)


@app.get("/api/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
