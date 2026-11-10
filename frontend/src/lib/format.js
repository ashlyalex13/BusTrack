export const money = (v) =>
  new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(Number(v || 0))

export const hour = (d) => new Date(d).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', hour12: true })

export const dayLabel = (d) =>
  new Date(d).toLocaleDateString('es-CO', { weekday: 'short', day: 'numeric', month: 'short' })

export const duration = (min) => `${Math.floor(min / 60)}h${min % 60 ? ` ${min % 60}m` : ''}`

export const todayISO = () => {
  const d = new Date()
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 10)
}

export const errMsg = (e) => (e?.message || 'Error inesperado').replace(/Value error, /g, '')
