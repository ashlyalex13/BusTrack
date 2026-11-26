import { describe, expect, it } from 'vitest'
import { buildCsv } from './csv.js'

describe('buildCsv (exportación de reportes)', () => {
  it('usa BOM UTF-8, separador ";" y fin de línea CRLF para Excel', () => {
    const csv = buildCsv(['Hora', 'Ruta'], [['05:00', 'Cali → Buga']])
    expect(csv.startsWith('﻿')).toBe(true)
    expect(csv.slice(1)).toBe('Hora;Ruta\r\n05:00;Cali → Buga')
  })

  it('escapa valores con separadores, comillas o saltos de línea', () => {
    const csv = buildCsv(['Empresa'], [['Rápido; Pacífico'], ['Dice "hola"'], ['Línea 1\nLínea 2']])
    const lines = csv.slice(1).split('\r\n')
    expect(lines[1]).toBe('"Rápido; Pacífico"')
    expect(lines[2]).toBe('"Dice ""hola"""')
    expect(lines[3]).toBe('"Línea 1\nLínea 2"')
  })

  it('convierte vacíos y números en texto', () => {
    expect(buildCsv(['A', 'B', 'C'], [[null, undefined, 0]]).slice(1)).toBe('A;B;C\r\n;;0')
  })
})
