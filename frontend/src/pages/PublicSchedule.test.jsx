import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import PublicSchedule from './PublicSchedule.jsx'
import { api } from '../lib/api.js'

vi.mock('../lib/api.js', async (importOriginal) => ({ ...(await importOriginal()), api: vi.fn() }))

const trip = {
  id: 1, origin: 'Cali', destination: 'Bogotá', company_name: 'Rápido Pacífico', departure_at: '2030-05-10T21:00:00',
  duration_minutes: 600, fare: 85000, available: 12,
}

function mockApi(trips) {
  api.mockImplementation((path) => {
    if (path === '/trips/cities') return Promise.resolve({ origins: ['Cali'], destinations: ['Bogotá', 'Buga'] })
    return Promise.resolve(trips)
  })
}

describe('Portal público de horarios (HU01)', () => {
  beforeEach(() => api.mockReset())

  it('muestra las salidas con empresa, tarifa y asientos disponibles', async () => {
    mockApi([trip])
    render(<PublicSchedule />)
    expect(await screen.findByText(/Rápido Pacífico/)).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('1 viajes')).toBeInTheDocument()
  })

  it('busca por origen y destino', async () => {
    mockApi([trip])
    const user = userEvent.setup()
    render(<PublicSchedule />)
    await screen.findByRole('option', { name: 'Bogotá' })
    await user.selectOptions(screen.getByLabelText('Origen'), 'Cali')
    await user.selectOptions(screen.getByLabelText('Destino'), 'Bogotá')
    await user.click(screen.getByRole('button', { name: /Buscar/ }))
    expect(api).toHaveBeenLastCalledWith(expect.stringMatching(/^\/trips\/search\?origin=Cali&destination=Bogot%C3%A1&date=/))
  })

  it('si no hay viajes muestra un mensaje claro', async () => {
    mockApi([])
    render(<PublicSchedule />)
    expect(await screen.findByText('No hay viajes disponibles')).toBeInTheDocument()
  })
})
