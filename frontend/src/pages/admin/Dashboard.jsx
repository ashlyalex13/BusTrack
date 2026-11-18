import { useEffect, useState } from 'react'
import { Banknote, Bus, Download, Gauge, Ticket, UserRound } from 'lucide-react'
import { api } from '../../lib/api.js'
import { downloadCsv } from '../../lib/csv.js'
import { errMsg, hour, money, todayISO } from '../../lib/format.js'

const STATUS_ES = { scheduled: 'Programado', departed: 'Despachado', cancelled: 'Cancelado' }

function exportCsv(data) {
  const rows = data.trips.map((t) => [
    hour(t.departure_at), t.origin, t.destination, t.company_name, t.bus_plate || '', t.bus_capacity, t.sold,
    t.bus_capacity ? Math.round((t.sold * 100) / t.bus_capacity) : 0, t.revenue, STATUS_ES[t.status] || t.status,
  ])
  rows.push(['TOTAL', '', '', '', '', '', data.tickets_sold, data.occupancy, data.revenue, ''])
  downloadCsv(`bustrack-reporte-${data.date}.csv`,
    ['Hora', 'Origen', 'Destino', 'Empresa', 'Placa', 'Capacidad', 'Vendidos', 'Ocupación %', 'Recaudo', 'Estado'], rows)
}
import { Alert, Empty, Occupancy, PageHeader, Spinner, StatCard, StatusBadge } from '../../components/ui.jsx'

/** HU05: viajes del día y recaudo, filtrable por fecha. */
export default function Dashboard() {
  const [date, setDate] = useState(todayISO())
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    setData(null)
    api(`/reports/daily?date=${date}`).then(setData).catch((e) => setError(errMsg(e)))
  }, [date])

  return (
    <div className="space-y-6">
      <PageHeader title="Panel de operación" subtitle="Viajes del día, tiquetes vendidos y recaudo.">
        <div>
          <label className="label">Fecha del reporte</label>
          <input type="date" className="input" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>
        <button className="btn btn-ghost" disabled={!data || data.trips.length === 0} onClick={() => exportCsv(data)}>
          <Download size={16} /> Exportar CSV
        </button>
      </PageHeader>
      <Alert type="error">{error}</Alert>
      {!data ? <Spinner /> : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard icon={Bus} label="Viajes" value={data.trips_count} tone="sky" />
            <StatCard icon={Ticket} label="Tiquetes vendidos" value={data.tickets_sold} tone="indigo" />
            <StatCard icon={Banknote} label="Recaudo" value={money(data.revenue)} tone="emerald" />
            <StatCard icon={Gauge} label="Ocupación" value={`${data.occupancy}%`} tone="amber" />
          </div>

          <div className="grid gap-6 xl:grid-cols-[1fr_340px]">
            <div className="card overflow-hidden">
              <div className="border-b border-slate-200 px-4 py-3 font-bold">Viajes del día</div>
              {data.trips.length === 0 ? <Empty icon={Bus} title="No hay viajes en esta fecha" /> : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-slate-50"><tr>
                      <th className="th">Hora</th><th className="th">Ruta</th><th className="th">Empresa</th>
                      <th className="th">Ocupación</th><th className="th text-right">Recaudo</th><th className="th">Estado</th>
                    </tr></thead>
                    <tbody className="divide-y divide-slate-100">
                      {data.trips.map((t) => (
                        <tr key={t.id} className="hover:bg-slate-50">
                          <td className="td font-semibold">{hour(t.departure_at)}</td>
                          <td className="td whitespace-nowrap">{t.origin} → {t.destination}</td>
                          <td className="td">{t.company_name}</td>
                          <td className="td"><Occupancy sold={t.sold} capacity={t.bus_capacity} /></td>
                          <td className="td text-right font-semibold">{money(t.revenue)}</td>
                          <td className="td"><StatusBadge status={t.status} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="space-y-6">
            <div className="card h-fit overflow-hidden">
              <div className="border-b border-slate-200 px-4 py-3 font-bold">Recaudo por empresa</div>
              <div className="divide-y divide-slate-100">
                {data.by_company.map((c) => (
                  <div key={c.company} className="p-4">
                    <div className="flex justify-between font-semibold"><span>{c.company}</span><span>{money(c.revenue)}</span></div>
                    <p className="text-xs text-slate-500">{c.trips} viajes · {c.tickets} tiquetes</p>
                    <div className="mt-2 h-1.5 rounded-full bg-slate-100">
                      <div className="h-1.5 rounded-full bg-indigo-500" style={{ width: `${data.revenue ? (c.revenue * 100) / data.revenue : 0}%` }} />
                    </div>
                  </div>
                ))}
                {data.by_company.length === 0 && <p className="p-4 text-sm text-slate-500">Sin datos.</p>}
              </div>
            </div>

            <div className="card h-fit overflow-hidden">
              <div className="border-b border-slate-200 px-4 py-3 font-bold">Recaudo por taquillero</div>
              <div className="divide-y divide-slate-100">
                {(data.by_seller ?? []).map((s) => (
                  <div key={s.seller} className="flex items-center justify-between gap-2 p-4">
                    <div className="flex items-center gap-2">
                      <span className="grid h-8 w-8 place-items-center rounded-full bg-sky-100 text-sky-700"><UserRound size={16} /></span>
                      <div><p className="font-semibold">{s.seller}</p><p className="text-xs text-slate-500">{s.tickets} tiquetes</p></div>
                    </div>
                    <span className="font-semibold">{money(s.revenue)}</span>
                  </div>
                ))}
                {!data.by_seller?.length &&<p className="p-4 text-sm text-slate-500">Sin ventas.</p>}
              </div>
            </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
