import { describe, expect, it } from 'vitest'
import { duration, errMsg, hour, money, todayISO } from './format.js'

const normalize = (s) => s.replace(/\s/g, ' ') // Intl usa espacios no separables

describe('format', () => {
  it('formatea pesos colombianos sin decimales', () => {
    expect(normalize(money(85000))).toBe('$ 85.000')
    expect(normalize(money('15000.00'))).toBe('$ 15.000')
    expect(normalize(money(null))).toBe('$ 0')
  })

  it('muestra la duración en horas y minutos', () => {
    expect(duration(600)).toBe('10h')
    expect(duration(75)).toBe('1h 15m')
    expect(duration(45)).toBe('0h 45m')
  })

  it('muestra la hora en formato de 12 horas', () => {
    expect(normalize(hour('2030-05-10T21:05:00'))).toBe('09:05 p. m.')
    expect(normalize(hour('2030-05-10T08:30:00'))).toBe('08:30 a. m.')
  })

  it('todayISO devuelve la fecha local en formato AAAA-MM-DD', () => {
    expect(todayISO()).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    const now = new Date()
    expect(Number(todayISO().slice(8, 10))).toBe(now.getDate())
  })

  it('errMsg limpia el prefijo técnico de los errores de validación', () => {
    expect(errMsg(new Error('Value error, El origen debe ser distinto'))).toBe('El origen debe ser distinto')
    expect(errMsg(null)).toBe('Error inesperado')
  })
})
