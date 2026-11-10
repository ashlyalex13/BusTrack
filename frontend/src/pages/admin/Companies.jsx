import CrudPage from '../../components/CrudPage.jsx'

const Active = ({ on }) => <span className={`badge ${on ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>{on ? 'Activa' : 'Inactiva'}</span>

export default function Companies() {
  return (
    <CrudPage
      title="Empresas transportadoras" subtitle="Empresas que operan viajes en la terminal."
      baseUrl="/companies" entity="empresa"
      emptyForm={{ name: '', nit: '', phone: '', is_active: true }}
      toForm={(r) => ({ ...r, nit: r.nit ?? '', phone: r.phone ?? '' })}
      toPayload={(f) => ({ name: f.name, nit: f.nit || null, phone: f.phone || null, is_active: f.is_active })}
      columns={[
        { label: 'Nombre', render: (r) => <span className="font-semibold">{r.name}</span> },
        { label: 'NIT', key: 'nit' },
        { label: 'Teléfono', key: 'phone' },
        { label: 'Estado', render: (r) => <Active on={r.is_active} /> },
      ]}
      fields={[
        { name: 'name', label: 'Nombre', required: true },
        { name: 'nit', label: 'NIT' },
        { name: 'phone', label: 'Teléfono' },
        { name: 'is_active', label: 'Empresa activa', type: 'checkbox' },
      ]}
    />
  )
}
