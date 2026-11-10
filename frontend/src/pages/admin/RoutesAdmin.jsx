import CrudPage from '../../components/CrudPage.jsx'
import { duration, money } from '../../lib/format.js'

/** HU02: rutas y tarifas. */
export default function RoutesAdmin() {
  return (
    <CrudPage
      title="Rutas y tarifas" subtitle="La tarifa de la ruta se aplica a cada tiquete vendido."
      baseUrl="/routes" entity="ruta"
      emptyForm={{ origin: '', destination: '', base_fare: '', duration_minutes: 60 }}
      toPayload={(f) => ({ origin: f.origin, destination: f.destination, base_fare: Number(f.base_fare), duration_minutes: Number(f.duration_minutes) })}
      columns={[
        { label: 'Origen', render: (r) => <span className="font-semibold">{r.origin}</span> },
        { label: 'Destino', render: (r) => <span className="font-semibold">{r.destination}</span> },
        { label: 'Duración', render: (r) => duration(r.duration_minutes) },
        { label: 'Tarifa', render: (r) => <span className="font-semibold text-emerald-700">{money(r.base_fare)}</span> },
      ]}
      fields={[
        { name: 'origin', label: 'Ciudad de origen', required: true },
        { name: 'destination', label: 'Ciudad de destino', required: true, help: 'Debe ser distinta del origen.' },
        { name: 'base_fare', label: 'Tarifa (COP)', type: 'number', min: 1, step: 100, required: true },
        { name: 'duration_minutes', label: 'Duración estimada (minutos)', type: 'number', min: 1, required: true },
      ]}
    />
  )
}
