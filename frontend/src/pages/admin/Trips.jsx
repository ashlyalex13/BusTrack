import { useEffect, useState } from 'react'
import CrudPage from '../../components/CrudPage.jsx'
import { api } from '../../lib/api.js'
import { hour, todayISO } from '../../lib/format.js'
import { Occupancy, StatusBadge } from '../../components/ui.jsx'

/** RF01: programación de viajes. */
export default function Trips() {
  const [date, setDate] = useState(todayISO())
  const [routes, setRoutes] = useState([])
  const [companies, setCompanies] = useState([])

  useEffect(() => {
    api('/routes').then(setRoutes).catch(() => {})
    api('/companies').then(setCompanies).catch(() => {})
  }, [])

  return (
    <CrudPage
      title="Programación de viajes" subtitle="Viajes por fecha, bus asignado y estado."
      baseUrl="/trips" listUrl={`/trips?date=${date}`} entity="viaje"
      toolbar={<div><label className="label">Fecha</label><input type="date" className="input" value={date} onChange={(e) => setDate(e.target.value)} /></div>}
      emptyForm={{ route_id: '', company_id: '', departure_at: `${date}T08:00`, bus_capacity: 40, bus_plate: '', status: 'scheduled' }}
      toForm={(r) => ({ ...r, departure_at: r.departure_at.slice(0, 16), bus_plate: r.bus_plate ?? '' })}
      toPayload={(f) => ({
        route_id: Number(f.route_id), company_id: Number(f.company_id), departure_at: f.departure_at,
        bus_capacity: Number(f.bus_capacity), bus_plate: f.bus_plate || null, status: f.status,
      })}
      columns={[
        { label: 'Salida', render: (r) => <span className="font-semibold">{hour(r.departure_at)}</span> },
        { label: 'Ruta', render: (r) => <span className="whitespace-nowrap">{r.origin} → {r.destination}</span> },
        { label: 'Empresa', key: 'company_name' },
        { label: 'Placa', key: 'bus_plate' },
        { label: 'Ocupación', render: (r) => <Occupancy sold={r.sold} capacity={r.bus_capacity} /> },
        { label: 'Estado', render: (r) => <StatusBadge status={r.status} /> },
      ]}
      fields={[
        { name: 'route_id', label: 'Ruta', type: 'select', required: true, options: routes.map((r) => ({ value: r.id, label: `${r.origin} → ${r.destination}` })) },
        { name: 'company_id', label: 'Empresa', type: 'select', required: true, options: companies.filter((c) => c.is_active).map((c) => ({ value: c.id, label: c.name })) },
        { name: 'departure_at', label: 'Fecha y hora de salida', type: 'datetime-local', required: true },
        { name: 'bus_capacity', label: 'Capacidad del bus (asientos)', type: 'number', min: 4, required: true },
        { name: 'bus_plate', label: 'Placa del bus', placeholder: 'ABC123' },
        { name: 'status', label: 'Estado', type: 'select', required: true, options: [
          { value: 'scheduled', label: 'Programado' }, { value: 'departed', label: 'Despachado' }, { value: 'cancelled', label: 'Cancelado' }] },
      ]}
    />
  )
}
