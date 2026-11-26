import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { Bus, LogIn } from 'lucide-react'
import { useAuth } from '../lib/auth.jsx'
import { errMsg } from '../lib/format.js'
import { Alert } from '../components/ui.jsx'

export default function Login() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (user) return <Navigate to={user.role === 'admin' ? '/admin' : '/taquilla'} replace />

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const u = await login(form.email, form.password)
      navigate(u.role === 'admin' ? '/admin' : '/taquilla')
    } catch (err) {
      setError(errMsg(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex justify-center py-8">
      <div className="card w-full max-w-sm p-6">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 grid h-14 w-14 place-items-center rounded-2xl bg-slate-900 text-amber-400"><Bus size={28} /></div>
          <h1 className="text-xl font-extrabold">Ingreso al sistema</h1>
          <p className="text-sm text-slate-500">Administradores y taquilleros</p>
        </div>
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="label" htmlFor="login-email">Correo</label>
            <input id="login-email" className="input" type="email" required autoFocus autoComplete="username" value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
          <div>
            <label className="label" htmlFor="login-password">Contraseña</label>
            <input id="login-password" className="input" type="password" required autoComplete="current-password" value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </div>
          <Alert type="error">{error}</Alert>
          <button className="btn btn-primary w-full" disabled={loading}><LogIn size={16} /> {loading ? 'Ingresando...' : 'Ingresar'}</button>
        </form>
        <div className="mt-5 rounded-lg bg-slate-50 p-3 text-xs text-slate-500">
          <p className="mb-1 font-semibold text-slate-600">Usuarios de demostración</p>
          <p>admin@bustrack.co · admin123</p>
          <p>taquilla1@bustrack.co · taquilla123</p>
        </div>
      </div>
    </div>
  )
}
