import { Component } from 'react'
import { Link } from 'react-router-dom'
import { RefreshCw, TriangleAlert } from 'lucide-react'

/**
 * Captura errores de renderizado de una pantalla y muestra un aviso en lugar
 * de dejar la página en blanco. El menú sigue funcionando para navegar a otra vista.
 */
export default class ErrorBoundary extends Component {
  state = { error: null }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error('Error en la interfaz:', error, info.componentStack)
  }

  render() {
    if (!this.state.error) return this.props.children
    return (
      <div className="card mx-auto max-w-lg p-8 text-center">
        <div className="mx-auto mb-3 grid h-14 w-14 place-items-center rounded-full bg-amber-100 text-amber-600"><TriangleAlert size={28} /></div>
        <h2 className="text-lg font-bold text-slate-900">Algo salió mal en esta pantalla</h2>
        <p className="mt-1 text-sm text-slate-500">Puedes reintentar o ir a otra sección. Si el problema continúa, avisa al administrador.</p>
        <div className="mt-5 flex justify-center gap-2">
          <button className="btn btn-primary" onClick={() => this.setState({ error: null })}><RefreshCw size={16} /> Reintentar</button>
          <Link to="/" className="btn btn-ghost" onClick={() => this.setState({ error: null })}>Ir al inicio</Link>
        </div>
      </div>
    )
  }
}
