"""Prueba de concurrencia (RNF01): N taquilleros venden el MISMO asiento a la vez.

Resultado esperado: exactamente 1 venta exitosa (201) y N-1 rechazos (409).
Uso (con el backend corriendo):  python tests/concurrency_test.py [N]
"""
import sys
import threading
from collections import Counter

import httpx

API = "http://127.0.0.1:8000/api"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20

token = httpx.post(f"{API}/auth/login", json={"email": "taquilla1@bustrack.co", "password": "taquilla123"}).json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

trip = next(t for t in httpx.get(f"{API}/trips/search").json() if t["available"] > 0)
seats = httpx.get(f"{API}/trips/{trip['id']}/seats").json()["seats"]
seat = next(s["number"] for s in seats if s["status"] == "free")
print(f"Viaje #{trip['id']} {trip['origin']} -> {trip['destination']}, asiento {seat}, {N} peticiones simultáneas")

barrier = threading.Barrier(N)
results: list[int] = []


def attempt(i: int):
    body = {"trip_id": trip["id"], "seat_number": seat, "passenger_name": f"Pasajero {chr(65 + i)}", "passenger_doc": f"1000{i:04d}"}
    with httpx.Client(timeout=30) as client:
        barrier.wait()  # todas salen al mismo tiempo
        results.append(client.post(f"{API}/tickets", json=body, headers=headers).status_code)


threads = [threading.Thread(target=attempt, args=(i,)) for i in range(N)]
for t in threads:
    t.start()
for t in threads:
    t.join()

count = Counter(results)
print(f"Resultados: {dict(count)}")
ok = count.get(201) == 1 and count.get(409) == N - 1
print("PRUEBA SUPERADA: exactamente 1 venta" if ok else "PRUEBA FALLIDA")
sys.exit(0 if ok else 1)
