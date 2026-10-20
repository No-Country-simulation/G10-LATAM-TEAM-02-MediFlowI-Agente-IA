import { useCallback, useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import {
  fetchUsers,
  createNewUser,
  updateUserDetails,
  type User,
} from '../api/auth.api'
import { useAuth } from '../hooks/useAuth'
import Loading from '../components/common/Loading'
import ErrorMessage from '../components/common/ErrorMessage'
import {
  FaUserPlus,
  FaSearch,
  FaFilter,
  FaCheck,
} from 'react-icons/fa'

const SPECIALTIES = [
  'Sin especialidad',
  'Ginecología y Obstetricia',
  'Cirugía General',
  'Medicina Interna',
  'Pediatría',
  'Cardiología',
  'Traumatología',
  'Medicina General',
  'Neurología',
]

const ROLES: Array<{ value: User['rol']; label: string }> = [
  { value: 'ADMINISTRADOR', label: 'Administrador' },
  { value: 'OPERADOR', label: 'Operador' },
  { value: 'COORDINADOR', label: 'Coordinador' },
  { value: 'AUDITOR', label: 'Auditor' },
  { value: 'SUPERVISOR', label: 'Supervisor' },
  { value: 'PENDIENTE', label: 'Pendiente' },
]

export default function UsersManagementView() {
  const { user: currentUser, token: authToken } = useAuth()
  const location = useLocation()
  const isSolicitudesRoute = location.pathname.includes('solicitudes')

  const [usersList, setUsersList] = useState<User[]>([])
  const [loadingUsers, setLoadingUsers] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [toastMessage, setToastMessage] = useState<string | null>(null)
  const [updatingId, setUpdatingId] = useState<string | null>(null)

  // Filtros y Búsqueda
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState('TODOS')
  const [statusFilter, setStatusFilter] = useState(isSolicitudesRoute ? 'PENDIENTE' : 'TODOS')

  useEffect(() => {
    if (isSolicitudesRoute) {
      setStatusFilter('PENDIENTE')
    }
  }, [isSolicitudesRoute])

  // Paginación
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 8

  // Modal para Crear Usuario
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [newDni, setNewDni] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [newNombres, setNewNombres] = useState('')
  const [newApellidos, setNewApellidos] = useState('')
  const [newCorreo, setNewCorreo] = useState('')
  const [newTelefono, setNewTelefono] = useState('')
  const [newEspecialidad, setNewEspecialidad] = useState('')
  const [newRol, setNewRol] = useState<User['rol']>('OPERADOR')
  const [createModalError, setCreateModalError] = useState<string | null>(null)
  const [savingUser, setSavingUser] = useState(false)

  // Cargar usuarios
  const loadUsers = useCallback(async () => {
    setLoadingUsers(true)
    setErrorMessage(null)
    try {
      if (!authToken) throw new Error('La sesión administrativa no está disponible.')
      const data = await fetchUsers(authToken)
      setUsersList(data)
    } catch (error) {
      setUsersList([])
      setErrorMessage(error instanceof Error ? error.message : 'No se pudieron cargar las solicitudes de acceso.')
    } finally {
      setLoadingUsers(false)
    }
  }, [authToken])

  useEffect(() => {
    queueMicrotask(() => void loadUsers())
  }, [loadUsers])

  const showToast = (msg: string) => {
    setToastMessage(msg)
    setTimeout(() => {
      setToastMessage(null)
    }, 3500)
  }

  // Actualización inmediata de Rol (Autosave)
  const handleRoleChange = async (userId: string, newRole: User['rol']) => {
    if (!authToken) return
    setUpdatingId(userId)
    try {
      const updated = await updateUserDetails(authToken, userId, { rol: newRole })
      setUsersList((prev) => prev.map((u) => (u.id === userId ? { ...u, rol: updated.rol } : u)))
      showToast(`Rol actualizado a ${newRole} con éxito.`)
    } catch (err: any) {
      showToast(`Error al actualizar rol: ${err.message || 'Error del servidor'}`)
    } finally {
      setUpdatingId(null)
    }
  }

  // Actualización inmediata de Especialidad (Autosave)
  const handleSpecialtyChange = async (userId: string, newSpecialty: string) => {
    if (!authToken) return
    setUpdatingId(userId)
    const val = newSpecialty === 'Sin especialidad' ? '' : newSpecialty
    try {
      const updated = await updateUserDetails(authToken, userId, { especialidad_medica: val })
      setUsersList((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, especialidad_medica: updated.especialidad_medica } : u)),
      )
      showToast('Especialidad actualizada con éxito.')
    } catch (err: any) {
      showToast(`Error al actualizar especialidad: ${err.message || 'Error del servidor'}`)
    } finally {
      setUpdatingId(null)
    }
  }

  // Toggle inmediato de Permiso / Estado (Autosave)
  const handleToggleStatus = async (userItem: User) => {
    if (!authToken) return
    setUpdatingId(userItem.id)
    const newStatus: 'ACTIVO' | 'INACTIVO' = userItem.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO'
    try {
      const updated = await updateUserDetails(authToken, userItem.id, { estado: newStatus })
      setUsersList((prev) => prev.map((u) => (u.id === userItem.id ? { ...u, estado: updated.estado } : u)))
      showToast(`Permiso ${newStatus === 'ACTIVO' ? 'habilitado' : 'deshabilitado'} para ${userItem.nombres}.`)
    } catch (err: any) {
      showToast(`Error al modificar permiso: ${err.message || 'Error del servidor'}`)
    } finally {
      setUpdatingId(null)
    }
  }

  // Manejo de Creación Manual
  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreateModalError(null)

    if (!newDni.trim() || !newNombres.trim() || !newApellidos.trim() || !newPassword) {
      setCreateModalError('Por favor complete todos los campos obligatorios.')
      return
    }

    if (newPassword !== confirmPassword) {
      setCreateModalError('Las contraseñas no coinciden.')
      return
    }

    setSavingUser(true)
    try {
      if (!authToken) throw new Error('Sesión inválida.')
      await createNewUser(authToken, {
        documento_identidad: newDni.trim(),
        password: newPassword,
        nombres: newNombres.trim(),
        apellidos: newApellidos.trim(),
        correo: newCorreo.trim() || undefined,
        telefono: newTelefono.trim() || undefined,
        rol: newRol,
        especialidad_medica: newEspecialidad === 'Sin especialidad' ? undefined : newEspecialidad || undefined,
        estado: 'ACTIVO',
      })
      setIsCreateModalOpen(false)
      showToast('Usuario creado exitosamente.')
      await loadUsers()
    } catch (err: any) {
      setCreateModalError(err.message || 'Error al crear usuario.')
    } finally {
      setSavingUser(false)
    }
  }

  // Formato de fecha
  const formatDate = (isoString?: string) => {
    if (!isoString) return '-'
    try {
      const d = new Date(isoString)
      return `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear().toString().slice(-2)}`
    } catch {
      return isoString
    }
  }

  // Filtrado de usuarios
  const filteredUsers = usersList.filter((u) => {
    const fullText = `${u.nombres} ${u.apellidos} ${u.correo || ''} ${u.documento_identidad}`.toLowerCase()
    const matchesSearch = fullText.includes(searchTerm.toLowerCase())
    const matchesRole = roleFilter === 'TODOS' || u.rol === roleFilter
    const matchesStatus =
      statusFilter === 'TODOS' ||
      (statusFilter === 'PENDIENTE' ? (u.rol === 'PENDIENTE' || (u.estado as string) === 'PENDIENTE') : u.estado === statusFilter)
    return matchesSearch && matchesRole && matchesStatus
  })

  // Paginación
  const totalPages = Math.max(1, Math.ceil(filteredUsers.length / pageSize))
  const paginatedUsers = filteredUsers.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  const getInitials = (nombres: string, apellidos: string) => {
    const n = nombres?.trim()?.[0] || ''
    const a = apellidos?.trim()?.[0] || ''
    return `${n}${a}`.toUpperCase() || 'U'
  }

  if (loadingUsers) return <Loading message="Cargando solicitudes de acceso y usuarios..." />
  if (errorMessage) return <ErrorMessage title="Error al cargar usuarios" message={errorMessage} onRetry={loadUsers} />

  return (
    <div className="clinical-page w-full">
      {/* Toast de notificación */}
      {toastMessage && (
        <div
          role="status"
          className="position-fixed bottom-4 end-4 z-50 bg-[#1e3a5f] text-white px-4 py-3 rounded-xl shadow-lg d-flex align-items-center gap-2"
          style={{ zIndex: 1060 }}
        >
          <FaCheck className="text-emerald-400" />
          <span className="small font-medium">{toastMessage}</span>
        </div>
      )}

      {/* Tabs superiores tipo Píldora (Enrutamiento, Historial, Solicitudes) */}
      {/* <div className="d-flex justify-content-center align-items-center gap-4 mb-4">
        <Link
          to="/triaje"
          className="text-decoration-none fw-semibold text-secondary small hover:text-dark transition-colors"
        >
          Enrutamiento
        </Link>
        <Link
          to="/documentos"
          className="text-decoration-none fw-semibold text-secondary small hover:text-dark transition-colors"
        >
          Historial
        </Link>
        <span
          className="px-4 py-1.5 rounded-pill bg-white shadow-sm fw-bold small text-dark border border-slate-200"
          style={{ color: '#1e3a5f' }}
        >
          Solicitudes
        </span>
      </div> */}

      {/* Encabezado principal */}
      <div className="flex items-center flex-col text-center mt-2 mb-5 gap-2 sm:gap-4">
        <h1
          className="display-6 fw-bold tracking-tight mb-2"
          style={{ fontFamily: "'Montserrat', sans-serif", color: '#1e3a5f' }}
        >
          Solicitudes de acceso
        </h1>
        <p
          className="text-secondary fw-normal fs-6 mx-auto"
          style={{ maxWidth: '620px', color: '#556987' }}
        >
          A continuación se listan todas las solicitudes de acceso que han sido recibidas para utilizar MediFlow
        </p>
      </div>

      {/* Barra de herramientas (Búsqueda, Filtro y Botón Nuevo) */}
      <div className="bg-white rounded-3 shadow-sm border border-slate-100 p-3 mb-4 d-flex flex-wrap align-items-center justify-content-between gap-3">
        <div className="d-flex flex-wrap align-items-center gap-2 flex-grow-1" style={{ maxWidth: '650px' }}>
          <div className="position-relative flex-grow-1" style={{ minWidth: '220px' }}>
            <FaSearch className="position-absolute start-0 top-50 translate-middle-y ms-3 text-muted" />
            <input
              type="text"
              placeholder="Buscar por nombre, correo o DNI..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-control form-control-sm ps-5 rounded-pill border-slate-200"
              style={{ fontSize: '0.875rem' }}
            />
          </div>

          <div className="d-flex align-items-center gap-1.5 min-w-[200px]">
            <FaFilter className="text-muted small" />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="form-select form-select-sm rounded-pill border-slate-200 text-secondary"
              style={{ fontSize: '0.85rem' }}
            >
              <option value="TODOS">Todos los roles</option>
              {ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="form-select form-select-sm rounded-pill border-slate-200 text-secondary"
            style={{ fontSize: '0.85rem' }}
          >
            <option value="TODOS">Todos los estados</option>
            <option value="PENDIENTE">Pendientes de Aprobación</option>
            <option value="ACTIVO">Habilitados (Activos)</option>
            <option value="INACTIVO">Deshabilitados (Inactivos)</option>
          </select>
        </div>

        <button
          type="button"
          onClick={() => setIsCreateModalOpen(true)}
          className="btn btn-sm btn-primary rounded-pill px-3 py-1.5 d-flex align-items-center gap-1.5 shadow-sm"
          style={{ backgroundColor: '#1e3a5f', borderColor: '#1e3a5f' }}
        >
          <FaUserPlus size={13} />
          <span>Nuevo usuario</span>
        </button>
      </div>

      {/* Tarjeta Contenedora Principal con Tabla de Solicitudes */}
      <div className="bg-white rounded-4 shadow-sm border border-slate-100 p-3 sm:p-4 mb-4 overflow-hidden">
        <div className="table-responsive rounded-4">
          <table className="table table-hover align-middle mb-0" style={{ minWidth: '920px' }}>
            <thead>
              <tr className="border-bottom text-secondary" style={{ fontSize: '0.85rem' }}>
                <th scope="col" className="pb-3 fw-bold ps-3" style={{ color: '#1e3a5f' }}>
                  Usuarios
                </th>
                <th scope="col" className="pb-3 fw-bold" style={{ color: '#1e3a5f' }}>
                  Correo electrónico
                </th>
                <th scope="col" className="pb-3 fw-bold text-center" style={{ color: '#1e3a5f', width: '170px' }}>
                  Rol
                </th>
                <th scope="col" className="pb-3 fw-bold text-center" style={{ color: '#1e3a5f', width: '220px' }}>
                  Especialidad
                </th>
                <th scope="col" className="pb-3 fw-bold text-center" style={{ color: '#1e3a5f', width: '140px' }}>
                  Fecha de registro
                </th>
                <th scope="col" className="pb-3 fw-bold text-center" style={{ color: '#1e3a5f', width: '160px' }}>
                  Permiso habilitado
                </th>
              </tr>
            </thead>
            <tbody>
              {paginatedUsers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-5 text-muted">
                    No se encontraron solicitudes ni usuarios coincidentes con el criterio de búsqueda.
                  </td>
                </tr>
              ) : (
                paginatedUsers.map((u) => {
                  const isCurrentAdmin = u.id === currentUser?.id
                  return (
                    <tr key={u.id} className="border-bottom border-light">
                      {/* Columna Usuarios */}
                      <td className="ps-3 py-3">
                        <div className="d-flex align-items-center gap-2.5">
                          <div
                            className="d-flex align-items-center justify-content-center rounded-circle fw-bold text-white shadow-sm flex-shrink-0"
                            style={{
                              width: '38px',
                              height: '38px',
                              backgroundColor: u.rol === 'PENDIENTE' ? '#f59e0b' : '#1e3a5f',
                              fontSize: '0.85rem',
                            }}
                          >
                            {getInitials(u.nombres, u.apellidos)}
                          </div>
                          <div>
                            <div className="fw-semibold text-dark" style={{ fontSize: '0.9rem' }}>
                              {u.nombres} {u.apellidos}
                            </div>
                            {isCurrentAdmin && (
                              <span className="badge bg-light text-primary border" style={{ fontSize: '0.7rem' }}>
                                En sesión
                              </span>
                            )}
                            {u.rol === 'PENDIENTE' && (
                              <span className="badge bg-warning text-dark border ms-1" style={{ fontSize: '0.7rem' }}>
                                Pendiente
                              </span>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Columna Correo electrónico */}
                      <td className="py-3 text-secondary" style={{ fontSize: '0.875rem' }}>
                        {u.correo || u.documento_identidad}
                      </td>

                      {/* Columna Rol (Selector directo) */}
                      <td className="py-3 text-center">
                        <select
                          value={u.rol}
                          onChange={(e) => handleRoleChange(u.id, e.target.value as User['rol'])}
                          disabled={updatingId === u.id}
                          className="form-select form-select-sm rounded-pill text-secondary fw-medium px-3 mx-auto"
                          style={{
                            maxWidth: '160px',
                            fontSize: '0.825rem',
                            borderColor: u.rol === 'PENDIENTE' ? '#f59e0b' : '#e2e8f0',
                            backgroundColor: u.rol === 'PENDIENTE' ? '#fffbeb' : '#ffffff',
                          }}
                        >
                          {ROLES.map((r) => (
                            <option key={r.value} value={r.value}>
                              {r.label}
                            </option>
                          ))}
                        </select>
                      </td>

                      {/* Columna Especialidad (Selector directo) */}
                      <td className="py-3 text-center">
                        <select
                          value={u.especialidad_medica || 'Sin especialidad'}
                          onChange={(e) => handleSpecialtyChange(u.id, e.target.value)}
                          disabled={updatingId === u.id}
                          className="form-select form-select-sm rounded-pill text-secondary fw-medium px-3 mx-auto"
                          style={{ maxWidth: '210px', fontSize: '0.825rem', borderColor: '#e2e8f0' }}
                        >
                          {SPECIALTIES.map((esp) => (
                            <option key={esp} value={esp}>
                              {esp}
                            </option>
                          ))}
                        </select>
                      </td>

                      {/* Columna Fecha de registro */}
                      <td className="py-3 text-center text-secondary small">
                        {formatDate(u.created_at)}
                      </td>

                      {/* Columna Permiso habilitado (Toggle Switch) */}
                      <td className="py-3 text-center">
                        <button
                          type="button"
                          role="switch"
                          aria-checked={u.estado === 'ACTIVO'}
                          onClick={() => handleToggleStatus(u)}
                          disabled={updatingId === u.id}
                          className="btn p-0 border-0 bg-transparent"
                          title={u.estado === 'ACTIVO' ? 'Deshabilitar ingreso' : 'Habilitar ingreso'}
                        >
                          <div
                            className="rounded-pill p-1 transition-all d-inline-flex align-items-center"
                            style={{
                              width: '46px',
                              height: '26px',
                              backgroundColor: u.estado === 'ACTIVO' ? '#22c55e' : '#cbd5e1',
                              cursor: 'pointer',
                              transition: 'background-color 0.2s',
                            }}
                          >
                            <div
                              className="rounded-circle bg-white shadow-sm"
                              style={{
                                width: '18px',
                                height: '18px',
                                transform: u.estado === 'ACTIVO' ? 'translateX(20px)' : 'translateX(0px)',
                                transition: 'transform 0.2s ease-in-out',
                              }}
                            />
                          </div>
                        </button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Paginación Inferior (01 02 03 ... 04 05) */}
        {totalPages > 1 && (
          <div className="d-flex flex-wrap justify-content-center align-items-center gap-2 mt-4 pt-3 border-top">
            {Array.from({ length: totalPages }, (_, idx) => idx + 1).map((pageNum) => (
              <button
                key={pageNum}
                type="button"
                onClick={() => setCurrentPage(pageNum)}
                className={`btn btn-sm rounded-circle fw-semibold d-flex align-items-center justify-content-center ${currentPage === pageNum ? 'btn-primary shadow-sm' : 'btn-light text-secondary'
                  }`}
                style={{
                  width: '34px',
                  height: '34px',
                  backgroundColor: currentPage === pageNum ? '#1e3a5f' : undefined,
                  borderColor: currentPage === pageNum ? '#1e3a5f' : undefined,
                  fontSize: '0.85rem',
                }}
              >
                {pageNum.toString().padStart(2, '0')}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Modal para Crear Usuario Administrativo */}
      {isCreateModalOpen && (
        <div
          className="modal show d-block"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)', zIndex: 1055 }}
          tabIndex={-1}
        >
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content rounded-4 border-0 shadow">
              <div className="modal-header border-bottom py-3 px-4">
                <h5 className="modal-title fw-bold text-dark d-flex align-items-center gap-2">
                  <FaUserPlus className="text-primary" />
                  <span>Nuevo Usuario</span>
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setIsCreateModalOpen(false)}
                  disabled={savingUser}
                />
              </div>

              <form onSubmit={handleCreateUser}>
                <div className="modal-body p-4">
                  {createModalError && (
                    <div className="alert alert-danger py-2 px-3 small rounded-3 mb-3">
                      {createModalError}
                    </div>
                  )}

                  <div className="row g-3">
                    <div className="col-12 col-md-6">
                      <label className="form-label small fw-semibold text-secondary">
                        Nombres *
                      </label>
                      <input
                        type="text"
                        required
                        className="form-control form-control-sm rounded-3"
                        value={newNombres}
                        onChange={(e) => setNewNombres(e.target.value)}
                        placeholder="Ej. Carlos"
                      />
                    </div>
                    <div className="col-12 col-md-6">
                      <label className="form-label small fw-semibold text-secondary">
                        Apellidos *
                      </label>
                      <input
                        type="text"
                        required
                        className="form-control form-control-sm rounded-3"
                        value={newApellidos}
                        onChange={(e) => setNewApellidos(e.target.value)}
                        placeholder="Ej. Gómez"
                      />
                    </div>

                    <div className="col-12 col-md-6">
                      <label className="form-label small fw-semibold text-secondary">
                        DNI (8 dígitos) *
                      </label>
                      <input
                        type="text"
                        required
                        maxLength={8}
                        className="form-control form-control-sm rounded-3"
                        value={newDni}
                        onChange={(e) => setNewDni(e.target.value)}
                        placeholder="12345678"
                      />
                    </div>
                    <div className="col-12 col-md-6">
                      <label className="form-label small fw-semibold text-secondary">
                        Correo Electrónico
                      </label>
                      <input
                        type="email"
                        className="form-control form-control-sm rounded-3"
                        value={newCorreo}
                        onChange={(e) => setNewCorreo(e.target.value)}
                        placeholder="carlos@clinica.com"
                      />
                    </div>
                    <div className="col-12 col-md-6">
                      <label className="form-label small fw-semibold text-secondary">
                        Teléfono
                      </label>
                      <input
                        type="tel"
                        className="form-control form-control-sm rounded-3"
                        value={newTelefono}
                        onChange={(e) => setNewTelefono(e.target.value)}
                        placeholder="+51 987 654 321"
                      />
                    </div>

                    <div className="col-12 col-md-6">
                      <label className="form-label small fw-semibold text-secondary">
                        Rol Inicial *
                      </label>
                      <select
                        className="form-select form-select-sm rounded-3"
                        value={newRol}
                        onChange={(e) => setNewRol(e.target.value as User['rol'])}
                      >
                        {ROLES.map((r) => (
                          <option key={r.value} value={r.value}>
                            {r.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="col-12 col-md-6">
                      <label className="form-label small fw-semibold text-secondary">
                        Especialidad
                      </label>
                      <select
                        className="form-select form-select-sm rounded-3"
                        value={newEspecialidad}
                        onChange={(e) => setNewEspecialidad(e.target.value)}
                      >
                        {SPECIALTIES.map((esp) => (
                          <option key={esp} value={esp}>
                            {esp}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="col-12 col-md-6">
                      <label className="form-label small fw-semibold text-secondary">
                        Contraseña (mín 12 car.) *
                      </label>
                      <input
                        type="password"
                        required
                        className="form-control form-control-sm rounded-3"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="••••••••••••"
                      />
                    </div>
                    <div className="col-12 col-md-6">
                      <label className="form-label small fw-semibold text-secondary">
                        Confirmar Contraseña *
                      </label>
                      <input
                        type="password"
                        required
                        className="form-control form-control-sm rounded-3"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="••••••••••••"
                      />
                    </div>
                  </div>
                </div>

                <div className="modal-footer border-top py-2.5 px-4 d-flex justify-content-end gap-2">
                  <button
                    type="button"
                    className="btn btn-sm btn-light rounded-pill px-3"
                    onClick={() => setIsCreateModalOpen(false)}
                    disabled={savingUser}
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="btn btn-sm btn-primary rounded-pill px-4 shadow-sm"
                    style={{ backgroundColor: '#1e3a5f', borderColor: '#1e3a5f' }}
                    disabled={savingUser}
                  >
                    {savingUser ? 'Guardando...' : 'Guardar Usuario'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
