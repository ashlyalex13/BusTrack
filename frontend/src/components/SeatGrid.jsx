import { Armchair } from 'lucide-react'

/** Grilla visual del bus: 2 asientos + pasillo + 2 asientos por fila (RF08). */
export default function SeatGrid({ seats, selected, onSelect }) {
  const rows = []
  for (let i = 0; i < seats.length; i += 4) rows.push(seats.slice(i, i + 4))

  const cell = (s) => {
    const isSel = s.number === selected
    const free = s.status === 'free'
    const cls = free
      ? isSel
        ? 'border-indigo-700 bg-indigo-600 text-white ring-4 ring-indigo-200 scale-105'
        : 'border-emerald-400 bg-white text-emerald-700 hover:bg-emerald-50 hover:-translate-y-0.5'
      : s.status === 'boarded'
        ? 'border-slate-500 bg-slate-500 text-white'
        : 'border-slate-300 bg-slate-300 text-slate-500'
    return (
      <button
        key={s.number} type="button" disabled={!free || !onSelect}
        onClick={() => onSelect(isSel ? null : s.number)}
        title={free ? `Asiento ${s.number} libre` : `Asiento ${s.number} ocupado`}
        className={`h-11 w-11 rounded-lg border-2 text-sm font-bold transition disabled:cursor-not-allowed ${cls}`}
      >
        {s.number}
      </button>
    )
  }

  return (
    <div>
      <div className="inline-block rounded-[2rem] border-2 border-slate-300 bg-slate-100 p-4">
        <div className="mb-4 flex items-center justify-between border-b border-dashed border-slate-300 pb-3 text-xs text-slate-500">
          <span className="flex items-center gap-1 rounded bg-slate-300 px-2 py-1 font-medium"><Armchair size={14} /> Conductor</span>
          <span className="font-medium">FRENTE</span>
        </div>
        <div className="space-y-2">
          {rows.map((r, i) => (
            <div key={i} className="flex gap-2">
              {r.slice(0, 2).map(cell)}
              <div className="w-5" />
              {r.slice(2).map(cell)}
            </div>
          ))}
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-600">
        <Legend cls="border-emerald-400 bg-white" label="Libre" />
        <Legend cls="border-indigo-700 bg-indigo-600" label="Seleccionado" />
        <Legend cls="border-slate-300 bg-slate-300" label="Vendido" />
        <Legend cls="border-slate-500 bg-slate-500" label="Abordado" />
      </div>
    </div>
  )
}

const Legend = ({ cls, label }) => (
  <span className="flex items-center gap-1.5"><span className={`h-4 w-4 rounded border-2 ${cls}`} />{label}</span>
)
