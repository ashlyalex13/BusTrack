# BusTrack

Sistema de gestión para terminales de transporte terrestre: rutas, viajes, taquilla con grilla de asientos,
tiquetes con QR verificable, portal público de horarios y reportes.

**Stack:** MySQL 8 · FastAPI + SQLAlchemy · React + Vite + Tailwind CSS · nginx · Docker

## Ejecución con Docker (un solo comando)

Requisito: Docker Desktop.

```bash
docker compose up --build
```

| Servicio | Contenedor | Acceso |
|---|---|---|
| Interfaz web (React servido por nginx) | `bustrack-web` | http://localhost:8080 |
| API (FastAPI) y documentación Swagger | `bustrack-api` | http://localhost:8080/docs (pasa por nginx) |
| Base de datos MySQL 8 | `bustrack-db` | `localhost:3307` |

- La primera vez se crea el schema y se cargan **datos de demostración** de forma automática (solo si la base está vacía; reiniciar no borra información).
- Usuarios demo: `admin@bustrack.co / admin123` (administrador) y `taquilla1@bustrack.co / taquilla123` (taquillero).
- Orden de arranque garantizado con *healthchecks*: MySQL → API → web.
- Pruebas dentro del contenedor: `docker compose exec api pytest`
- Detener: `docker compose down` (conserva los datos) · borrar todo: `docker compose down -v`.
- Producción: crear un archivo `.env` junto a `docker-compose.yml` con `APP_ENV=production`, `JWT_SECRET`, `QR_SECRET` y `MYSQL_PASSWORD` propios.

```
Navegador ──► nginx (web:80 → localhost:8080) ──/api, /docs──► FastAPI (api:8000) ──► MySQL (db:3306)
                    └── archivos estáticos de React
```

## Ejecución para desarrollo (sin contenedores para la app)

Requisitos: Docker Desktop (solo para MySQL), Python 3.11+ y Node.js 18+.

```bash
# 1. Base de datos (crea el schema automáticamente desde database/schema.sql)
docker compose up -d db

# 2. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # Linux/Mac: cp .env.example .env
python -m app.seed              # datos de demostración (borra lo existente)
uvicorn app.main:app --reload --port 8000

# 3. Frontend (otra terminal)
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

- API y documentación Swagger: http://localhost:8000/docs
- Usuarios demo: `admin@bustrack.co / admin123`, `taquilla1@bustrack.co / taquilla123`

## Módulos

| Módulo | Ruta frontend | Rol |
|---|---|---|
| Portal público de horarios (HU01) | `/` | Sin login |
| Taquilla: grilla de asientos y venta (HU03) | `/taquilla` | admin, taquillero |
| Verificación de QR (HU04) | `/verificar` | admin, taquillero |
| Panel: viajes del día y recaudo (HU05) | `/admin` | admin |
| CRUD viajes, rutas/tarifas (HU02), empresas, usuarios | `/admin/*` | admin |

## Contratos de API

| Método interno | Endpoint |
|---|---|
| `Trip.getTodayTrips()` | `GET /api/trips/today` |
| `Trip.searchAvailable(o, d, date)` | `GET /api/trips/search?origin=&destination=&date=` |
| `Trip.getSeats(id)` | `GET /api/trips/{id}/seats` |
| `Ticket.sell({...})` | `POST /api/tickets` → 201, o 409 si el asiento está ocupado |
| `Ticket.verify(code)` | `GET /api/tickets/verify?code=` (consulta) · `POST /api/tickets/verify` (registra abordaje) |
| Reporte diario | `GET /api/reports/daily?date=` |

## Decisiones técnicas críticas

**Sin venta doble (RNF01).** La venta corre en una transacción que primero bloquea la fila del viaje con
`SELECT ... FOR UPDATE`, así que las ventas de un mismo viaje se procesan una tras otra. Luego vuelve a revisar
el asiento con una lectura bloqueante. Como respaldo, la base de datos tiene `UNIQUE(trip_id, active_seat)`, donde
`active_seat` es una columna generada que vale `NULL` en los tiquetes anulados. La grilla se actualiza cada 4 s.

**QR no adivinable (RNF02).** El código es `uuid.firma`, donde `firma = HMAC-SHA256(QR_SECRET, uuid|trip_id|asiento)`
truncada a 32 caracteres hex. La verificación recalcula la firma y rechaza códigos alterados, inexistentes, anulados
o ya usados.

**Seguridad (RNF03).** Las contraseñas se guardan con bcrypt, el JWT expira y los roles se validan en cada endpoint.
Los secretos van en `.env`, que está excluido de Git.

## Pruebas

Las pruebas automáticas usan una base de datos aislada (`bustrack_test`), que se crea sola con el contenedor.
Si tu volumen de Docker es anterior a este cambio, créala una vez:
`docker exec -i bustrack-db mysql -uroot -proot < database/test-db.sql`

```bash
cd backend
pytest                                 # suite completa (requiere el contenedor de MySQL en ejecución)
python tests/concurrency_test.py 20   # demo en vivo contra el servidor: 20 ventas simultáneas → 1 éxito
```

## Estructura

```
database/schema.sql         Schema MySQL
backend/app/
  models.py  schemas.py     Entidades ORM y DTOs (Pydantic)
  security.py  qr.py        JWT/roles y firma HMAC del QR
  services.py               Serialización compartida
  routers/                  auth, catalog (empresas/rutas), trips, tickets, reports
  seed.py                   Datos de demostración
frontend/src/
  lib/                      Cliente API, auth, formatos
  components/               Layout, UI, SeatGrid, TicketModal, CrudPage genérico
  pages/                    Portal público, Login, Taquilla, Verificar, admin/*
```

## Próximas mejoras
- Reserva temporal de asiento (2 min) mientras se registra el pasajero
- Escaneo de QR con la cámara
- Anulación de tiquetes desde la UI (el endpoint `POST /api/tickets/{uuid}/cancel` ya existe)
- Exportar reportes a PDF o Excel
