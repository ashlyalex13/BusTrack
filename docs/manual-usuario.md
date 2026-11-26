# BusTrack · Manual de usuario

**Versión:** 1.0.0

BusTrack es el sistema de la terminal para consultar horarios, vender tiquetes con código QR, controlar el abordaje
y administrar empresas, rutas, viajes y reportes.

## Contenido

1. [Ingreso al sistema](#1-ingreso-al-sistema)
2. [Público: consulta de horarios](#2-público-consulta-de-horarios)
3. [Taquillero: venta de tiquetes](#3-taquillero-venta-de-tiquetes)
4. [Taquillero: consulta y reimpresión de tiquetes](#4-taquillero-consulta-y-reimpresión-de-tiquetes)
5. [Control de abordaje: verificar QR](#5-control-de-abordaje-verificar-qr)
6. [Administrador](#6-administrador)
7. [Mensajes frecuentes](#7-mensajes-frecuentes)

## Roles

| Rol | Qué puede hacer |
|---|---|
| **Público** (sin iniciar sesión) | Consultar horarios, tarifas y asientos disponibles |
| **Taquillero** | Todo lo anterior, más vender tiquetes, consultar o reimprimir tiquetes y verificar QR |
| **Administrador** | Todo lo anterior, más anular tiquetes, ver el panel con reportes y gestionar viajes, rutas, empresas y usuarios |

El menú superior muestra solo las opciones del rol que inició sesión. En pantallas pequeñas el menú se abre con el
botón ☰.

---

## 1. Ingreso al sistema

1. Abre el sistema en el navegador (en la instalación local: http://localhost:8080).
2. Pulsa **Ingresar** en la esquina superior derecha.
3. Escribe tu **correo** y tu **contraseña** y pulsa **Ingresar**.
4. Al terminar el turno, pulsa **Cerrar sesión** (el ícono de salida junto a tu nombre).

- La sesión dura 8 horas. Después de ese tiempo el sistema pide ingresar de nuevo.
- Tras **5 intentos fallidos** seguidos, el ingreso queda bloqueado **5 minutos** como protección. Si olvidaste la
  contraseña, pídele al administrador que la cambie.
- Usuarios de demostración: `admin@bustrack.co / admin123` (administrador) y `taquilla1@bustrack.co / taquilla123` (taquillero).

## 2. Público: consulta de horarios

La página de inicio (**Horarios**) está disponible para cualquier persona, sin iniciar sesión.

1. Elige el **Origen**, el **Destino** y la **Fecha**. Puedes dejar origen o destino vacíos para ver todas las opciones.
2. Pulsa **Buscar**.
3. Cada viaje muestra la hora de salida, la ruta, la empresa, la duración, la tarifa y los **asientos disponibles**.
   Un viaje sin cupo aparece como agotado.

## 3. Taquillero: venta de tiquetes

Menú **Taquilla**.

1. **Busca el viaje:** elige origen, destino y fecha y pulsa **Buscar**. Aparece la lista de salidas.
2. **Selecciona el viaje** en la lista. A la derecha (o debajo, en el celular) aparece la **grilla de asientos**. La
   grilla se actualiza sola cada pocos segundos (indicador **En vivo**), así que ves las ventas de las demás taquillas.

   | Color | Significado |
   |---|---|
   | Blanco con borde verde | Libre |
   | Azul índigo | Tu selección |
   | Ámbar | Reservado por otra taquilla (no se puede elegir) |
   | Gris claro | Vendido |
   | Gris oscuro | Abordado |

3. **Elige un asiento libre.** Queda **reservado para ti durante 2 minutos**, con la cuenta regresiva visible. En ese
   tiempo ninguna otra taquilla puede venderlo. Si eliges otro asiento, el anterior se libera.
4. **Registra al pasajero:**
   - **Nombre completo:** solo letras.
   - **Documento de identidad:** de 5 a 20 caracteres, con números, letras o guiones.
5. Pulsa **Vender asiento N**. Se abre el **tiquete de viaje** con el código QR, la ruta, la salida, el asiento, el
   pasajero y el valor.
6. Pulsa **Imprimir** para entregar el tiquete, o **Cerrar** para continuar.

Debajo de la grilla aparece la lista de **tiquetes vendidos del viaje**. Desde ahí puedes volver a abrir cualquiera
con **Ver**.

**Si la reserva vence** antes de vender, elige el asiento otra vez. Si mientras tanto otra taquilla lo tomó, el
sistema te avisa y debes escoger otro.

## 4. Taquillero: consulta y reimpresión de tiquetes

Menú **Tiquetes**.

1. Escribe el **documento** o parte del **nombre** del pasajero (mínimo 3 caracteres) y pulsa **Buscar**.
2. En los resultados puedes ver el viaje, el asiento, el estado y el valor.
   - **Ver** abre el tiquete con su QR para reimprimirlo.
   - **Anular** solo aparece para el administrador (ver la sección 6.6).

## 5. Control de abordaje: verificar QR

Menú **Verificar QR**. Lo usa el personal de la puerta de abordaje.

1. Lee el código de una de estas formas:
   - pulsa **Escanear con la cámara** y apunta al QR del tiquete (el navegador pedirá permiso para usar la cámara);
   - usa un lector de códigos USB, que escribe el código en el campo;
   - pega el código en **Código del tiquete**.
2. Pulsa **Consultar** para ver si el tiquete es válido **sin** registrar el abordaje.
3. Pulsa **Validar y registrar abordaje** cuando el pasajero sube al bus. El sistema muestra:
   - **TIQUETE VÁLIDO** (verde), con los datos del pasajero, el viaje y el asiento. El abordaje queda registrado.
   - **TIQUETE RECHAZADO** (rojo), con el motivo:

     | Mensaje | Qué significa |
     |---|---|
     | *El tiquete no existe* | El código no corresponde a ninguna venta |
     | *Firma inválida: el código fue alterado* | El QR fue modificado o es falso |
     | *El tiquete fue anulado* | La venta se anuló |
     | *El tiquete ya fue usado (fecha y hora)* | Ese QR ya se usó para abordar. Cada tiquete sirve una sola vez. |

## 6. Administrador

### 6.1 Panel (reportes del día)

Menú **Panel**. Elige la **Fecha del reporte** y verás:

- Indicadores: viajes, tiquetes vendidos, ocupación y recaudo.
- **Viajes del día:** hora, ruta, empresa, ocupación y estado.
- **Recaudo por empresa** y **recaudo por taquillero**.
- **Exportar CSV:** descarga el reporte para abrirlo en Excel.

### 6.2 Viajes

Menú **Viajes**. Lista los viajes de la fecha elegida con su ocupación.

- **Nuevo viaje:** elige la ruta, la empresa (solo aparecen las activas), la fecha y hora de salida (debe ser futura),
  la capacidad del bus (de 4 a 80 asientos) y la placa.
- **Editar:** permite cambiar el estado a *Programado*, *Despachado* o *Cancelado*. No se puede reducir la capacidad
  por debajo de un asiento ya vendido.
- **Eliminar:** solo se pueden eliminar viajes sin tiquetes vendidos. Si ya hay ventas, cambia el estado a *Cancelado*.

Solo se venden tiquetes de viajes **programados** que todavía no han salido.

### 6.3 Rutas y tarifas

Menú **Rutas**. Cada ruta tiene origen, destino, **tarifa** y duración estimada.

- El origen debe ser distinto del destino y la tarifa mayor que cero.
- Cambiar la tarifa afecta solo las ventas nuevas: los tiquetes ya vendidos conservan su valor.
- No se puede eliminar una ruta que tenga viajes.

### 6.4 Empresas

Menú **Empresas**. Registra el nombre, el NIT y el teléfono de cada transportadora.

- Una empresa con viajes no se puede eliminar.
- Para que deje de aparecer al programar viajes, desmarca **Empresa activa**.

### 6.5 Usuarios

Menú **Usuarios**. Crea taquilleros y administradores.

- **Contraseña:** mínimo 6 caracteres. Al editar un usuario, déjala vacía para no cambiarla.
- Para retirar a alguien, desmarca **Usuario activo**. No podrá ingresar, pero sus ventas siguen en los reportes.

### 6.6 Anular un tiquete

En **Tiquetes**, busca al pasajero y pulsa **Anular**. El sistema pide confirmación.

- Al anular, el asiento vuelve a quedar libre para la venta y el QR deja de servir.
- Solo se pueden anular tiquetes vendidos que **no** hayan abordado.

## 7. Mensajes frecuentes

| Mensaje | Causa y solución |
|---|---|
| *El asiento N ya fue vendido* | Otra taquilla lo vendió un instante antes. Elige otro asiento. |
| *El asiento N está reservado por otra taquilla* | Otra taquilla lo está vendiendo. Espera o elige otro. |
| *El viaje ya salió: no se pueden vender ni reservar asientos* | La hora de salida ya pasó |
| *Demasiados intentos fallidos. Intenta de nuevo en N minutos.* | Se bloqueó el ingreso por intentos fallidos. Espera el tiempo indicado. |
| *No se pudo conectar con el servidor* | Revisa la conexión a internet o avisa al administrador del sistema |
| Te devuelve a la pantalla de ingreso | La sesión expiró (8 horas). Ingresa de nuevo. |
