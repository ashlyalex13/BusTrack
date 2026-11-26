# BusTrack · Guía de pruebas para el evaluador

Esta guía permite comprobar en unos 15 minutos que el sistema cumple sus requisitos principales. Todo se ejecuta en
la máquina local con Docker.

## 1. Puesta en marcha

```bash
git clone https://github.com/ashlyalex13/BusTrack.git
cd BusTrack
docker compose up --build
```

Cuando los tres contenedores estén en estado *healthy* (`docker compose ps`), abre **http://localhost:8080**. La
primera vez se cargan datos de demostración automáticamente: 3 usuarios, 3 empresas, 8 rutas y 96 viajes entre ayer y pasado mañana, con algunas ventas ya hechas.

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin@bustrack.co` | `admin123` | Administrador |
| `taquilla1@bustrack.co` | `taquilla123` | Taquillero (Laura Gómez) |
| `taquilla2@bustrack.co` | `taquilla123` | Taquillero (Andrés Ríos) |

> Para simular dos taquillas a la vez, usa una ventana normal y otra de incógnito (o dos navegadores distintos), cada
> una con un taquillero diferente.

## 2. Pruebas automatizadas

| Comando | Qué ejecuta | Resultado esperado |
|---|---|---|
| `docker compose exec api pytest` | Las 185 pruebas del backend (51 unitarias + 134 de integración) dentro del contenedor | Todas pasan (`passed`) |
| `docker compose exec api pytest -m unit` | Solo las unitarias, sin base de datos | 51 pasan |
| `docker compose exec api pytest --cov=app` | Backend con reporte de cobertura | Cobertura total ≈ 97 % |
| `cd frontend && npm install && npm test` | Las 43 pruebas del frontend (requiere Node.js 18+) | Todas pasan |

También puedes ver la ejecución en GitHub, sin instalar nada: pestaña **Actions** del repositorio. Cada cambio ejecuta
backend, frontend y el despliegue completo con Docker.

## 3. Escenarios de prueba manual

Marca cada escenario a medida que lo verificas.

### E1. Consulta pública de horarios (HU01)
- [ ] Sin iniciar sesión, en **Horarios**, elige origen *Cali*, un destino y la fecha de hoy o mañana, y pulsa **Buscar**.
- [ ] **Esperado:** cada viaje muestra la hora, la empresa, la tarifa y los asientos disponibles.

### E2. Control de acceso por rol (RNF03)
- [ ] Sin sesión, abre http://localhost:8080/admin. **Esperado:** redirige al inicio de sesión.
- [ ] Ingresa como `taquilla1`. **Esperado:** el menú muestra Taquilla, Tiquetes y Verificar QR, pero no las opciones de administración.
- [ ] Ingresa 6 veces con una contraseña incorrecta. **Esperado:** a partir del sexto intento aparece *"Demasiados intentos fallidos..."* y el ingreso queda bloqueado 5 minutos para ese correo.

### E3. Venta de tiquete con reserva de asiento (HU03)
- [ ] Como `taquilla1`, en **Taquilla**, busca un viaje y selecciónalo.
- [ ] Haz clic en un asiento libre. **Esperado:** queda en color índigo con *"Reservado para ti · expira en 2:00"*.
- [ ] En la segunda ventana, como `taquilla2`, abre el mismo viaje. **Esperado:** en unos 4 segundos ese asiento aparece en ámbar (*reservado por otra taquilla*) y no se puede elegir.
- [ ] En la primera ventana, escribe el nombre *Ana Torres* y el documento *1010101*, y pulsa **Vender asiento N**. **Esperado:** se abre el tiquete con su QR, y en la otra ventana el asiento pasa a gris (vendido).

### E4. Validaciones de datos
- [ ] Intenta vender con el nombre *"Ana 123"* o el documento *"12"*. **Esperado:** no se vende. El formulario o el servidor muestran un mensaje en español que indica qué corregir.
- [ ] Como administrador, crea una ruta con el mismo origen y destino, o con tarifa 0. **Esperado:** se rechaza.

### E5. Verificación del QR y abordaje (HU04, RNF02)
- [ ] Copia el código que aparece bajo el QR del tiquete vendido en E3. En **Verificar QR**, pégalo y pulsa **Consultar**. **Esperado:** *TIQUETE VÁLIDO*, sin registrar el abordaje todavía.
- [ ] Pulsa **Validar y registrar abordaje**. **Esperado:** *Abordaje registrado correctamente*.
- [ ] Vuelve a validar el mismo código. **Esperado:** *TIQUETE RECHAZADO: el tiquete ya fue usado (fecha y hora)*.
- [ ] Cambia un solo carácter del final del código y consulta. **Esperado:** *Firma inválida: el código fue alterado*.
- [ ] Opcional: con un celular o una cámara web, usa **Escanear con la cámara** sobre el QR en pantalla.

### E6. Venta simultánea del mismo asiento (RNF01)

Este es el escenario más importante. Ejecuta:

```bash
docker compose exec api python tests/concurrency_test.py 20
```

**Esperado:** de 20 ventas simultáneas del mismo asiento, **exactamente 1** obtiene `201` y **19** obtienen `409`.
Puedes repetirlo varias veces: el resultado no cambia.

### E7. Anulación de tiquete
- [ ] Como administrador, en **Tiquetes**, busca *1010101* (o vende uno nuevo sin abordar) y pulsa **Anular**.
- [ ] **Esperado:** solo se pueden anular tiquetes no abordados. Al anular, el asiento vuelve a estar libre en la grilla y el QR queda rechazado (*el tiquete fue anulado*).

### E8. Administración y reportes (HU02, HU05)
- [ ] En **Rutas**, cambia la tarifa de una ruta. **Esperado:** las ventas nuevas usan la tarifa nueva, y los tiquetes anteriores conservan su valor.
- [ ] En **Viajes**, crea un viaje para mañana. Luego intenta eliminar un viaje con tiquetes vendidos. **Esperado:** el sistema no lo permite y sugiere marcarlo como *Cancelado*.
- [ ] En **Panel**, elige la fecha de hoy. **Esperado:** muestra los viajes, la ocupación y el recaudo por empresa y por taquillero, con las ventas hechas durante la prueba. **Exportar CSV** descarga el reporte y se abre bien en Excel.

### E9. Persistencia y despliegue
- [ ] Ejecuta `docker compose down` y luego `docker compose up`. **Esperado:** las ventas hechas siguen ahí, porque los datos demo solo se cargan si la base está vacía.
- [ ] Documentación de la API: http://localhost:8080/docs (Swagger), donde se puede probar cada endpoint.

## 4. Limpieza

```bash
docker compose down -v
```

Este comando detiene los contenedores y borra la base de datos de prueba.
