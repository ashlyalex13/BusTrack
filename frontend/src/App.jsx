import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider, RequireRole } from './lib/auth.jsx'
import Layout from './components/Layout.jsx'
import PublicSchedule from './pages/PublicSchedule.jsx'
import Login from './pages/Login.jsx'
import Taquilla from './pages/Taquilla.jsx'
import Verify from './pages/Verify.jsx'
import Tickets from './pages/Tickets.jsx'
import NotFound from './pages/NotFound.jsx'
import Dashboard from './pages/admin/Dashboard.jsx'
import Companies from './pages/admin/Companies.jsx'
import RoutesAdmin from './pages/admin/RoutesAdmin.jsx'
import Trips from './pages/admin/Trips.jsx'
import Users from './pages/admin/Users.jsx'

const STAFF = ['admin', 'taquillero']
const ADMIN = ['admin']
const guard = (roles, el) => <RequireRole roles={roles}>{el}</RequireRole>

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<PublicSchedule />} />
            <Route path="login" element={<Login />} />
            <Route path="taquilla" element={guard(STAFF, <Taquilla />)} />
            <Route path="verificar" element={guard(STAFF, <Verify />)} />
            <Route path="tiquetes" element={guard(STAFF, <Tickets />)} />
            <Route path="admin" element={guard(ADMIN, <Dashboard />)} />
            <Route path="admin/viajes" element={guard(ADMIN, <Trips />)} />
            <Route path="admin/rutas" element={guard(ADMIN, <RoutesAdmin />)} />
            <Route path="admin/empresas" element={guard(ADMIN, <Companies />)} />
            <Route path="admin/usuarios" element={guard(ADMIN, <Users />)} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
