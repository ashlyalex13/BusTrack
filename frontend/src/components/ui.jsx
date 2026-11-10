import { CircleAlert, CircleCheck, Info, Loader2, X } from 'lucide-react'

export function Spinner({ label = 'Cargando...' }) {
  return (
    <div className="flex items-center justify-center gap-2 py-10 text-sm text-slate-500">
      <Loader2 className="animate-spin" size={18} /> {label}
    </div>
  )
}

export function PageHeader({ title, subtitle, children }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
      </div>
      {children && <div className="flex flex-wrap items-end gap-2">{children}</div>}
    </div>
  )
}

const ALERT = {
  error: ['border-rose-200 bg-rose-50 text-rose-800', CircleAlert],
  warn: ['border-amber-200 bg-amber-50 text-amber-800', CircleAlert],
  success: ['border-emerald-200 bg-emerald-50 text-emerald-800', CircleCheck],
  info: ['border-sky-200 bg-sky-50 text-sky-800', Info],
}

export function Alert({ type = 'info', children, onClose }) {
  if (!children) return null
  const [cls, Icon] = ALERT[type]
  return (
    <div className={`flex items-start gap-2 rounded-lg border px-3 py-2.5 text-sm ${cls}`}>
      <Icon size={18} className="mt-0.5 shrink-0" />
      <div className="flex-1">{children}</div>
      {onClose && <button onClick={onClose} className="opacity-60 hover:opacity-100"><X size={16} /></button>}
    </div>
  )
}

export function Empty({ icon: Icon, title, children }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 px-4 py-14 text-center">
      {Icon && <div className="grid h-14 w-14 place-items-center rounded-full bg-slate-100 text-slate-400"><Icon size={26} /></div>}
      <p className="font-semibold text-slate-700">{title}</p>
      {children && <p className="max-w-sm text-sm text-slate-500">{children}</p>}
    </div>
  )
}

export function Modal({ title, onClose, children, wide }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-slate-900/50 p-4 backdrop-blur-sm"
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className={`card mt-8 w-full ${wide ? 'max-w-2xl' : 'max-w-md'} p-5`}>
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-bold text-slate-900">{title}</h3>
          <button onClick={onClose} className="rounded p-1 text-slate-500 hover:bg-slate-100"><X size={18} /></button>
        </div>
        {children}
      </div>
    </div>
  )
}

const STATUS = {
  scheduled: ['Programado', 'bg-sky-100 text-sky-700'],
  departed: ['Despachado', 'bg-slate-200 text-slate-700'],
  cancelled: ['Cancelado', 'bg-rose-100 text-rose-700'],
  sold: ['Vendido', 'bg-emerald-100 text-emerald-700'],
  boarded: ['Abordado', 'bg-indigo-100 text-indigo-700'],
}

export function StatusBadge({ status }) {
  const [label, cls] = STATUS[status] || [status, 'bg-slate-100 text-slate-600']
  return <span className={`badge ${cls}`}>{label}</span>
}

export function Occupancy({ sold, capacity }) {
  const pct = capacity ? Math.round((sold * 100) / capacity) : 0
  const color = pct >= 90 ? 'bg-rose-500' : pct >= 60 ? 'bg-amber-400' : 'bg-emerald-500'
  return (
    <div className="min-w-28">
      <div className="mb-1 flex justify-between text-xs text-slate-500"><span>{sold}/{capacity}</span><span>{pct}%</span></div>
      <div className="h-1.5 rounded-full bg-slate-200"><div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} /></div>
    </div>
  )
}

export function StatCard({ icon: Icon, label, value, tone = 'indigo' }) {
  const tones = {
    indigo: 'bg-indigo-100 text-indigo-600', emerald: 'bg-emerald-100 text-emerald-600',
    amber: 'bg-amber-100 text-amber-600', sky: 'bg-sky-100 text-sky-600',
  }
  return (
    <div className="card flex items-center gap-4 p-5">
      <div className={`grid h-12 w-12 shrink-0 place-items-center rounded-xl ${tones[tone]}`}><Icon size={22} /></div>
      <div className="min-w-0">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
        <p className="text-xl font-extrabold break-words text-slate-900 xl:text-2xl">{value}</p>
      </div>
    </div>
  )
}
