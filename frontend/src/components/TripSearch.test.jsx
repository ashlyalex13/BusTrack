import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { AvailabilityBadge, searchQuery, TripSummary } from './TripSearch.jsx'

const trip = {
  departure_at: '2030-05-10T21:00:00', duration_minutes: 75, origin: 'Cali', destination: 'Buga',
  company_name: 'Expreso Andino', fare: 15000, available: 18,
}

describe('TripSearch', () => {
  it('searchQuery solo incluye los filtros con valor', () => {
    expect(searchQuery({ origin: 'Cali', destination: '', date: '2030-05-10' })).toBe('/trips/search?origin=Cali&date=2030-05-10')
    expect(searchQuery({ origin: '', destination: '', date: '' })).toBe('/trips/search?')
  })

  it('TripSummary muestra hora, ruta, empresa y duración', () => {
    render(<TripSummary trip={trip} />)
    expect(screen.getByText('09:00')).toBeInTheDocument()
    expect(screen.getByText(/p\.\s?m\./)).toBeInTheDocument()
    expect(screen.getByText('Cali')).toBeInTheDocument()
    expect(screen.getByText('Buga')).toBeInTheDocument()
    expect(screen.getByText(/Expreso Andino/)).toBeInTheDocument()
    expect(screen.getByText(/1h 15m/)).toBeInTheDocument()
  })

  it.each([
    [0, 'Agotado', 'bg-rose-100'],
    [3, '3', 'bg-amber-100'],     // pocos asientos: alerta
    [18, '18', 'bg-emerald-100'],
  ])('AvailabilityBadge con %i asientos', (available, text, color) => {
    const { container } = render(<AvailabilityBadge trip={{ ...trip, available }} />)
    const badge = container.firstChild
    expect(badge).toHaveTextContent(text)
    expect(badge).toHaveClass(color)
  })
})
