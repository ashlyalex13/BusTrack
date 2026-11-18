import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { Building2, Bus, CalendarClock, FileSearch, LayoutDashboard, LogIn, LogOut, Route as RouteIcon, ScanLine, Ticket, Users } from 'lucide-react'
import { useAuth } from '../lib/auth.jsx'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

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

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-800">
      <header className="sticky top-0 z-40 bg-slate-900 text-white shadow">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3">
          <Link to="/" className="flex items-center gap-2 text-lg font-extrabold tracking-tight">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-amber-400 text-slate-900"><Bus size={20} /></span>
            <span>Bus<span className="text-amber-400">Track</span></span>
          </Link>
          <nav className="order-3 -mx-1 flex w-full gap-1 overflow-x-auto md:order-none md:w-auto md:flex-1">
            {links.map((l) => (
              <NavLink
                key={l.to} to={l.to} end={l.end}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition ${
                    isActive ? 'bg-white/15 text-white' : 'text-slate-300 hover:bg-white/10 hover:text-white'}`}
              >
                <l.icon size={16} /> {l.label}
              </NavLink>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3">
            {user ? (
              <>
                <div className="text-right text-sm leading-tight">
                  <div className="font-semibold">{user.name}</div>
                  <div className="text-xs capitalize text-amber-300">{user.role}</div>
                </div>
                <button
                  onClick={() => { logout(); navigate('/') }}
                  className="rounded-lg p-2 text-slate-300 hover:bg-white/10 hover:text-white" title="Cerrar sesión"
                >
                  <LogOut size={18} />
                </button>
              </>
            ) : (
              <Link to="/login" className="btn btn-accent"><LogIn size={16} /> Ingresar</Link>
            )}
          </div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6">
        <Outlet />
      </main>
      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
        BusTrack · Sistema de gestión para terminales de transporte terrestre
      </footer>
    </div>
  )
}
