import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import SeatGrid from './SeatGrid.jsx'

const seats = [
  { number: 1, status: 'free' },
  { number: 2, status: 'sold' },
  { number: 3, status: 'reserved' },
  { number: 4, status: 'boarded' },
  { number: 5, status: 'free' },
]
const seat = (n) => screen.getByRole('button', { name: String(n) })

describe('SeatGrid (grilla de asientos, RF08)', () => {
  it('dibuja un botón por asiento', () => {
    render(<SeatGrid seats={seats} onSelect={() => {}} />)
    expect(screen.getAllByRole('button')).toHaveLength(5)
  })

  it('solo permite elegir asientos libres', () => {
    render(<SeatGrid seats={seats} onSelect={() => {}} />)
    expect(seat(1)).toBeEnabled()
    expect(seat(2)).toBeDisabled() // vendido
    expect(seat(3)).toBeDisabled() // reservado por otra taquilla
    expect(seat(4)).toBeDisabled() // abordado
    expect(seat(3)).toHaveAttribute('title', 'Asiento 3: reservado por otra taquilla')
  })

  it('al hacer clic en un asiento libre lo selecciona', async () => {
    const onSelect = vi.fn()
    render(<SeatGrid seats={seats} onSelect={onSelect} />)
    await userEvent.click(seat(5))
    expect(onSelect).toHaveBeenCalledWith(5)
  })

  it('el asiento propio sigue disponible aunque el servidor lo marque reservado, y un segundo clic lo libera', async () => {
    const onSelect = vi.fn()
    render(<SeatGrid seats={seats} selected={3} onSelect={onSelect} />)
    expect(seat(3)).toBeEnabled()
    expect(seat(3)).toHaveAttribute('title', 'Asiento 3 reservado para ti')
    await userEvent.click(seat(3))
    expect(onSelect).toHaveBeenCalledWith(null)
  })

  it('sin onSelect (solo lectura) no se puede elegir ningún asiento', () => {
    render(<SeatGrid seats={seats} />)
    expect(seat(1)).toBeDisabled()
  })
})
