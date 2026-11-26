import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Taquilla from './Taquilla.jsx'
import { api, ApiError } from '../lib/api.js'

// API simulada: la prueba recorre el flujo de venta tal como lo hace el taquillero (HU03).
vi.mock('../lib/api.js', async (importOriginal) => ({ ...(await importOriginal()), api: vi.fn() }))

const trip = {
  id: 1, origin: 'Cali', destination: 'Buga', company_name: 'Expreso Andino', departure_at: '2030-05-10T21:00:00',
  duration_minutes: 75, fare: 15000, available: 3, bus_capacity: 4, bus_plate: 'ABC123', status: 'scheduled',
}
const seats = [
  { number: 1, status: 'sold' }, { number: 2, status: 'free' }, { number: 3, status: 'reserved' }, { number: 4, status: 'free' },
]
const soldTicket = {
  uuid: 'u-1', code: 'u-1.firma', qr_image: 'data:image/png;base64,AAAA', seat_number: 4, passenger_name: 'Ana Torres',
  passenger_doc: '1010101', price: 15000, status: 'sold', seller_name: 'Laura Gómez', trip,
}

function mockApi({ sale } = {}) {
  api.mockImplementation((path, options = {}) => {
    const method = options.method || 'GET'
    if (path === '/trips/cities') return Promise.resolve({ origins: ['Cali'], destinations: ['Buga'] })
    if (path.startsWith('/trips/search')) return Promise.resolve([trip])
    if (path === '/trips/1/seats') return Promise.resolve({ trip, seats })
    if (path.startsWith('/tickets?trip_id=1')) return Promise.resolve([])
    if (path === '/trips/1/holds' && method === 'POST') return Promise.resolve({ trip_id: 1, seat_number: options.body.seat_number, expires_in: 120 })
    if (path.startsWith('/trips/1/holds/') && method === 'DELETE') return Promise.resolve(null)
    if (path === '/tickets' && method === 'POST') return sale ? sale() : Promise.resolve(soldTicket)
    return Promise.reject(new Error(`ruta no simulada: ${method} ${path}`))
  })
}

async function openTripAndPickSeat(user) {
  render(<Taquilla />)
  await user.click(await screen.findByRole('button', { name: /Cali.*Buga/ }))
  await user.click(await screen.findByRole('button', { name: '4' }))
}

describe('Taquilla: venta de tiquete', () => {
  beforeEach(() => api.mockReset())

  it('lista los viajes y muestra la grilla del viaje elegido', async () => {
    mockApi()
    const user = userEvent.setup()
    render(<Taquilla />)
    await user.click(await screen.findByRole('button', { name: /Cali.*Buga/ }))
    expect(await screen.findByRole('button', { name: '1' })).toBeDisabled() // vendido
    expect(screen.getByRole('button', { name: '2' })).toBeEnabled()
    expect(screen.getByText('3 libres de 4')).toBeInTheDocument()
  })

  it('al elegir un asiento lo reserva y muestra la cuenta regresiva', async () => {
    mockApi()
    const user = userEvent.setup()
    await openTripAndPickSeat(user)
    expect(api).toHaveBeenCalledWith('/trips/1/holds', { method: 'POST', body: { seat_number: 4 } })
    // La cuenta regresiva corre en tiempo real: en un equipo lento ya pudo bajar unos segundos.
    expect(await screen.findByText(/Reservado para ti · expira en (2:00|1:[45]\d)/)).toBeInTheDocument()
  })

  it('vende el tiquete y muestra el tiquete con QR', async () => {
    mockApi()
    const user = userEvent.setup()
    await openTripAndPickSeat(user)
    await user.type(screen.getByLabelText(/Nombre completo/), 'Ana Torres')
    await user.type(screen.getByLabelText(/Documento de identidad/), '1010101')
    await user.click(screen.getByRole('button', { name: /Vender asiento 4/ }))

    expect(api).toHaveBeenCalledWith('/tickets', {
      method: 'POST', body: { trip_id: 1, seat_number: 4, passenger_name: 'Ana Torres', passenger_doc: '1010101' },
    })
    const modal = await screen.findByText('Tiquete de viaje')
    expect(modal).toBeInTheDocument()
    expect(screen.getByAltText('Código QR del tiquete')).toBeInTheDocument()
    expect(screen.getByText(/Tiquete vendido: asiento 4 para Ana Torres/)).toBeInTheDocument()
  })

  it('si otra taquilla vendió el asiento muestra el error del servidor', async () => {
    mockApi({ sale: () => Promise.reject(new ApiError(409, 'El asiento 4 ya fue vendido')) })
    const user = userEvent.setup()
    await openTripAndPickSeat(user)
    await user.type(screen.getByLabelText(/Nombre completo/), 'Ana Torres')
    await user.type(screen.getByLabelText(/Documento de identidad/), '1010101')
    await user.click(screen.getByRole('button', { name: /Vender asiento 4/ }))

    expect(await screen.findByText('El asiento 4 ya fue vendido')).toBeInTheDocument()
    expect(screen.queryByText(/Reservado para ti/)).toBeNull() // se limpia la selección
    expect(screen.getByRole('button', { name: /Vender tiquete/ })).toBeDisabled()
  })
})
