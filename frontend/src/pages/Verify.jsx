import { lazy, Suspense, useCallback, useState } from 'react'
import { Camera, CameraOff, CircleCheck, CircleX, ScanLine, Search } from 'lucide-react'
import { api } from '../lib/api.js'
import { dayLabel, errMsg, hour, money } from '../lib/format.js'
import { Alert, PageHeader, Spinner, StatusBadge } from '../components/ui.jsx'

// La librería de la cámara pesa ~340 kB: se descarga solo cuando se abre el escáner.
const QrScanner = lazy(() => import('../components/QrScanner.jsx'))

/** HU04: verificación de tiquete por código QR (cámara, lector USB o código pegado). */
export default function Verify() {
  const [code, setCode] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [scanning, setScanning] = useState(false)

  const check = useCallback(async (value, board) => {
    const clean = value.trim()
    if (!clean) return
    setLoading(true)
    setError('')
    try {
      setResult(board
        ? await api('/tickets/verify', { method: 'POST', body: { code: clean } })
        : await api(`/tickets/verify?code=${encodeURIComponent(clean)}`))
    } catch (e) {
      setError(errMsg(e))
    } finally {
      setLoading(false)
    }
  }, [])

  const run = (board) => check(code, board)

  // Al leer un QR con la cámara se consulta de inmediato; el abordaje se confirma con el botón.
  const onScan = useCallback((text) => {
    setScanning(false)
    setCode(text)
    check(text, false)
  }, [check])

  const t = result?.ticket
  return (
    <div className="mx-auto max-w-2xl">
      <PageHeader title="Verificar tiquete" subtitle="Escanea el QR con la cámara o con un lector, o pega el código del tiquete." />
      <div className="card space-y-4 p-5">
        <button type="button" className={`btn w-full ${scanning ? 'btn-ghost' : 'btn-accent'}`} onClick={() => setScanning((s) => !s)}>
          {scanning ? <><CameraOff size={16} /> Cerrar cámara</> : <><Camera size={16} /> Escanear con la cámara</>}
        </button>
        {scanning && <Suspense fallback={<Spinner label="Abriendo cámara..." />}><QrScanner onScan={onScan} /></Suspense>}
        <div>
          <label className="label" htmlFor="ticket-code">Código del tiquete</label>
          <input id="ticket-code" className="input font-mono" autoFocus placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.firma" value={code}
            onChange={(e) => { setCode(e.target.value); setResult(null) }}
            onKeyDown={(e) => e.key === 'Enter' && run(false)} />
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="btn btn-ghost" disabled={loading} onClick={() => run(false)}><Search size={16} /> Consultar</button>
          <button className="btn btn-primary" disabled={loading} onClick={() => run(true)}><ScanLine size={16} /> Validar y registrar abordaje</button>
        </div>
        <Alert type="error">{error}</Alert>
      </div>

      {result && (
        <div className={`card mt-4 overflow-hidden border-2 ${result.valid ? 'border-emerald-400' : 'border-rose-400'}`}>
          <div className={`flex items-center gap-3 p-4 ${result.valid ? 'bg-emerald-50 text-emerald-800' : 'bg-rose-50 text-rose-800'}`}>
            {result.valid ? <CircleCheck size={32} /> : <CircleX size={32} />}
            <div>
              <p className="text-lg font-extrabold">{result.valid ? 'TIQUETE VÁLIDO' : 'TIQUETE RECHAZADO'}</p>
              <p className="text-sm">{result.message}</p>
            </div>
          </div>
          {t && (
            <div className="grid grid-cols-2 gap-4 p-4 text-sm sm:grid-cols-3">
              <Info label="Pasajero" value={t.passenger_name} />
              <Info label="Documento" value={t.passenger_doc} />
              <Info label="Asiento" value={`#${t.seat_number}`} />
              <Info label="Ruta" value={`${t.trip.origin} → ${t.trip.destination}`} />
              <Info label="Salida" value={`${dayLabel(t.trip.departure_at)} ${hour(t.trip.departure_at)}`} />
              <Info label="Empresa" value={t.trip.company_name} />
              <Info label="Valor" value={money(t.price)} />
              <div><p className="label">Estado</p><StatusBadge status={t.status} /></div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

const Info = ({ label, value }) => <div><p className="label">{label}</p><p className="font-semibold text-slate-800">{value}</p></div>
