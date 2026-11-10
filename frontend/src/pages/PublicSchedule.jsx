import { useEffect, useState } from 'react'
import { BusFront, ShieldCheck, Ticket, Timer } from 'lucide-react'
import { api } from '../lib/api.js'
import { dayLabel, errMsg, todayISO } from '../lib/format.js'
import { AvailabilityBadge, searchQuery, TripSearchForm, TripSummary } from '../components/TripSearch.jsx'
import { Alert, Empty, Spinner } from '../components/ui.jsx'

/** HU01: consulta pública de horarios, sin inicio de sesión. */
export default function PublicSchedule() {
  const [filters, setFilters] = useState({ origin: '', destination: '', date: todayISO() })
  const [trips, setTrips] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const search = async (f = filters) => {
    setLoading(true)
    setError('')
    try { setTrips(await api(searchQuery(f))) } catch (e) { setError(errMsg(e)) } finally { setLoading(false) }
  }
  useEffect(() => { search() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="space-y-6">
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-900 to-indigo-700 p-6 text-white shadow-lg sm:p-10">
        <BusFront className="absolute -right-6 -bottom-8 text-white/10" size={220} />
        <div className="relative max-w-2xl">
          <span className="badge bg-amber-400 text-slate-900">Terminal de Transportes</span>
          <h1 className="mt-3 text-3xl font-extrabold tracking-tight sm:text-4xl">Consulta horarios y disponibilidad en tiempo real</h1>
          <p className="mt-2 text-indigo-100">Busca tu ruta, revisa las salidas del día y acércate a la taquilla de tu empresa preferida.</p>
        </div>
        <div className="relative mt-6 rounded-xl bg-white p-4 text-slate-800 shadow-xl">
          <TripSearchForm value={filters} onChange={setFilters} onSubmit={() => search()} />
        </div>
      </section>

      <div className="grid gap-3 sm:grid-cols-3">
        {[[Timer, 'Información al minuto', 'Disponibilidad de asientos actualizada'],
          [Ticket, 'Compra en taquilla', 'Tiquete con código QR único'],
          [ShieldCheck, 'Viaje seguro', 'Tiquetes verificables contra fraude']].map(([Icon, t, d]) => (
          <div key={t} className="card flex items-center gap-3 p-4">
            <div className="grid h-10 w-10 place-items-center rounded-lg bg-indigo-50 text-indigo-600"><Icon size={20} /></div>
            <div><p className="text-sm font-semibold">{t}</p><p className="text-xs text-slate-500">{d}</p></div>
          </div>
        ))}
      </div>

      <section>
        <div className="mb-3 flex items-baseline justify-between">
          <h2 className="text-lg font-bold text-slate-900">Salidas · {dayLabel(`${filters.date}T00:00`)}</h2>
          {trips && <span className="text-sm text-slate-500">{trips.length} viajes</span>}
        </div>
        <Alert type="error">{error}</Alert>
        {loading ? <Spinner /> : trips && trips.length === 0 ? (
          <div className="card"><Empty icon={BusFront} title="No hay viajes disponibles">
            No encontramos salidas para esa ruta y fecha. Prueba con otra fecha o quita algún filtro.
          </Empty></div>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {trips?.map((t) => (
              <div key={t.id} className="card flex items-center justify-between gap-3 p-4 transition hover:shadow-md">
                <TripSummary trip={t} />
                <AvailabilityBadge trip={t} />
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
