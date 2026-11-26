/**
 * Construye el contenido CSV compatible con Excel en español:
 * separador ";", fin de línea CRLF y BOM UTF-8 para que las tildes se vean bien.
 */
export function buildCsv(headers, rows) {
  const escape = (value) => {
    const s = String(value ?? '')
    return /[;"\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }
  return '﻿' + [headers, ...rows].map((r) => r.map(escape).join(';')).join('\r\n')
}

/** Descarga una tabla como archivo CSV. */
export function downloadCsv(filename, headers, rows) {
  const url = URL.createObjectURL(new Blob([buildCsv(headers, rows)], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}
