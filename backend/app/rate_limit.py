"""Límite de intentos fallidos de inicio de sesión (protección contra fuerza bruta).

Se cuenta por correo + IP: tras LOGIN_MAX_ATTEMPTS fallos dentro de la ventana,
ese par queda bloqueado hasta que expire el intento más antiguo. Un inicio de
sesión correcto reinicia el contador. Se guarda en memoria: suficiente para un
solo servidor; con varios servidores se movería a Redis o a la base de datos.
"""
import time
from collections import defaultdict, deque
from threading import Lock

from .config import LOGIN_LOCK_SECONDS, LOGIN_MAX_ATTEMPTS


class LoginLimiter:
    def __init__(self, max_attempts: int, window_seconds: int):
        self.max_attempts = max_attempts
        self.window = window_seconds
        self._failures: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def _prune(self, key: str, current: float) -> deque[float]:
        attempts = self._failures[key]
        while attempts and current - attempts[0] >= self.window:
            attempts.popleft()
        return attempts

    def retry_after(self, key: str) -> int:
        """Segundos que faltan para poder intentar de nuevo (0 si no está bloqueado)."""
        with self._lock:
            current = time.monotonic()
            attempts = self._prune(key, current)
            if len(attempts) < self.max_attempts:
                return 0
            return int(self.window - (current - attempts[0])) + 1

    def register_failure(self, key: str) -> None:
        with self._lock:
            self._failures[key].append(time.monotonic())

    def reset(self, key: str | None = None) -> None:
        with self._lock:
            if key is None:
                self._failures.clear()
            else:
                self._failures.pop(key, None)


login_limiter = LoginLimiter(LOGIN_MAX_ATTEMPTS, LOGIN_LOCK_SECONDS)
