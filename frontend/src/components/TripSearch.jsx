import { useEffect, useState } from 'react'
import { ArrowRight, Clock, Search } from 'lucide-react'
import { api } from '../lib/api.js'
import { duration, hour, money } from '../lib/format.js'

/** Filtros origen / destino / fecha compartidos por el portal público y la taquilla. */
export function TripSearchForm({ value, onChange, onSubmit, compact }) {
  const [cities, setCities] = useState({ origins: [], destinations: [] })
  useEffect(() => { api('/trips/cities').then(setCities).catch(() => {}) }, [])
  const set = (k) => (e) => onChange({ ...value, [k]: e.target.value })

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit() }}
      className={`grid gap-3 ${compact ? 'grid-cols-2' : 'sm:grid-cols-2 lg:grid-cols-[1fr_1fr_1fr_auto]'}`}>
      <div>
        <label className="label">Origen</label>
        <select className="input" value={value.origin} onChange={set('origin')}>
          <option value="">Todos</option>
          {cities.origins.map((c) => <option key={c}>{c}</option>)}
        </select>
      </div>
      <div>
        <label className="label">Destino</label>
        <select className="input" value={value.destination} onChange={set('destination')}>
          <option value="">Todos</option>
          {cities.destinations.map((c) => <option key={c}>{c}</option>)}
        </select>
      </div>
      <div className={compact ? 'col-span-2' : ''}>
        <label className="label">Fecha</label>
        <input type="date" className="input" value={value.date} onChange={set('date')} />
      </div>
      <div className={`flex items-end ${compact ? 'col-span-2' : ''}`}>
        <button className="btn btn-primary w-full"><Search size={16} /> Buscar</button>
      </div>
    </form>
  )
}

export function searchQuery(f) {
  const p = new URLSearchParams()
  Object.entries(f).forEach(([k, v]) => v && p.set(k, v))
  return `/trips/search?${p}`
}

export function AvailabilityBadge({ trip }) {
  if (trip.available === 0) return <span className="badge shrink-0 bg-rose-100 text-rose-700">Agotado</span>
  const cls = trip.available <= 5 ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
  return (
    <span className={`badge shrink-0 ${cls}`} title={`${trip.available} asientos disponibles`}>
      {trip.available} <span className="hidden sm:inline">disponibles</span><span className="sm:hidden">libres</span>
    </span>
  )
}

export function TripSummary({ trip }) {
  // "09:00 p. m." → hora grande y "p. m." pequeño: ocupa un ancho fijo y nunca se parte en dos líneas.
  const [time, ...period] = hour(trip.departure_at).split(' ')
  return (
    <div className="flex min-w-0 flex-1 items-center gap-3">
      <div className="w-16 shrink-0 text-center">
        <div className="whitespace-nowrap text-lg font-extrabold leading-tight text-slate-900">{time}</div>
        <div className="whitespace-nowrap text-[11px] font-semibold uppercase text-slate-500">{period.join(' ')}</div>
      </div>
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-x-1.5 font-semibold text-slate-800">
          <span>{trip.origin}</span> <ArrowRight size={14} className="shrink-0 text-slate-400" /> <span>{trip.destination}</span>
        </div>
        <div className="truncate text-xs text-slate-500">{trip.company_name} · {money(trip.fare)}</div>
        <div className="flex items-center gap-1 text-xs text-slate-400"><Clock size={11} /> {duration(trip.duration_minutes)}</div>
      </div>
    </div>
  )
}
