import { useEffect, useId, useState } from 'react'
import { Html5Qrcode } from 'html5-qrcode'
import { Alert } from './ui.jsx'

/**
 * Lector de QR con la cámara del dispositivo (trasera en celulares).
 * Requiere contexto seguro: funciona en localhost y en HTTPS.
 */
export default function QrScanner({ onScan }) {
  const id = `qr-${useId().replace(/:/g, '')}`
  const [error, setError] = useState('')

  useEffect(() => {
    const scanner = new Html5Qrcode(id, { verbose: false })
    let cancelled = false
    let running = false

    const stop = () => (running ? scanner.stop().catch(() => {}) : Promise.resolve())

    scanner
      .start(
        { facingMode: 'environment' },
        { fps: 10, qrbox: { width: 230, height: 230 } },
        (text) => {
          if (cancelled) return
          cancelled = true
          stop().finally(() => onScan(text))
        },
        () => {}, // fotogramas sin QR: se ignoran
      )
      .then(() => {
        running = true
        if (cancelled) stop()
      })
      .catch(() => setError('No se pudo acceder a la cámara. Revisa los permisos del navegador, o pega el código / usa un lector USB.'))

    return () => {
      cancelled = true
      stop()
    }
  }, [id, onScan])

  return (
    <div className="space-y-2">
      <div id={id} className="mx-auto max-w-sm overflow-hidden rounded-xl bg-slate-900" />
      {error ? <Alert type="warn">{error}</Alert> : <p className="text-center text-xs text-slate-500">Apunta la cámara al código QR del tiquete.</p>}
    </div>
  )
}
