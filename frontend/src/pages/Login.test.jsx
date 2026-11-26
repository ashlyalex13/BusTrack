import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Login from './Login.jsx'
import { AuthProvider } from '../lib/auth.jsx'
import { api, ApiError, getToken } from '../lib/api.js'

vi.mock('../lib/api.js', async (importOriginal) => ({ ...(await importOriginal()), api: vi.fn() }))

function renderLogin() {
  render(
    <AuthProvider>
      <MemoryRouter initialEntries={['/login']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/taquilla" element={<p>Pantalla de taquilla</p>} />
          <Route path="/admin" element={<p>Panel de administración</p>} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>,
  )
}

async function submit(email, password) {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText('Correo'), email)
  await user.type(screen.getByLabelText('Contraseña'), password)
  await user.click(screen.getByRole('button', { name: /Ingresar/ }))
}

describe('Inicio de sesión (RF04)', () => {
  beforeEach(() => api.mockReset())

  it.each([
    ['taquillero', 'Pantalla de taquilla'],
    ['admin', 'Panel de administración'],
  ])('un %s entra y va a su pantalla', async (role, screenText) => {
    api.mockResolvedValue({ access_token: 'token-123', user: { id: 1, name: 'Ana', role } })
    renderLogin()
    await submit('ana@bustrack.co', 'clave123')
    expect(api).toHaveBeenCalledWith('/auth/login', { method: 'POST', body: { email: 'ana@bustrack.co', password: 'clave123' } })
    expect(await screen.findByText(screenText)).toBeInTheDocument()
    expect(getToken()).toBe('token-123')
  })

  it('con credenciales incorrectas muestra el error y no guarda sesión', async () => {
    api.mockRejectedValue(new ApiError(401, 'Correo o contraseña incorrectos'))
    renderLogin()
    await submit('ana@bustrack.co', 'mala')
    expect(await screen.findByText('Correo o contraseña incorrectos')).toBeInTheDocument()
    expect(getToken()).toBeNull()
  })
})
