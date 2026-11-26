-- =====================================================================
-- BusTrack - Schema MySQL 8 (InnoDB)
-- Se ejecuta automáticamente al crear el contenedor de Docker.
-- =====================================================================
SET NAMES utf8mb4;

CREATE TABLE users (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(120) NOT NULL,
    email          VARCHAR(160) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,                 -- bcrypt
    role           ENUM('admin', 'taquillero') NOT NULL,
    is_active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE companies (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(120) NOT NULL UNIQUE,
    nit         VARCHAR(30) UNIQUE,
    phone       VARCHAR(30),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- La tarifa se configura por ruta (RF02)
CREATE TABLE routes (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    origin            VARCHAR(80) NOT NULL,
    destination       VARCHAR(80) NOT NULL,
    base_fare         DECIMAL(10,2) NOT NULL,
    duration_minutes  INT NOT NULL DEFAULT 60,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_route (origin, destination),
    CONSTRAINT chk_fare CHECK (base_fare > 0),
    CONSTRAINT chk_route_cities CHECK (origin <> destination)
) ENGINE=InnoDB;

CREATE TABLE trips (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    route_id      INT NOT NULL,
    company_id    INT NOT NULL,
    departure_at  DATETIME NOT NULL,
    bus_capacity  INT NOT NULL DEFAULT 40,
    bus_plate     VARCHAR(10),
    status        ENUM('scheduled', 'departed', 'cancelled') NOT NULL DEFAULT 'scheduled',
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_trip_route   FOREIGN KEY (route_id)   REFERENCES routes(id),
    CONSTRAINT fk_trip_company FOREIGN KEY (company_id) REFERENCES companies(id),
    CONSTRAINT chk_capacity CHECK (bus_capacity BETWEEN 4 AND 80),
    INDEX idx_trips_departure (departure_at)
) ENGINE=InnoDB;

-- RNF01: la columna generada active_seat vale NULL cuando el tiquete está
-- anulado, por lo que UNIQUE(trip_id, active_seat) impide dos tiquetes
-- activos en el mismo asiento (red de seguridad además del FOR UPDATE).
CREATE TABLE tickets (
    uuid            CHAR(36) PRIMARY KEY,
    trip_id         INT NOT NULL,
    seat_number     INT NOT NULL,
    passenger_name  VARCHAR(120) NOT NULL,
    passenger_doc   VARCHAR(30) NOT NULL,
    seller_id       INT NOT NULL,
    price           DECIMAL(10,2) NOT NULL,
    qr_signature    VARCHAR(64) NOT NULL,                 -- HMAC-SHA256 truncado (RNF02)
    status          ENUM('sold', 'boarded', 'cancelled') NOT NULL DEFAULT 'sold',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    boarded_at      DATETIME NULL,
    active_seat     INT GENERATED ALWAYS AS (IF(status <> 'cancelled', seat_number, NULL)) STORED,
    CONSTRAINT fk_ticket_trip   FOREIGN KEY (trip_id)   REFERENCES trips(id),
    CONSTRAINT fk_ticket_seller FOREIGN KEY (seller_id) REFERENCES users(id),
    UNIQUE KEY uq_trip_active_seat (trip_id, active_seat),
    INDEX idx_tickets_created (created_at)
) ENGINE=InnoDB;

-- HU03: reserva temporal de un asiento mientras el taquillero registra al
-- pasajero. Expira sola (expires_at) y un asiento reservado no lo puede
-- vender otra taquilla.
CREATE TABLE seat_holds (
    trip_id      INT NOT NULL,
    seat_number  INT NOT NULL,
    user_id      INT NOT NULL,
    expires_at   DATETIME NOT NULL,
    PRIMARY KEY (trip_id, seat_number),
    CONSTRAINT fk_hold_trip FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    CONSTRAINT fk_hold_user FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_holds_expires (expires_at)
) ENGINE=InnoDB;
