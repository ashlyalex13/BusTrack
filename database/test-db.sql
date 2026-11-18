-- Base de datos aislada para las pruebas automáticas (pytest).
-- Las pruebas crean y limpian sus propias tablas en cada ejecución.
CREATE DATABASE IF NOT EXISTS bustrack_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON bustrack_test.* TO 'bustrack'@'%';
FLUSH PRIVILEGES;
