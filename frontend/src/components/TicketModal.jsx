import { Bus, Printer } from 'lucide-react'
import { Modal, StatusBadge } from './ui.jsx'
import { dayLabel, hour, money } from '../lib/format.js'

export default function TicketModal({ ticket, onClose }) {
  if (!ticket) return null
  const t = ticket.trip
  const Row = ({ label, value }) => (
    <div><p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">{label}</p><p className="font-semibold text-slate-800">{value}</p></div>
  )
  return (
    <Modal title="Tiquete de viaje" onClose={onClose}>
      <div className="print-area">
        <div className="overflow-hidden rounded-xl border-2 border-dashed border-slate-300">
          <div className="flex items-center justify-between bg-slate-900 px-4 py-3 text-white">
            <span className="flex items-center gap-2 font-extrabold"><Bus size={18} className="text-amber-400" /> BusTrack</span>
            <StatusBadge status={ticket.status} />
          </div>
          <div className="space-y-4 p-4">
            <div className="flex items-end justify-between">
              <div>
                <p className="text-xs text-slate-500">{t.company_name}</p>
                <p className="text-xl font-extrabold text-slate-900">{t.origin} → {t.destination}</p>
                <p className="text-sm text-slate-600">{dayLabel(t.departure_at)} · {hour(t.departure_at)}</p>
              </div>
              <div className="rounded-lg bg-indigo-600 px-3 py-2 text-center text-white">
                <p className="text-[10px] uppercase">Asiento</p>
                <p className="text-2xl font-extrabold leading-none">{ticket.seat_number}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 border-t border-slate-200 pt-3 text-sm">
              <Row label="Pasajero" value={ticket.passenger_name} />
              <Row label="Documento" value={ticket.passenger_doc} />
              <Row label="Valor" value={money(ticket.price)} />
              <Row label="Placa" value={t.bus_plate || '—'} />
            </div>
            {ticket.qr_image && (
              <div className="flex flex-col items-center border-t border-slate-200 pt-3">
                <img src={ticket.qr_image} alt="Código QR del tiquete" className="h-44 w-44" />
                <p className="mt-1 break-all text-center font-mono text-[10px] text-slate-400">{ticket.code}</p>
              </div>
            )}
            <p className="text-center text-[11px] text-slate-400">Vendido por {ticket.seller_name} · Presente este código al abordar</p>
          </div>
        </div>
      </div>
      <div className="mt-4 flex justify-end gap-2">
        <button className="btn btn-ghost" onClick={onClose}>Cerrar</button>
        <button className="btn btn-primary" onClick={() => window.print()}><Printer size={16} /> Imprimir</button>
      </div>
    </Modal>
  )
}
