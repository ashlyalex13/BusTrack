const TOKEN_KEY = 'bustrack_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => (t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY))

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

/** Cliente único para el backend: agrega el JWT y traduce errores. */
export async function api(path, { method = 'GET', body } = {}) {
  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  let res
  try {
    res = await fetch(`/api${path}`, { method, headers, body: body !== undefined ? JSON.stringify(body) : undefined })
  } catch {
    throw new ApiError(0, 'No se pudo conectar con el servidor. Revisa tu conexión a internet e intenta de nuevo.')
  }
  if (res.status === 204) return null
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    let msg = data?.detail
    if (Array.isArray(msg)) msg = msg.map((e) => `${e.loc?.at(-1) ?? ''}: ${e.msg}`).join(' · ')
    if (res.status === 401 && token) {
      setToken(null)
      window.dispatchEvent(new Event('auth:logout'))
    }
    throw new ApiError(res.status, msg || `Error ${res.status}`)
  }
  return data
}
