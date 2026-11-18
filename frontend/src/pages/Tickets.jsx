import { useState } from 'react'
import { Ban, Printer, Search, SearchX } from 'lucide-react'
import { api } from '../lib/api.js'
import { useAuth } from '../lib/auth.jsx'
import { dayLabel, errMsg, hour, money } from '../lib/format.js'
import TicketModal from '../components/TicketModal.jsx'
import { Alert, Empty, PageHeader, Spinner, StatusBadge } from '../components/ui.jsx'

/** Consulta de tiquetes por pasajero: reimpresión y anulación (solo administrador). */
export default function Tickets() {
  const { user } = useAuth()
  const [q, setQ] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState(null)
  const [ticket, setTicket] = useState(null)

  const search = async (e) => {
    e?.preventDefault()
    if (q.trim().length < 3) return setMsg({ type: 'warn', text: 'Escribe al menos 3 caracteres.' })
    setLoading(true)
    setMsg(null)
    try {
      setResults(await api(`/tickets/search?q=${encodeURIComponent(q.trim())}`))
    } catch (err) {
      setMsg({ type: 'error', text: errMsg(err) })
    } finally {
      setLoading(false)
    }
  }

  const cancel = async (t) => {
    if (!window.confirm(`¿Anular el tiquete del asiento ${t.seat_number} de ${t.passenger_name}? El asiento quedará libre.`)) return
    try {
      await api(`/tickets/${t.uuid}/cancel`, { method: 'POST' })
      setMsg({ type: 'success', text: `Tiquete de ${t.passenger_name} anulado. El asiento ${t.seat_number} quedó libre.` })
      search()
    } catch (err) {
      setMsg({ type: 'error', text: errMsg(err) })
    }
  }

  const view = (uuid) => api(`/tickets/${uuid}`).then(setTicket).catch((e) => setMsg({ type: 'error', text: errMsg(e) }))

  return (
    <div>
      <PageHeader title="Consulta de tiquetes" subtitle="Busca por documento o nombre del pasajero para reimprimir o anular." />
      <form onSubmit={search} className="card mb-4 flex flex-wrap gap-2 p-4">
        <input className="input min-w-0 flex-1" autoFocus placeholder="Documento o nombre del pasajero" value={q}
          onChange={(e) => setQ(e.target.value)} />
        <button className="btn btn-primary"><Search size={16} /> Buscar</button>
      </form>
      {msg && <div className="mb-4"><Alert type={msg.type} onClose={() => setMsg(null)}>{msg.text}</Alert></div>}

      {loading ? <Spinner /> : results && (
        <div className="card overflow-hidden">
          {results.length === 0 ? <Empty icon={SearchX} title="Sin resultados">No hay tiquetes para “{q}”.</Empty> : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50"><tr>
                  <th className="th">Pasajero</th><th className="th">Viaje</th><th className="th">Asiento</th>
                  <th className="th">Valor</th><th className="th">Estado</th><th className="th" />
                </tr></thead>
                <tbody className="divide-y divide-slate-100">
                  {results.map((t) => (
                    <tr key={t.uuid} className="hover:bg-slate-50">
                      <td className="td"><p className="font-semibold">{t.passenger_name}</p><p className="text-xs text-slate-500">{t.passenger_doc}</p></td>
                      <td className="td whitespace-nowrap">
                        <p>{t.trip.origin} → {t.trip.destination}</p>
                        <p className="text-xs text-slate-500">{dayLabel(t.trip.departure_at)} · {hour(t.trip.departure_at)} · {t.trip.company_name}</p>
                      </td>
                      <td className="td font-bold">{t.seat_number}</td>
                      <td className="td">{money(t.price)}</td>
                      <td className="td"><StatusBadge status={t.status} /></td>
                      <td className="td whitespace-nowrap text-right">
                        <button className="btn btn-ghost btn-sm" onClick={() => view(t.uuid)}><Printer size={14} /> Ver</button>
                        {user.role === 'admin' && t.status === 'sold' && (
                          <button className="btn btn-sm ml-1 text-rose-600 hover:bg-rose-50" onClick={() => cancel(t)}><Ban size={14} /> Anular</button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      <TicketModal ticket={ticket} onClose={() => setTicket(null)} />
    </div>
  )
}
