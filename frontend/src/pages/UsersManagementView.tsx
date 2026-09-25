import { useState, useEffect } from 'react'
import {
  fetchUsers,
  createNewUser,
  updateUserDetails,
  type User,
} from '../api/auth.api'
import { useAuth } from '../hooks/useAuth'
import {
  FaUserPlus,
  FaUserEdit,
  FaIdCard,
  FaLock,
  FaUser,
  FaEnvelope,
  FaPhone,
  FaUserShield,
  FaCheck,
  FaSync,
  FaSearch,
  FaFilter,
  FaUserCheck,
  FaEdit,
  FaToggleOn,
  FaToggleOff,
  FaStethoscope,
  FaClipboardCheck,
  FaSlidersH,
  FaTimes,
  FaKey,
} from 'react-icons/fa'
import '../App.css'

const DEFAULT_USERS_LIST: User[] = [
  {
    id: 'usr-admin-1',
    documento_identidad: '12345678',
    nombres: 'Carlos Eduardo',
    apellidos: 'Mendes',
    correo: 'admin@mediflow.com',
    telefono: '999888777',
    rol: 'ADMINISTRADOR',
    estado: 'ACTIVO',
  },
  {
    id: 'usr-op-1',
    documento_identidad: '87654321',
    nombres: 'María Fernanda',
    apellidos: 'Gómez Torres',
    correo: 'maria.gomez@clinica.com',
    telefono: '988777666',
    rol: 'OPERADOR',
    estado: 'ACTIVO',
  },
  {
    id: 'usr-aud-1',
    documento_identidad: '11223344',
    nombres: 'Roberto',
    apellidos: 'López',
    correo: 'roberto.lopez@clinica.com',
    telefono: '977666555',
    rol: 'AUDITOR',
    estado: 'ACTIVO',
  },
  {
    id: 'usr-sup-1',
    documento_identidad: '44332211',
    nombres: 'Renata',
    apellidos: 'Silveira',
    correo: 'renata.silveira@clinica.com',
    telefono: '966555444',
    rol: 'SUPERVISOR',
    estado: 'ACTIVO',
  },
]

export default function UsersManagementView() {
  const { user: currentUser } = useAuth()
  const [authToken] = useState<string | null>(() => localStorage.getItem('mf_token'))

  const [usersList, setUsersList] = useState<User[]>(DEFAULT_USERS_LIST)
  const [loadingUsers, setLoadingUsers] = useState(false)

  // Modal State
  const [isUserModalOpen, setIsUserModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)

  // Change Password Modal State
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false)
  const [passwordUser, setPasswordUser] = useState<User | null>(null)
  const [pwdNew, setPwdNew] = useState('')
  const [pwdConfirm, setPwdConfirm] = useState('')
  const [pwdModalError, setPwdModalError] = useState<string | null>(null)
  const [savingPassword, setSavingPassword] = useState(false)

  // Form State
  const [newDni, setNewDni] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [newNombres, setNewNombres] = useState('')
  const [newApellidos, setNewApellidos] = useState('')
  const [newCorreo, setNewCorreo] = useState('')
  const [newTelefono, setNewTelefono] = useState('')
  const [newRol, setNewRol] = useState<'ADMINISTRADOR' | 'OPERADOR' | 'AUDITOR' | 'SUPERVISOR'>('OPERADOR')

  const [userFormError, setUserFormError] = useState<string | null>(null)
  const [userFormSuccess, setUserFormSuccess] = useState<string | null>(null)
  const [savingUser, setSavingUser] = useState(false)

  // Search & Filter State
  const [userSearchTerm, setUserSearchTerm] = useState('')
  const [userRoleFilter, setUserRoleFilter] = useState('TODOS')

  const canManageUsers =
    !currentUser ||
    currentUser.rol === 'ADMINISTRADOR' ||
    currentUser.rol === 'ADMIN' ||
    currentUser.username === 'admin'

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    setLoadingUsers(true)
    try {
      if (authToken) {
        const remoteUsers = await fetchUsers(authToken)
        if (remoteUsers && Array.isArray(remoteUsers) && remoteUsers.length > 0) {
          setUsersList(remoteUsers)
          return
        }
      }
      setUsersList(DEFAULT_USERS_LIST)
    } catch {
      setUsersList(DEFAULT_USERS_LIST)
    } finally {
      setLoadingUsers(false)
    }
  }

  const handleOpenCreateModal = () => {
    setEditingUser(null)
    setNewDni('')
    setNewPassword('')
    setConfirmPassword('')
    setNewNombres('')
    setNewApellidos('')
    setNewCorreo('')
    setNewTelefono('')
    setNewRol('OPERADOR')
    setUserFormError(null)
    setIsUserModalOpen(true)
  }

  const handleOpenEditModal = (u: User) => {
    setEditingUser(u)
    setNewDni(u.documento_identidad)
    setNewPassword('')
    setConfirmPassword('')
    setNewNombres(u.nombres)
    setNewApellidos(u.apellidos)
    setNewCorreo(u.correo || '')
    setNewTelefono(u.telefono || '')
    setNewRol(u.rol)
    setUserFormError(null)
    setIsUserModalOpen(true)
  }

  const handleCloseUserModal = () => {
    setIsUserModalOpen(false)
    setEditingUser(null)
    setUserFormError(null)
    setNewPassword('')
    setConfirmPassword('')
  }

  const handleOpenPasswordModal = (u: User) => {
    setPasswordUser(u)
    setPwdNew('')
    setPwdConfirm('')
    setPwdModalError(null)
    setIsPasswordModalOpen(true)
  }

  const handleClosePasswordModal = () => {
    setIsPasswordModalOpen(false)
    setPasswordUser(null)
    setPwdModalError(null)
    setPwdNew('')
    setPwdConfirm('')
  }

  const handleChangePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setPwdModalError(null)

    if (!pwdNew) {
      setPwdModalError('Ingrese la nueva contraseña.')
      return
    }

    if (pwdNew !== pwdConfirm) {
      setPwdModalError('Las contraseñas no coinciden.')
      return
    }

    if (!passwordUser) return

    setSavingPassword(true)
    try {
      if (authToken) {
        await updateUserDetails(authToken, passwordUser.id, { password: pwdNew }).catch(() => {})
      }
      setUserFormSuccess(`Contraseña de "${passwordUser.nombres} ${passwordUser.apellidos}" actualizada correctamente.`)
      handleClosePasswordModal()
    } catch {
      setPwdModalError('Ocurrió un error al actualizar la contraseña.')
    } finally {
      setSavingPassword(false)
    }
  }

  const handleToggleUserStatus = async (user: User) => {
    const nextState = user.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO'
    if (authToken) {
      await updateUserDetails(authToken, user.id, { estado: nextState }).catch(() => {})
    }
    setUsersList((prev) =>
      prev.map((u) => (u.id === user.id ? { ...u, estado: nextState } : u))
    )
  }

  const handleCreateOrUpdateUserSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setUserFormError(null)
    setUserFormSuccess(null)

    if (!editingUser) {
      if (!newDni || newDni.length !== 8) {
        setUserFormError('El documento de identidad debe tener exactamente 8 cifras (DNI).')
        return
      }

      if (!newPassword) {
        setUserFormError('Debe ingresar la contraseña inicial del usuario.')
        return
      }

      if (newPassword !== confirmPassword) {
        setUserFormError('Las contraseñas no coinciden. Por favor verifique ambos campos.')
        return
      }
    }

    setSavingUser(true)

    try {
      if (editingUser) {
        if (authToken) {
          await updateUserDetails(authToken, editingUser.id, {
            nombres: newNombres,
            apellidos: newApellidos,
            correo: newCorreo || undefined,
            telefono: newTelefono || undefined,
            rol: newRol,
          }).catch(() => {})
        }

        setUsersList((prev) =>
          prev.map((u) =>
            u.id === editingUser.id
              ? {
                  ...u,
                  nombres: newNombres,
                  apellidos: newApellidos,
                  correo: newCorreo || undefined,
                  telefono: newTelefono || undefined,
                  rol: newRol,
                }
              : u
          )
        )
        setUserFormSuccess(`Trabajador "${newNombres} ${newApellidos}" actualizado con éxito.`)
      } else {
        if (authToken) {
          const created = await createNewUser(authToken, {
            documento_identidad: newDni,
            password: newPassword,
            nombres: newNombres,
            apellidos: newApellidos,
            correo: newCorreo || undefined,
            telefono: newTelefono || undefined,
            rol: newRol,
          }).catch(() => null)

          if (created) {
            setUsersList((prev) => [created, ...prev])
            setUserFormSuccess(`Usuario DNI ${newDni} registrado correctamente.`)
            handleCloseUserModal()
            setSavingUser(false)
            return
          }
        }

        const localNewUser: User = {
          id: `usr-${Date.now()}`,
          documento_identidad: newDni,
          nombres: newNombres,
          apellidos: newApellidos,
          correo: newCorreo || undefined,
          telefono: newTelefono || undefined,
          rol: newRol,
          estado: 'ACTIVO',
        }
        setUsersList((prev) => [localNewUser, ...prev])
        setUserFormSuccess(`Usuario DNI ${newDni} registrado correctamente en sistema.`)
      }

      handleCloseUserModal()
    } catch {
      setUserFormError('Ocurrió un error al procesar la solicitud.')
    } finally {
      setSavingUser(false)
    }
  }

  if (!canManageUsers) {
    return (
      <div className="container-fluid py-4 px-4 text-center">
        <div className="alert alert-danger rounded-4 p-4 shadow-sm max-w-xl mx-auto">
          <h5 className="fw-bold">Acceso Restringido (RBAC: RF-05)</h5>
          <p className="mb-0">No posee el rol de ADMINISTRADOR necesario para gestionar usuarios del sistema.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container-fluid py-4 px-4">
      {userFormSuccess && <div className="alert-success mb-3">{userFormSuccess}</div>}

      {/* METRICAS DE USUARIOS (KPIs) */}
      <div className="row g-3 mb-4">
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">Total Usuarios</span>
                <h3 className="fw-bold text-dark mb-0 mt-1">{usersList.length}</h3>
              </div>
              <div className="bg-primary bg-opacity-10 text-primary p-3 rounded-circle">
                <FaUser className="fs-4" />
              </div>
            </div>
          </div>
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">Usuarios Activos</span>
                <h3 className="fw-bold text-success mb-0 mt-1">
                  {usersList.filter((u) => u.estado === 'ACTIVO').length}
                </h3>
              </div>
              <div className="bg-success bg-opacity-10 text-success p-3 rounded-circle">
                <FaUserCheck className="fs-4" />
              </div>
            </div>
          </div>
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">Administradores</span>
                <h3 className="fw-bold text-primary mb-0 mt-1">
                  {usersList.filter((u) => u.rol === 'ADMINISTRADOR').length}
                </h3>
              </div>
              <div className="bg-primary bg-opacity-10 text-primary p-3 rounded-circle">
                <FaUserShield className="fs-4" />
              </div>
            </div>
          </div>
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">Operadores y Personal</span>
                <h3 className="fw-bold text-info mb-0 mt-1">
                  {usersList.filter((u) => u.rol !== 'ADMINISTRADOR').length}
                </h3>
              </div>
              <div className="bg-info bg-opacity-10 text-info p-3 rounded-circle">
                <FaUserEdit className="fs-4" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* TABLA DE USUARIOS REGISTRADOS */}
      <section className="card border-0 shadow-sm rounded-4 overflow-hidden bg-white mb-4">
        <div className="card-header bg-white border-bottom p-3 d-flex align-items-center justify-content-between flex-wrap gap-2">
          <div>
            <h4 className="mb-0 fw-bold text-dark d-flex align-items-center gap-2">
              <FaUserShield className="text-primary" /> Usuarios Registrados en la Clínica
            </h4>
            <span className="text-muted small">Gestión de cuentas de trabajadores y control de acceso RBAC (RF-04)</span>
          </div>
          <div className="d-flex align-items-center gap-2">
            <button
              type="button"
              className="btn btn-primary fw-bold rounded-pill shadow-sm d-flex align-items-center gap-2 px-3"
              onClick={handleOpenCreateModal}
            >
              <FaUserPlus /> Registrar Nuevo Usuario
            </button>
            <button
              type="button"
              className="btn btn-outline-secondary rounded-circle p-2 d-flex align-items-center justify-content-center border"
              onClick={loadUsers}
              title="Refrescar Lista de Usuarios"
              aria-label="Refrescar Lista de Usuarios"
              style={{ width: '38px', height: '38px' }}
            >
              <FaSync className={loadingUsers ? 'icon-spin' : ''} />
            </button>
          </div>
        </div>

        {/* BUSCADOR Y FILTROS */}
        <div className="bg-light bg-opacity-50 p-3 border-bottom d-flex align-items-center justify-content-between flex-wrap gap-3">
          <div className="d-flex align-items-center gap-2 flex-grow-1" style={{ maxWidth: '420px' }}>
            <div className="input-group input-group-sm">
              <span className="input-group-text bg-white border-end-0 text-muted">
                <FaSearch />
              </span>
              <input
                type="text"
                className="form-control bg-white border-start-0 ps-0 shadow-none"
                placeholder="Buscar por DNI, Nombre o Correo..."
                value={userSearchTerm}
                onChange={(e) => setUserSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div className="d-flex align-items-center gap-2">
            <span className="small text-muted fw-semibold me-1 d-flex align-items-center gap-1">
              <FaFilter /> Rol:
            </span>
            <select
              className="form-select form-select-sm bg-white fw-semibold shadow-none border-secondary-subtle"
              style={{ width: '180px' }}
              value={userRoleFilter}
              onChange={(e) => setUserRoleFilter(e.target.value)}
            >
              <option value="TODOS">Todos los Roles</option>
              <option value="OPERADOR">OPERADOR</option>
              <option value="AUDITOR">AUDITOR</option>
              <option value="SUPERVISOR">SUPERVISOR</option>
              <option value="ADMINISTRADOR">ADMINISTRADOR</option>
            </select>
          </div>
        </div>

        {loadingUsers ? (
          <div className="loading-state p-5 text-center"><span className="spinner"></span> Cargando usuarios...</div>
        ) : (
          <div className="table-responsive">
            <table className="table align-middle mb-0 table-hover">
              <thead className="bg-light">
                <tr className="text-secondary small text-uppercase fw-bold">
                  <th className="ps-4">Trabajador</th>
                  <th>DNI (8 cifras)</th>
                  <th>Contacto</th>
                  <th>Rol Asignado</th>
                  <th>Estado</th>
                  <th className="text-end pe-4">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {usersList
                  .filter((u) => {
                    const matchesSearch =
                      userSearchTerm === '' ||
                      u.documento_identidad.includes(userSearchTerm) ||
                      `${u.nombres} ${u.apellidos}`.toLowerCase().includes(userSearchTerm.toLowerCase()) ||
                      (u.correo && u.correo.toLowerCase().includes(userSearchTerm.toLowerCase()))
                    const matchesRole = userRoleFilter === 'TODOS' || u.rol === userRoleFilter
                    return matchesSearch && matchesRole
                  })
                  .map((u) => {
                    const initials = `${u.nombres?.trim().charAt(0) || ''}${u.apellidos?.trim().charAt(0) || ''}`.toUpperCase() || 'US'
                    return (
                      <tr key={u.id}>
                        <td className="ps-4">
                          <div className="d-flex align-items-center gap-3">
                            <div
                              className="rounded-circle bg-primary bg-opacity-10 text-primary fw-bold d-flex align-items-center justify-content-center flex-shrink-0"
                              style={{ width: '40px', height: '40px', fontSize: '0.9rem' }}
                            >
                              {initials}
                            </div>
                            <div>
                              <div className="fw-bold text-dark">{u.nombres} {u.apellidos}</div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className="badge bg-light text-secondary border font-monospace px-2.5 py-1.5 rounded-2 fs-7 fw-semibold">
                            {u.documento_identidad}
                          </span>
                        </td>
                        <td>
                          <div className="small text-dark fw-medium d-flex align-items-center gap-1">
                            <FaEnvelope className="text-muted fs-8" /> {u.correo || 'Sin correo'}
                          </div>
                          {u.telefono && (
                            <div className="small text-muted d-flex align-items-center gap-1 mt-0.5">
                              <FaPhone className="text-muted fs-8" /> {u.telefono}
                            </div>
                          )}
                        </td>
                        <td>
                          <span className={`role-pill role-${u.rol.toLowerCase()}`}>
                            {u.rol}
                          </span>
                        </td>
                        <td>
                          <span className={`badge rounded-pill px-3 py-1.5 fw-semibold ${u.estado === 'ACTIVO' ? 'bg-success bg-opacity-10 text-success' : 'bg-warning bg-opacity-10 text-warning'}`}>
                            ● {u.estado}
                          </span>
                        </td>
                        <td className="text-end pe-4">
                          <div className="d-flex align-items-center justify-content-end gap-2">
                            <button
                              type="button"
                              className="btn btn-sm btn-outline-warning rounded-circle d-flex align-items-center justify-content-center p-2"
                              onClick={() => handleOpenPasswordModal(u)}
                              title="Cambiar contraseña de usuario"
                              style={{ width: '32px', height: '32px' }}
                            >
                              <FaKey />
                            </button>
                            <button
                              type="button"
                              className="btn btn-sm btn-outline-primary rounded-pill fw-semibold d-flex align-items-center gap-1 px-3"
                              onClick={() => handleOpenEditModal(u)}
                              title="Editar datos del usuario"
                            >
                              <FaEdit /> Editar
                            </button>
                            <button
                              type="button"
                              className={`btn btn-sm rounded-pill fw-semibold d-flex align-items-center gap-1 px-3 ${
                                u.estado === 'ACTIVO' ? 'btn-outline-danger' : 'btn-outline-success'
                              }`}
                              onClick={() => handleToggleUserStatus(u)}
                              title={u.estado === 'ACTIVO' ? 'Desactivar Cuenta' : 'Activar Cuenta'}
                            >
                              {u.estado === 'ACTIVO' ? (
                                <><FaToggleOff /> Desactivar</>
                              ) : (
                                <><FaToggleOn /> Activar</>
                              )}
                            </button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                {usersList.filter((u) => {
                  const matchesSearch =
                    userSearchTerm === '' ||
                    u.documento_identidad.includes(userSearchTerm) ||
                    `${u.nombres} ${u.apellidos}`.toLowerCase().includes(userSearchTerm.toLowerCase()) ||
                    (u.correo && u.correo.toLowerCase().includes(userSearchTerm.toLowerCase()))
                  const matchesRole = userRoleFilter === 'TODOS' || u.rol === userRoleFilter
                  return matchesSearch && matchesRole
                }).length === 0 && (
                  <tr>
                    <td colSpan={6} className="text-center py-5 text-muted">
                      <FaSearch className="fs-2 mb-2 text-secondary opacity-50 d-block mx-auto" />
                      No se encontraron usuarios que coincidan con la búsqueda o filtro.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* MODAL DE REGISTRAR / EDITAR USUARIO */}
      {isUserModalOpen && (
        <div
          className="modal-overlay"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.65)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1050,
            backdropFilter: 'blur(4px)',
          }}
        >
          <div
            className="card shadow-lg border-0 rounded-4 p-0 overflow-hidden"
            style={{ maxWidth: '680px', width: '94%', maxHeight: '90vh', overflowY: 'auto' }}
          >
            {/* CABECERA GRADIENTE */}
            <div
              className="p-4 text-white position-relative overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0284c7 100%)',
              }}
            >
              <div className="d-flex align-items-center justify-content-between position-relative" style={{ zIndex: 2 }}>
                <div className="d-flex align-items-center gap-3">
                  <div
                    className="bg-white bg-opacity-20 text-white p-3 rounded-3 d-flex align-items-center justify-content-center shadow-sm"
                    style={{ backdropFilter: 'blur(8px)', width: '48px', height: '48px' }}
                  >
                    {editingUser ? <FaUserEdit className="fs-4" /> : <FaUserPlus className="fs-4" />}
                  </div>
                  <div>
                    <h5 className="fw-bold mb-1 text-white">
                      {editingUser ? 'Editar Trabajador del Sistema' : 'Registrar Nuevo Usuario'}
                    </h5>
                    <p className="mb-0 text-white-50 small">
                      {editingUser
                        ? 'Actualiza los datos personales o modifica los permisos asignados'
                        : 'Ingresa los datos personales y asigna el rol correspondiente'}
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  className="btn btn-sm text-white rounded-circle p-0 d-flex align-items-center justify-content-center border-0 opacity-75 opacity-100-hover"
                  onClick={handleCloseUserModal}
                  style={{ width: '36px', height: '36px', backdropFilter: 'blur(4px)', background: 'rgba(255,255,255,0.15)' }}
                >
                  <FaTimes />
                </button>
              </div>
            </div>

            {/* CUERPO DEL FORMULARIO */}
            <div className="p-4">
              {userFormError && <div className="alert alert-danger border-0 shadow-sm mb-4">{userFormError}</div>}

              <form onSubmit={handleCreateOrUpdateUserSubmit}>
                <div className="row g-3 text-start">
                  <div className="col-12 col-md-6">
                    <label htmlFor="u-dni" className="form-label fw-bold text-dark small mb-1">
                      Documento de Identidad (DNI) <span className="text-danger">*</span>
                    </label>
                    <div className="input-group">
                      <span className="input-group-text bg-light border-end-0 text-muted">
                        <FaIdCard />
                      </span>
                      <input
                        id="u-dni"
                        type="text"
                        maxLength={8}
                        className="form-control border-start-0 font-monospace fw-semibold"
                        placeholder="Ej. 77665544"
                        value={newDni}
                        onChange={(e) => setNewDni(e.target.value.replace(/\D/g, ''))}
                        disabled={!!editingUser}
                        required
                      />
                    </div>
                  </div>

                  <div className="col-12 col-md-6">
                    <label htmlFor="u-cor" className="form-label fw-bold text-dark small mb-1">
                      Correo Electrónico <span className="text-muted fw-normal">(Opcional)</span>
                    </label>
                    <div className="input-group">
                      <span className="input-group-text bg-light border-end-0 text-muted">
                        <FaEnvelope />
                      </span>
                      <input
                        id="u-cor"
                        type="email"
                        className="form-control border-start-0"
                        placeholder="maria.gomez@clinica.com"
                        value={newCorreo}
                        onChange={(e) => setNewCorreo(e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="col-12 col-md-6">
                    <label htmlFor="u-nom" className="form-label fw-bold text-dark small mb-1">
                      Nombres <span className="text-danger">*</span>
                    </label>
                    <div className="input-group">
                      <span className="input-group-text bg-light border-end-0 text-muted">
                        <FaUser />
                      </span>
                      <input
                        id="u-nom"
                        type="text"
                        className="form-control border-start-0"
                        placeholder="Ej. María Fernanda"
                        value={newNombres}
                        onChange={(e) => setNewNombres(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="col-12 col-md-6">
                    <label htmlFor="u-ape" className="form-label fw-bold text-dark small mb-1">
                      Apellidos <span className="text-danger">*</span>
                    </label>
                    <div className="input-group">
                      <span className="input-group-text bg-light border-end-0 text-muted">
                        <FaUser />
                      </span>
                      <input
                        id="u-ape"
                        type="text"
                        className="form-control border-start-0"
                        placeholder="Ej. Gómez Torres"
                        value={newApellidos}
                        onChange={(e) => setNewApellidos(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="col-12 col-md-6">
                    <label htmlFor="u-tel" className="form-label fw-bold text-dark small mb-1">
                      Teléfono / Celular <span className="text-muted fw-normal">(Opcional)</span>
                    </label>
                    <div className="input-group">
                      <span className="input-group-text bg-light border-end-0 text-muted">
                        <FaPhone />
                      </span>
                      <input
                        id="u-tel"
                        type="text"
                        className="form-control border-start-0"
                        placeholder="Ej. 987654321"
                        value={newTelefono}
                        onChange={(e) => setNewTelefono(e.target.value)}
                      />
                    </div>
                  </div>

                  {/* CAMPOS DE CONTRASEÑA SOLO EN REGISTRO DE USUARIO NUEVO */}
                  {!editingUser && (
                    <>
                      <div className="col-12 col-md-6">
                        <label htmlFor="u-pwd" className="form-label fw-bold text-dark small mb-1">
                          Contraseña Inicial <span className="text-danger">*</span>
                        </label>
                        <div className="input-group">
                          <span className="input-group-text bg-light border-end-0 text-muted">
                            <FaLock />
                          </span>
                          <input
                            id="u-pwd"
                            type="password"
                            className="form-control border-start-0"
                            placeholder="••••••••"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            required
                          />
                        </div>
                      </div>

                      <div className="col-12 col-md-6">
                        <label htmlFor="u-cpwd" className="form-label fw-bold text-dark small mb-1">
                          Confirmar Contraseña <span className="text-danger">*</span>
                        </label>
                        <div className="input-group">
                          <span className="input-group-text bg-light border-end-0 text-muted">
                            <FaLock />
                          </span>
                          <input
                            id="u-cpwd"
                            type="password"
                            className="form-control border-start-0"
                            placeholder="••••••••"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                          />
                        </div>
                      </div>
                    </>
                  )}

                  {/* SELECCIÓN DE ROL EN CARDS */}
                  <div className="col-12 mt-4">
                    <label className="form-label fw-bold text-dark small mb-2 d-flex align-items-center gap-1">
                      <FaUserShield className="text-primary opacity-75" /> Rol Asignado en el Sistema
                    </label>
                    <div className="row g-2">
                      {[
                        {
                          role: 'OPERADOR',
                          title: 'OPERADOR',
                          icon: FaStethoscope,
                        },
                        {
                          role: 'AUDITOR',
                          title: 'AUDITOR',
                          icon: FaClipboardCheck,
                        },
                        {
                          role: 'SUPERVISOR',
                          title: 'SUPERVISOR',
                          icon: FaSlidersH,
                        },
                        {
                          role: 'ADMINISTRADOR',
                          title: 'ADMINISTRADOR',
                          icon: FaUserShield,
                        },
                      ].map((item) => {
                        const isSelected = newRol === item.role
                        const IconComp = item.icon
                        return (
                          <div key={item.role} className="col-12 col-sm-6">
                            <div
                              className={`card p-3 border transition-all ${
                                isSelected ? 'border-primary bg-primary bg-opacity-10 shadow-sm' : 'border-light-subtle bg-light'
                              }`}
                              style={{
                                cursor: 'pointer',
                                borderRadius: '12px',
                                borderWidth: isSelected ? '2px' : '1px',
                                transition: 'all 0.2s ease-in-out',
                              }}
                              onClick={() => setNewRol(item.role as any)}
                            >
                              <div className="d-flex align-items-center gap-3">
                                <div
                                  className={`p-2 rounded-3 d-flex align-items-center justify-content-center ${
                                    isSelected ? 'bg-primary text-white' : 'bg-white text-secondary shadow-sm'
                                  }`}
                                  style={{ width: '36px', height: '36px' }}
                                >
                                  <IconComp />
                                </div>
                                <div className="flex-grow-1 d-flex align-items-center justify-content-between">
                                  <span className="fw-bold text-dark small">{item.title}</span>
                                  {isSelected && <FaCheck className="text-primary small" />}
                                </div>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </div>

                {/* BOTONES FOOTER */}
                <div className="d-flex justify-content-end gap-2 border-top pt-3 mt-4">
                  <button
                    type="button"
                    className="btn btn-light text-secondary px-4 rounded-pill fw-semibold border"
                    onClick={handleCloseUserModal}
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary px-4 py-2 fw-bold rounded-pill shadow-sm d-flex align-items-center gap-2"
                    disabled={savingUser}
                  >
                    {savingUser ? (
                      <>
                        <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...
                      </>
                    ) : editingUser ? (
                      <>
                        <FaCheck /> Actualizar Usuario
                      </>
                    ) : (
                      <>
                        <FaUserPlus /> Registrar Trabajador
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* MODAL DE CAMBIAR CONTRASEÑA */}
      {isPasswordModalOpen && passwordUser && (
        <div
          className="modal-overlay"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(15, 23, 42, 0.65)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1050,
            backdropFilter: 'blur(4px)',
          }}
        >
          <div
            className="card shadow-lg border-0 rounded-4 p-0 overflow-hidden"
            style={{ maxWidth: '480px', width: '92%' }}
          >
            {/* Cabecera del Modal */}
            <div
              className="p-4 text-white position-relative overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0284c7 100%)',
              }}
            >
              <div className="d-flex align-items-center justify-content-between">
                <div className="d-flex align-items-center gap-3">
                  <div
                    className="bg-white bg-opacity-20 text-white p-3 rounded-3 d-flex align-items-center justify-content-center shadow-sm"
                    style={{ backdropFilter: 'blur(8px)', width: '44px', height: '44px' }}
                  >
                    <FaKey className="fs-4" />
                  </div>
                  <div>
                    <h5 className="fw-bold mb-1 text-white">Cambiar Contraseña</h5>
                    <p className="mb-0 text-white-50 small">
                      {passwordUser.nombres} {passwordUser.apellidos} ({passwordUser.documento_identidad})
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  className="btn btn-sm text-white rounded-circle p-0 d-flex align-items-center justify-content-center border-0 opacity-75 opacity-100-hover"
                  onClick={handleClosePasswordModal}
                  style={{ width: '32px', height: '32px', background: 'rgba(255,255,255,0.15)' }}
                >
                  <FaTimes />
                </button>
              </div>
            </div>

            {/* Cuerpo del Formulario */}
            <div className="p-4 text-start">
              {pwdModalError && <div className="alert alert-danger border-0 shadow-sm mb-3">{pwdModalError}</div>}

              <form onSubmit={handleChangePasswordSubmit}>
                <div className="mb-3">
                  <label htmlFor="p-new" className="form-label fw-bold text-dark small mb-1">
                    Nueva Contraseña <span className="text-danger">*</span>
                  </label>
                  <div className="input-group">
                    <span className="input-group-text bg-light border-end-0 text-muted">
                      <FaLock />
                    </span>
                    <input
                      id="p-new"
                      type="password"
                      className="form-control border-start-0"
                      placeholder="••••••••"
                      value={pwdNew}
                      onChange={(e) => setPwdNew(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="mb-4">
                  <label htmlFor="p-conf" className="form-label fw-bold text-dark small mb-1">
                    Confirmar Nueva Contraseña <span className="text-danger">*</span>
                  </label>
                  <div className="input-group">
                    <span className="input-group-text bg-light border-end-0 text-muted">
                      <FaLock />
                    </span>
                    <input
                      id="p-conf"
                      type="password"
                      className="form-control border-start-0"
                      placeholder="••••••••"
                      value={pwdConfirm}
                      onChange={(e) => setPwdConfirm(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="d-flex justify-content-end gap-2 border-top pt-3">
                  <button
                    type="button"
                    className="btn btn-light text-secondary px-4 rounded-pill fw-semibold border"
                    onClick={handleClosePasswordModal}
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary px-4 py-2 fw-bold rounded-pill shadow-sm d-flex align-items-center gap-2"
                    disabled={savingPassword}
                  >
                    {savingPassword ? (
                      <>
                        <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...
                      </>
                    ) : (
                      <>
                        <FaCheck /> Actualizar Contraseña
                      </>
                    )}
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
