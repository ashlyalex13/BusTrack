import CrudPage from '../../components/CrudPage.jsx'

export default function Users() {
  return (
    <CrudPage
      title="Usuarios" subtitle="Administradores y taquilleros con acceso al sistema."
      baseUrl="/users" entity="usuario" canDelete={false}
      emptyForm={{ name: '', email: '', password: '', role: 'taquillero', is_active: true }}
      toForm={(r) => ({ ...r, password: '' })}
      toPayload={(f) => ({ name: f.name, email: f.email, role: f.role, is_active: f.is_active, password: f.password || null })}
      columns={[
        { label: 'Nombre', render: (r) => <span className="font-semibold">{r.name}</span> },
        { label: 'Correo', key: 'email' },
        { label: 'Rol', render: (r) => <span className={`badge ${r.role === 'admin' ? 'bg-amber-100 text-amber-700' : 'bg-sky-100 text-sky-700'}`}>{r.role}</span> },
        { label: 'Estado', render: (r) => (r.is_active ? 'Activo' : 'Inactivo') },
      ]}
      fields={[
        { name: 'name', label: 'Nombre completo', required: true },
        { name: 'email', label: 'Correo', type: 'email', required: true },
        { name: 'password', label: 'Contraseña', type: 'password', required: 'create', help: 'Mínimo 6 caracteres. Al editar, déjala vacía para no cambiarla.' },
        { name: 'role', label: 'Rol', type: 'select', required: true, options: [{ value: 'taquillero', label: 'Taquillero' }, { value: 'admin', label: 'Administrador' }] },
        { name: 'is_active', label: 'Usuario activo', type: 'checkbox' },
      ]}
    />
  )
}
