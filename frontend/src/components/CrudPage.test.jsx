import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import CrudPage from './CrudPage.jsx'
import { api, ApiError } from '../lib/api.js'

vi.mock('../lib/api.js', async (importOriginal) => ({ ...(await importOriginal()), api: vi.fn() }))

// Misma configuración que la pantalla de Rutas del administrador (HU02).
const props = {
  title: 'Rutas y tarifas', baseUrl: '/routes', entity: 'ruta',
  emptyForm: { origin: '', destination: '', base_fare: '' },
  toPayload: (f) => ({ ...f, base_fare: Number(f.base_fare) }),
  columns: [{ label: 'Origen', key: 'origin' }, { label: 'Destino', key: 'destination' }],
  fields: [
    { name: 'origin', label: 'Origen', required: true },
    { name: 'destination', label: 'Destino', required: true },
    { name: 'base_fare', label: 'Tarifa', type: 'number', required: true },
  ],
}

describe('CrudPage (pantallas de administración, RF01)', () => {
  beforeEach(() => api.mockReset())

  it('lista los registros que devuelve la API', async () => {
    api.mockResolvedValue([{ id: 1, origin: 'Cali', destination: 'Buga' }])
    render(<CrudPage {...props} />)
    expect(await screen.findByText('Cali')).toBeInTheDocument()
    expect(api).toHaveBeenCalledWith('/routes')
  })

  it('crea un registro con el formulario y recarga la lista', async () => {
    api.mockResolvedValueOnce([]).mockResolvedValueOnce({ id: 2 }).mockResolvedValueOnce([{ id: 2, origin: 'Cali', destination: 'Tuluá' }])
    const user = userEvent.setup()
    render(<CrudPage {...props} />)
    await user.click(await screen.findByRole('button', { name: /Nuevo ruta/ }))
    await user.type(screen.getByLabelText(/Origen/), 'Cali')
    await user.type(screen.getByLabelText(/Destino/), 'Tuluá')
    await user.type(screen.getByLabelText(/Tarifa/), '22000')
    await user.click(screen.getByRole('button', { name: 'Guardar' }))

    expect(api).toHaveBeenCalledWith('/routes', { method: 'POST', body: { origin: 'Cali', destination: 'Tuluá', base_fare: 22000 } })
    expect(await screen.findByText('Tuluá')).toBeInTheDocument()
  })

  it('muestra en el formulario el error de validación del servidor', async () => {
    api.mockResolvedValueOnce([]).mockRejectedValueOnce(new ApiError(422, 'El origen debe ser distinto del destino'))
    const user = userEvent.setup()
    render(<CrudPage {...props} />)
    await user.click(await screen.findByRole('button', { name: /Nuevo ruta/ }))
    await user.type(screen.getByLabelText(/Origen/), 'Cali')
    await user.type(screen.getByLabelText(/Destino/), 'Cali')
    await user.type(screen.getByLabelText(/Tarifa/), '1000')
    await user.click(screen.getByRole('button', { name: 'Guardar' }))
    expect(await screen.findByText('El origen debe ser distinto del destino')).toBeInTheDocument()
  })

  it('edita un registro existente con PUT', async () => {
    api.mockResolvedValueOnce([{ id: 7, origin: 'Cali', destination: 'Buga', base_fare: 15000 }]).mockResolvedValue([])
    const user = userEvent.setup()
    render(<CrudPage {...props} />)
    const row = (await screen.findByText('Buga')).closest('tr')
    await user.click(within(row).getByRole('button', { name: /Editar/ }))
    expect(screen.getByLabelText(/Origen/)).toHaveValue('Cali')
    await user.click(screen.getByRole('button', { name: 'Guardar' }))
    expect(api).toHaveBeenCalledWith('/routes/7', expect.objectContaining({ method: 'PUT' }))
  })
})
