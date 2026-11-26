import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError, getToken, setToken } from './api.js'

function mockFetch(status, body) {
  const fetchMock = vi.fn().mockResolvedValue({
    status,
    ok: status >= 200 && status < 300,
    json: () => (body === undefined ? Promise.reject(new Error('sin cuerpo')) : Promise.resolve(body)),
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

describe('cliente de la API', () => {
  beforeEach(() => vi.unstubAllGlobals())

  it('envía el token y el cuerpo en JSON', async () => {
    setToken('abc123')
    const fetchMock = mockFetch(201, { ok: true })
    await api('/tickets', { method: 'POST', body: { seat_number: 4 } })
    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/tickets')
    expect(options.headers.Authorization).toBe('Bearer abc123')
    expect(options.headers['Content-Type']).toBe('application/json')
    expect(JSON.parse(options.body)).toEqual({ seat_number: 4 })
  })

  it('devuelve null cuando la respuesta es 204', async () => {
    mockFetch(204)
    expect(await api('/routes/1', { method: 'DELETE' })).toBeNull()
  })

  it('traduce el 409 de asiento ocupado en un ApiError con el mensaje del servidor', async () => {
    mockFetch(409, { detail: 'El asiento 7 ya fue vendido' })
    const error = await api('/tickets', { method: 'POST', body: {} }).catch((e) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(409)
    expect(error.message).toBe('El asiento 7 ya fue vendido')
  })

  it('muestra los errores de validación (422) con nombres de campo en español', async () => {
    mockFetch(422, { detail: [
      { loc: ['body', 'passenger_name'], msg: 'Value error, El nombre solo puede contener letras' },
      { loc: ['body', 'passenger_doc'], msg: 'Field required' },
    ] })
    const error = await api('/tickets', { method: 'POST', body: {} }).catch((e) => e)
    expect(error.message).toBe('Nombre del pasajero: El nombre solo puede contener letras · Documento: Field required')
  })

  it('cierra la sesión si el token expiró (401)', async () => {
    setToken('vencido')
    const listener = vi.fn()
    window.addEventListener('auth:logout', listener)
    mockFetch(401, { detail: 'Sesión inválida o expirada' })
    await expect(api('/auth/me')).rejects.toThrow('Sesión inválida o expirada')
    expect(getToken()).toBeNull()
    expect(listener).toHaveBeenCalledOnce()
    window.removeEventListener('auth:logout', listener)
  })

  it('da un mensaje claro cuando no hay conexión con el servidor', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    const error = await api('/trips/search').catch((e) => e)
    expect(error.status).toBe(0)
    expect(error.message).toMatch(/No se pudo conectar con el servidor/)
  })
})
