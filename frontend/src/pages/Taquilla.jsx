import { useCallback, useEffect, useRef, useState } from 'react'
import { BusFront, Lock, Printer, RefreshCw, Ticket, UserRound } from 'lucide-react'
import { api } from '../lib/api.js'
import { dayLabel, errMsg, hour, money, todayISO } from '../lib/format.js'
import { AvailabilityBadge, searchQuery, TripSearchForm, TripSummary } from '../components/TripSearch.jsx'
import SeatGrid from '../components/SeatGrid.jsx'
import TicketModal from '../components/TicketModal.jsx'
import { Alert, Empty, PageHeader, Spinner, StatusBadge } from '../components/ui.jsx'

const POLL_MS = 4000
const EMPTY_PAX = { passenger_name: '', passenger_doc: '' }

/** HU03: venta de tiquete con grilla en tiempo real y sin doble venta. */
export default function Taquilla() {
  const [filters, setFilters] = useState({ origin: '', destination: '', date: todayISO() })
  const [trips, setTrips] = useState(null)
  const [tripId, setTripId] = useState(null)
  const [seatData, setSeatData] = useState(null)
  const [seat, setSeat] = useState(null)
  const [pax, setPax] = useState(EMPTY_PAX)
  const [selling, setSelling] = useState(false)
  const [msg, setMsg] = useState(null)
  const [ticket, setTicket] = useState(null)
  const [tickets, setTickets] = useState([])
  const [hold, setHold] = useState(null) // { seat, until } reserva temporal del asiento seleccionado
  const [now, setNow] = useState(Date.now())
  const holdRef = useRef(null)
  const sectionRef = useRef(null)

  const loadTrips = useCallback((f = filters) => api(searchQuery(f)).then(setTrips).catch((e) => setMsg({ type: 'error', text: errMsg(e) })), [filters])

  const loadSeats = useCallback(async (id) => {
    const d = await api(`/trips/${id}/seats`)
    setSeatData(d)
    setSeat((s) => {
      if (s && ['sold', 'boarded'].includes(d.seats[s - 1]?.status)) {
        setMsg({ type: 'warn', text: `El asiento ${s} acaba de ser vendido por otra taquilla. Elige otro.` })
        return null
      }
      return s
    })
  }, [])

  const loadTickets = useCallback((id) => api(`/tickets?trip_id=${id}`).then(setTickets).catch(() => {}), [])

  useEffect(() => { loadTrips() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!tripId) return
    setSeatData(null)
    loadSeats(tripId)
    loadTickets(tripId)
    const timer = setInterval(() => loadSeats(tripId).catch(() => {}), POLL_MS)
    return () => clearInterval(timer)
  }, [tripId, loadSeats, loadTickets])

  // ---- Reserva temporal del asiento (HU03) ----
  const clearHold = useCallback(() => {
    holdRef.current = null
    setHold(null)
  }, [])

  const releaseHold = useCallback(() => {
    const h = holdRef.current
    if (h) api(`/trips/${h.tripId}/holds/${h.seat}`, { method: 'DELETE' }).catch(() => {})
    clearHold()
  }, [clearHold])

  useEffect(() => releaseHold, [releaseHold]) // al salir de la taquilla se libera la reserva

  useEffect(() => {
    if (!hold) return
    const t = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(t)
  }, [hold])

  const remaining = hold ? Math.max(0, Math.ceil((hold.until - now) / 1000)) : 0
  useEffect(() => {
    if (hold && remaining === 0) {
      setMsg({ type: 'warn', text: `La reserva del asiento ${hold.seat} expiró. Selecciónalo de nuevo.` })
      clearHold()
      setSeat(null)
    }
  }, [hold, remaining, clearHold])

  const pickSeat = async (n) => {
    setMsg(null)
    if (n === null) {
      releaseHold()
      setSeat(null)
      return
    }
    try {
      const h = await api(`/trips/${tripId}/holds`, { method: 'POST', body: { seat_number: n } })
      holdRef.current = { tripId, seat: n }
      setNow(Date.now())
      setHold({ seat: n, until: Date.now() + h.expires_in * 1000 })
      setSeat(n)
    } catch (err) {
      setMsg({ type: 'error', text: errMsg(err) })
      loadSeats(tripId)
    }
  }

  const selectTrip = (id) => {
    releaseHold()
    setTripId(id)
    setSeat(null)
    setMsg(null)
    // En celular/tablet la grilla queda debajo de la lista: se desplaza hasta ella.
    if (window.innerWidth < 1024) setTimeout(() => sectionRef.current?.scrollIntoView({ behavior: 'smooth' }), 80)
  }

  const sell = async (e) => {
    e.preventDefault()
    setSelling(true)
    setMsg(null)
    try {
      const t = await api('/tickets', { method: 'POST', body: { trip_id: tripId, seat_number: seat, ...pax } })
      setTicket(t)
      clearHold() // el servidor consume la reserva al vender
      setSeat(null)
      setPax(EMPTY_PAX)
      setMsg({ type: 'success', text: `Tiquete vendido: asiento ${t.seat_number} para ${t.passenger_name}.` })
    } catch (err) {
      setMsg({ type: 'error', text: errMsg(err) })
      if (err.status === 409) { clearHold(); setSeat(null) }
    } finally {
      setSelling(false)
      loadSeats(tripId)
      loadTickets(tripId)
      loadTrips()
    }
  }

  const reprint = (uuid) => api(`/tickets/${uuid}`).then(setTicket).catch((e) => setMsg({ type: 'error', text: errMsg(e) }))
  const trip = seatData?.trip

  return (
    <div>
      <PageHeader title="Taquilla" subtitle="Selecciona un viaje, elige el asiento y registra al pasajero." />
      <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
        <aside className="min-w-0 space-y-4">
          <div className="card p-4">
            <TripSearchForm compact value={filters} onChange={setFilters} onSubmit={() => loadTrips()} />
          </div>
          <div className="card max-h-[45vh] divide-y divide-slate-100 overflow-y-auto lg:max-h-[60vh]">
            {!trips ? <Spinner /> : trips.length === 0 ? (
              <Empty icon={BusFront} title="Sin viajes disponibles">Cambia la fecha o los filtros.</Empty>
            ) : trips.map((t) => (
              <button key={t.id} onClick={() => selectTrip(t.id)}
                className={`flex w-full items-center justify-between gap-2 p-3 text-left transition hover:bg-slate-50 ${t.id === tripId ? 'border-l-4 border-indigo-600 bg-indigo-50' : 'border-l-4 border-transparent'}`}>
                <TripSummary trip={t} />
                <AvailabilityBadge trip={t} />
              </button>
            ))}
          </div>
        </aside>

        <section ref={sectionRef} className="min-w-0 scroll-mt-20 space-y-4">
          {msg && <Alert type={msg.type} onClose={() => setMsg(null)}>{msg.text}</Alert>}
          {!tripId ? (
            <div className="card"><Empty icon={Ticket} title="Ningún viaje seleccionado">Elige un viaje de la lista para ver sus asientos.</Empty></div>
          ) : !trip ? <div className="card"><Spinner /></div> : (
            <>
              <div className="card flex flex-wrap items-center justify-between gap-3 p-4">
                <div>
                  <p className="text-xs text-slate-500">{trip.company_name} · Placa {trip.bus_plate || '—'} · {dayLabel(trip.departure_at)}</p>
                  <p className="text-lg font-extrabold text-slate-900 sm:text-xl">{trip.origin} → {trip.destination} · {hour(trip.departure_at)}</p>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <span className="flex items-center gap-1 text-slate-500"><RefreshCw size={14} className="animate-spin [animation-duration:3s]" /> En vivo</span>
                  <span className="badge bg-indigo-100 text-indigo-700">{trip.available} libres de {trip.bus_capacity}</span>
                </div>
              </div>

              <div className="grid gap-4 xl:grid-cols-[auto_1fr]">
                <div className="card flex justify-center p-4 xl:block"><SeatGrid seats={seatData.seats} selected={seat} onSelect={pickSeat} /></div>
                <form onSubmit={sell} className="card space-y-4 p-4">
                  <h3 className="flex items-center gap-2 font-bold"><UserRound size={18} /> Datos del pasajero</h3>
                  {seat ? (
                    <div className="space-y-1 rounded-lg bg-indigo-50 p-3 text-sm">
                      <p>Asiento seleccionado: <b className="text-indigo-700">#{seat}</b> · Valor: <b>{money(trip.fare)}</b></p>
                      {hold && (
                        <p className={`flex items-center gap-1.5 text-xs font-semibold ${remaining <= 30 ? 'text-rose-600' : 'text-indigo-600'}`}>
                          <Lock size={13} /> Reservado para ti · expira en {Math.floor(remaining / 60)}:{String(remaining % 60).padStart(2, '0')}
                        </p>
                      )}
                    </div>
                  ) : <Alert type="info">Selecciona un asiento libre en la grilla.</Alert>}
                  <div>
                    <label className="label">Nombre completo *</label>
                    <input className="input" required minLength={3} value={pax.passenger_name}
                      onChange={(e) => setPax({ ...pax, passenger_name: e.target.value })} />
                  </div>
                  <div>
                    <label className="label">Documento de identidad *</label>
                    <input className="input" required minLength={5} inputMode="numeric" value={pax.passenger_doc}
                      onChange={(e) => setPax({ ...pax, passenger_doc: e.target.value })} />
                  </div>
                  <button className="btn btn-primary w-full py-3" disabled={!seat || selling}>
                    <Ticket size={18} /> {selling ? 'Procesando...' : seat ? `Vender asiento ${seat} · ${money(trip.fare)}` : 'Vender tiquete'}
                  </button>
                </form>
              </div>

              <div className="card overflow-hidden">
                <div className="border-b border-slate-200 px-4 py-3 font-bold">Pasajeros del viaje ({tickets.length})</div>
                {tickets.length === 0 ? <p className="p-4 text-sm text-slate-500">Aún no hay tiquetes vendidos.</p> : (
                  <div className="max-h-80 overflow-auto">
                    <table className="w-full">
                      <thead className="bg-slate-50"><tr><th className="th">Asiento</th><th className="th">Pasajero</th><th className="th">Documento</th><th className="th">Estado</th><th className="th" /></tr></thead>
                      <tbody className="divide-y divide-slate-100">
                        {tickets.map((t) => (
                          <tr key={t.uuid}>
                            <td className="td font-bold">{t.seat_number}</td>
                            <td className="td">{t.passenger_name}</td>
                            <td className="td">{t.passenger_doc}</td>
                            <td className="td"><StatusBadge status={t.status} /></td>
                            <td className="td text-right"><button className="btn btn-ghost btn-sm" onClick={() => reprint(t.uuid)}><Printer size={14} /> Ver</button></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </>
          )}
        </section>
      </div>
      <TicketModal ticket={ticket} onClose={() => setTicket(null)} />
    </div>
  )
}
