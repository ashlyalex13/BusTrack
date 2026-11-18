/**
 * Descarga una tabla como CSV compatible con Excel en español:
 * separador ";" y BOM UTF-8 para que las tildes se vean bien.
 */
export function downloadCsv(filename, headers, rows) {
  const escape = (value) => {
    const s = String(value ?? '')
    return /[;"\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }
  const content = '﻿' + [headers, ...rows].map((r) => r.map(escape).join(';')).join('\r\n')
  const url = URL.createObjectURL(new Blob([content], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}
