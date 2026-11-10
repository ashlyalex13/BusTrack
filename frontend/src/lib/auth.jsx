import { createContext, useContext, useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { api, getToken, setToken } from './api.js'
import { Spinner } from '../components/ui.jsx'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(!!getToken())

  useEffect(() => {
    if (getToken()) {
      api('/auth/me')
        .then(setUser)
        .catch(() => setToken(null))
        .finally(() => setLoading(false))
    }
    const onLogout = () => setUser(null)
    window.addEventListener('auth:logout', onLogout)
    return () => window.removeEventListener('auth:logout', onLogout)
  }, [])

  const login = async (email, password) => {
    const r = await api('/auth/login', { method: 'POST', body: { email, password } })
    setToken(r.access_token)
    setUser(r.user)
    return r.user
  }
  const logout = () => {
    setToken(null)
    setUser(null)
  }

  return <AuthCtx.Provider value={{ user, loading, login, logout }}>{children}</AuthCtx.Provider>
}

export const useAuth = () => useContext(AuthCtx)

export function RequireRole({ roles, children }) {
  const { user, loading } = useAuth()
  if (loading) return <Spinner />
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />
  return children
}
