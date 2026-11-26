"""Unitarias de app/rate_limit.py: límite de intentos fallidos de inicio de sesión."""
import pytest

from app.rate_limit import LoginLimiter


@pytest.fixture
def clock(monkeypatch):
    """Reloj controlado para no tener que esperar minutos reales."""
    current = [1000.0]
    monkeypatch.setattr("app.rate_limit.time.monotonic", lambda: current[0])
    return current


def test_no_bloquea_antes_del_limite(clock):
    limiter = LoginLimiter(max_attempts=3, window_seconds=60)
    for _ in range(2):
        limiter.register_failure("ana")
    assert limiter.retry_after("ana") == 0


def test_bloquea_al_llegar_al_limite_e_informa_la_espera(clock):
    limiter = LoginLimiter(max_attempts=3, window_seconds=60)
    for _ in range(3):
        limiter.register_failure("ana")
    assert limiter.retry_after("ana") == 61
    clock[0] += 30
    assert limiter.retry_after("ana") == 31


def test_el_bloqueo_expira_con_el_tiempo(clock):
    limiter = LoginLimiter(max_attempts=3, window_seconds=60)
    for _ in range(3):
        limiter.register_failure("ana")
    clock[0] += 61
    assert limiter.retry_after("ana") == 0


def test_las_cuentas_son_independientes(clock):
    limiter = LoginLimiter(max_attempts=2, window_seconds=60)
    limiter.register_failure("ana")
    limiter.register_failure("ana")
    assert limiter.retry_after("ana") > 0
    assert limiter.retry_after("luis") == 0


def test_reset_limpia_una_cuenta_o_todas(clock):
    limiter = LoginLimiter(max_attempts=1, window_seconds=60)
    limiter.register_failure("ana")
    limiter.register_failure("luis")
    limiter.reset("ana")
    assert limiter.retry_after("ana") == 0 and limiter.retry_after("luis") > 0
    limiter.reset()
    assert limiter.retry_after("luis") == 0
