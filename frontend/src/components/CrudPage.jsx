import { useCallback, useEffect, useState } from 'react'
import { Inbox, Pencil, Plus, Trash2 } from 'lucide-react'
import { api } from '../lib/api.js'
import { errMsg } from '../lib/format.js'
import { Alert, Empty, Modal, PageHeader, Spinner } from './ui.jsx'

/**
 * Página CRUD genérica para el panel admin.
 * fields: [{ name, label, type: text|number|select|checkbox|password|datetime-local, options, required: true|'create' }]
 */
export default function CrudPage({
  title, subtitle, baseUrl, listUrl = baseUrl, columns, fields, emptyForm,
  toForm = (r) => r, toPayload = (f) => f, toolbar, entity = 'registro', canDelete = true,
}) {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [formError, setFormError] = useState('')
  const [saving, setSaving] = useState(false)

  const load = useCallback(() => {
    setLoading(true)
    api(listUrl).then(setRows).catch((e) => setError(errMsg(e))).finally(() => setLoading(false))
  }, [listUrl])
  useEffect(() => { load() }, [load])

  const open = (row) => {
    setEditing(row || {})
    setForm(row ? toForm(row) : emptyForm)
    setFormError('')
  }

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    setFormError('')
    try {
      const body = toPayload(form, !!editing.id)
      if (editing.id) await api(`${baseUrl}/${editing.id}`, { method: 'PUT', body })
      else await api(baseUrl, { method: 'POST', body })
      setEditing(null)
      load()
    } catch (err) {
      setFormError(errMsg(err))
    } finally {
      setSaving(false)
    }
  }

  const remove = async (row) => {
    if (!window.confirm(`¿Eliminar este ${entity}?`)) return
    try {
      await api(`${baseUrl}/${row.id}`, { method: 'DELETE' })
      load()
    } catch (err) {
      setError(errMsg(err))
    }
  }

  const isEdit = !!editing?.id
  const set = (name, value) => setForm((f) => ({ ...f, [name]: value }))

  return (
    <div>
      <PageHeader title={title} subtitle={subtitle}>
        {toolbar}
        <button className="btn btn-primary" onClick={() => open(null)}><Plus size={16} /> Nuevo {entity}</button>
      </PageHeader>
      <div className="mb-4"><Alert type="error" onClose={() => setError('')}>{error}</Alert></div>

      <div className="card overflow-hidden">
        {loading ? <Spinner /> : rows.length === 0 ? (
          <Empty icon={Inbox} title="Sin registros">Crea el primero con el botón “Nuevo {entity}”.</Empty>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-slate-200 bg-slate-50">
                <tr>{columns.map((c) => <th key={c.label} className="th">{c.label}</th>)}<th className="th text-right">Acciones</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rows.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50">
                    {columns.map((c) => <td key={c.label} className="td">{c.render ? c.render(r) : r[c.key]}</td>)}
                    <td className="td whitespace-nowrap text-right">
                      <button className="btn btn-ghost btn-sm" onClick={() => open(r)}><Pencil size={14} /> Editar</button>
                      {canDelete && <button className="btn btn-sm ml-1 text-rose-600 hover:bg-rose-50" onClick={() => remove(r)}><Trash2 size={14} /></button>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {editing && (
        <Modal title={`${isEdit ? 'Editar' : 'Nuevo'} ${entity}`} onClose={() => setEditing(null)}>
          <form onSubmit={save} className="space-y-4">
            {fields.map((f) => {
              const required = f.required === true || (f.required === 'create' && !isEdit)
              if (f.type === 'checkbox') {
                return (
                  <label key={f.name} className="flex items-center gap-2 text-sm font-medium">
                    <input type="checkbox" className="h-4 w-4 accent-indigo-600" checked={!!form[f.name]}
                      onChange={(e) => set(f.name, e.target.checked)} />
                    {f.label}
                  </label>
                )
              }
              return (
                <div key={f.name}>
                  <label className="label">{f.label}{required && ' *'}</label>
                  {f.type === 'select' ? (
                    <select className="input" required={required} value={form[f.name] ?? ''} onChange={(e) => set(f.name, e.target.value)}>
                      <option value="">Seleccione...</option>
                      {f.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  ) : (
                    <input className="input" type={f.type || 'text'} required={required} min={f.min} step={f.step}
                      placeholder={f.placeholder} value={form[f.name] ?? ''} onChange={(e) => set(f.name, e.target.value)} />
                  )}
                  {f.help && <p className="mt-1 text-xs text-slate-400">{f.help}</p>}
                </div>
              )
            })}
            <Alert type="error">{formError}</Alert>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" className="btn btn-ghost" onClick={() => setEditing(null)}>Cancelar</button>
              <button className="btn btn-primary" disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
