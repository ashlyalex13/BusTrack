// Configuración común de las pruebas del frontend.
import '@testing-library/jest-dom/vitest' // aserciones como toBeInTheDocument(), toBeDisabled()
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

afterEach(() => {
  cleanup()
  localStorage.clear()
  vi.restoreAllMocks()
})
