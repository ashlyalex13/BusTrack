import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  Building2, Bus, CalendarClock, FileSearch, LayoutDashboard, LogIn, LogOut, Menu, Route as RouteIcon, ScanLine,
  Ticket, Users, X,
} from 'lucide-react'
import ErrorBoundary from './ErrorBoundary.jsx'
import { useAuth } from '../lib/auth.jsx'

function useLinks(user) {
  const links = [{ to: '/', label: 'Horarios', icon: CalendarClock, end: true }]
  if (user) {
    links.push(
      { to: '/taquilla', label: 'Taquilla', icon: Ticket },
      { to: '/tiquetes', label: 'Tiquetes', icon: FileSearch },
      { to: '/verificar', label: 'Verificar QR', icon: ScanLine },
    )
    if (user.role === 'admin') {
      links.push(
        { to: '/admin', label: 'Panel', icon: LayoutDashboard, end: true },
        { to: '/admin/viajes', label: 'Viajes', icon: Bus },
        { to: '/admin/rutas', label: 'Rutas', icon: RouteIcon },
        { to: '/admin/empresas', label: 'Empresas', icon: Building2 },
        { to: '/admin/usuarios', label: 'Usuarios', icon: Users },
      )
    }
  }
  return links
}

const linkClass = ({ isActive }) =>
  `flex items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition xl:gap-1.5 xl:px-2.5 ${
    isActive ? 'bg-white/15 text-white' : 'text-slate-300 hover:bg-white/10 hover:text-white'}`

/**
 * Diseño general. En pantallas grandes (≥1280 px) el menú va en línea; en
 * celulares y tablets se abre con el botón de menú para no desbordar la pantalla.
 */
export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const links = useLinks(user)

  useEffect(() => setOpen(false), [location.pathname]) // al navegar se cierra el menú móvil

  const doLogout = () => { logout(); navigate('/') }

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-800">
      <header className="sticky top-0 z-40 bg-slate-900 text-white shadow">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3">
          <Link to="/" className="flex shrink-0 items-center gap-2 text-lg font-extrabold tracking-tight">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-amber-400 text-slate-900"><Bus size={20} /></span>
            <span>Bus<span className="text-amber-400">Track</span></span>
          </Link>

          <nav className="hidden min-w-0 flex-1 gap-0.5 xl:flex" aria-label="Menú principal">
            {links.map((l) => <NavLink key={l.to} to={l.to} end={l.end} className={linkClass}><l.icon size={16} /> {l.label}</NavLink>)}
          </nav>

          <div className="ml-auto flex items-center gap-2">
            {user ? (
              <>
                {/* Entre 1280 y 1535 px el menú ocupa casi todo el ancho: se muestra solo la inicial. */}
                <div className="hidden text-right text-sm leading-tight sm:block xl:hidden 2xl:block">
                  <div className="max-w-44 truncate font-semibold">{user.name}</div>
                  <div className="text-xs capitalize text-amber-300">{user.role}</div>
                </div>
                <span title={`${user.name} (${user.role})`}
                  className="hidden h-9 w-9 place-items-center rounded-full bg-amber-400 font-bold text-slate-900 xl:grid 2xl:hidden">
                  {user.name.charAt(0).toUpperCase()}
                </span>
                <button onClick={doLogout} className="hidden rounded-lg p-2 text-slate-300 hover:bg-white/10 hover:text-white xl:block" title="Cerrar sesión">
                  <LogOut size={18} />
                </button>
              </>
            ) : (
              <Link to="/login" className="btn btn-accent"><LogIn size={16} /> <span className="hidden sm:inline">Ingresar</span></Link>
            )}
            {(user || links.length > 1) && (
              <button
                onClick={() => setOpen((o) => !o)} aria-expanded={open} aria-label={open ? 'Cerrar menú' : 'Abrir menú'}
                className="rounded-lg p-2 text-slate-200 hover:bg-white/10 xl:hidden"
              >
                {open ? <X size={22} /> : <Menu size={22} />}
              </button>
            )}
          </div>
        </div>

        {open && (
          <nav className="border-t border-white/10 px-4 pb-4 pt-2 xl:hidden" aria-label="Menú móvil">
            {user && (
              <div className="mb-2 border-b border-white/10 px-3 pb-3 sm:hidden">
                <p className="font-semibold">{user.name}</p>
                <p className="text-xs capitalize text-amber-300">{user.role}</p>
              </div>
            )}
            <div className="grid gap-1 sm:grid-cols-2 md:grid-cols-3">
              {links.map((l) => <NavLink key={l.to} to={l.to} end={l.end} className={linkClass}><l.icon size={18} /> {l.label}</NavLink>)}
            </div>
            {user && (
              <button onClick={doLogout} className="mt-2 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-rose-300 hover:bg-white/10">
                <LogOut size={18} /> Cerrar sesión
              </button>
            )}
          </nav>
        )}
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6">
        {/* key: al cambiar de pantalla se reinicia el estado de error */}
        <ErrorBoundary key={location.pathname}><Outlet /></ErrorBoundary>
      </main>
      <footer className="border-t border-slate-200 bg-white px-4 py-4 text-center text-xs text-slate-500">
        BusTrack · Sistema de gestión para terminales de transporte terrestre
      </footer>
    </div>
  )
}
