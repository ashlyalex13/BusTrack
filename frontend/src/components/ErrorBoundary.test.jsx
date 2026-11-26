import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import ErrorBoundary from './ErrorBoundary.jsx'

let shouldFail = true
function Fragile() {
  if (shouldFail) throw new Error('fallo de prueba')
  return <p>Pantalla funcionando</p>
}

describe('ErrorBoundary', () => {
  it('muestra un aviso en lugar de dejar la página en blanco y permite reintentar', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {}) // React registra el error esperado
    shouldFail = true
    render(<MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><ErrorBoundary><Fragile /></ErrorBoundary></MemoryRouter>)
    expect(screen.getByText('Algo salió mal en esta pantalla')).toBeInTheDocument()

    shouldFail = false
    await userEvent.click(screen.getByRole('button', { name: /Reintentar/ }))
    expect(screen.getByText('Pantalla funcionando')).toBeInTheDocument()
  })
})
