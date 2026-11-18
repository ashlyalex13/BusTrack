-- Migración 001: reserva temporal de asientos (HU03).
-- Solo para bases de datos creadas antes de este cambio (las nuevas ya la traen en schema.sql).
-- Aplicar con:  docker exec -i bustrack-db mysql -ubustrack -pbustrack bustrack < database/migrations/001_seat_holds.sql
CREATE TABLE IF NOT EXISTS seat_holds (
    trip_id      INT NOT NULL,
    seat_number  INT NOT NULL,
    user_id      INT NOT NULL,
    expires_at   DATETIME NOT NULL,
    PRIMARY KEY (trip_id, seat_number),
    CONSTRAINT fk_hold_trip FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,
    CONSTRAINT fk_hold_user FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_holds_expires (expires_at)
) ENGINE=InnoDB;
