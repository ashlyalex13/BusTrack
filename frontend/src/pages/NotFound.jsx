import { Link, useLocation } from 'react-router-dom'
import { CalendarClock, MapPinOff } from 'lucide-react'

/** Página 404: la ruta solicitada no existe. */
export default function NotFound() {
  const { pathname } = useLocation()
  return (
    <div className="flex justify-center py-10">
      <div className="card w-full max-w-md p-8 text-center">
        <div className="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-full bg-slate-100 text-slate-400"><MapPinOff size={30} /></div>
        <p className="text-5xl font-extrabold text-slate-900">404</p>
        <h1 className="mt-2 text-lg font-bold text-slate-800">Esta ruta no tiene salidas</h1>
        <p className="mt-1 text-sm text-slate-500">La página <span className="break-all font-mono">{pathname}</span> no existe o fue movida.</p>
        <Link to="/" className="btn btn-primary mt-6"><CalendarClock size={16} /> Ir a los horarios</Link>
      </div>
    </div>
  )
}
