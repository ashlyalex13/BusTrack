import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Verify from './Verify.jsx'
import { api } from '../lib/api.js'

// Se simula la API: la prueba se centra en lo que ve y hace el controlador de acceso.
vi.mock('../lib/api.js', () => ({ api: vi.fn() }))

const ticket = {
  passenger_name: 'Ana Torres', passenger_doc: '1010101', seat_number: 7, price: 15000, status: 'boarded',
  trip: { origin: 'Cali', destination: 'Buga', departure_at: '2030-05-10T21:00:00', company_name: 'Expreso Andino' },
}

describe('Verificar tiquete (HU04)', () => {
  beforeEach(() => api.mockReset())

  it('consulta el código y muestra un tiquete válido con sus datos', async () => {
    api.mockResolvedValue({ valid: true, message: 'Tiquete válido', ticket: { ...ticket, status: 'sold' } })
    render(<Verify />)
    await userEvent.type(screen.getByPlaceholderText(/firma/), 'uuid.firma')
    await userEvent.click(screen.getByRole('button', { name: /Consultar/ }))

    expect(api).toHaveBeenCalledWith('/tickets/verify?code=uuid.firma')
    expect(await screen.findByText('TIQUETE VÁLIDO')).toBeInTheDocument()
    expect(screen.getByText('Ana Torres')).toBeInTheDocument()
    expect(screen.getByText('#7')).toBeInTheDocument()
  })

  it('registra el abordaje con POST', async () => {
    api.mockResolvedValue({ valid: true, message: 'Abordaje registrado correctamente', ticket })
    render(<Verify />)
    await userEvent.type(screen.getByPlaceholderText(/firma/), 'uuid.firma')
    await userEvent.click(screen.getByRole('button', { name: /Validar y registrar abordaje/ }))

    expect(api).toHaveBeenCalledWith('/tickets/verify', { method: 'POST', body: { code: 'uuid.firma' } })
    expect(await screen.findByText('Abordaje registrado correctamente')).toBeInTheDocument()
  })

  it('muestra el rechazo y su motivo', async () => {
    api.mockResolvedValue({ valid: false, message: 'Firma inválida: el código fue alterado', ticket: null })
    render(<Verify />)
    await userEvent.type(screen.getByPlaceholderText(/firma/), 'uuid.alterada{Enter}')
    expect(await screen.findByText('TIQUETE RECHAZADO')).toBeInTheDocument()
    expect(screen.getByText('Firma inválida: el código fue alterado')).toBeInTheDocument()
  })

  it('no consulta si el campo está vacío', async () => {
    render(<Verify />)
    await userEvent.click(screen.getByRole('button', { name: /Consultar/ }))
    expect(api).not.toHaveBeenCalled()
  })
})
