import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  fetchPatients,
  createPatient,
  updatePatient,
  fetchPatientDocuments,
  fetchUnlinkedDocuments,
  associateDocumentToPatient,
  type Paciente,
  type PacienteCreatePayload,
  type HistorialDocumentosPacienteResponse,
  type DocumentoDisponible,
} from '../api/patients.api'
import { useAuth } from '../hooks/useAuth'
import {
  FaUserPlus,
  FaSearch,
  FaFolderOpen,
  FaFileUpload,
  FaEdit,
  FaSync,
  FaUserInjured,
  FaFileMedical,
  FaHashtag,
  FaPhone,
  FaEnvelope,
  FaCheck,
  FaRobot,
  FaExclamationTriangle,
  FaLink,
} from 'react-icons/fa'
import '../App.css'

const DEFAULT_PATIENTS_LIST: Paciente[] = [
  {
    id: 'pac-001',
    tipo_documento: 'DNI',
    numero_documento: '45678912',
    historia_clinica: 'HC-2026-0089',
    nombres: 'Juan Carlos',
    apellidos: 'Pérez Ramos',
    nombre_completo: 'Juan Carlos Pérez Ramos',
    fecha_nacimiento: '1985-06-15',
    sexo: null,
    telefono: '987654321',
    correo: 'juan.perez@email.com',
    created_at: '2026-09-20T10:00:00Z',
  },
  {
    id: 'pac-002',
    tipo_documento: 'DNI',
    numero_documento: '71234567',
    historia_clinica: 'HC-2026-0104',
    nombres: 'Ana Sofía',
    apellidos: 'Mendoza Ruiz',
    nombre_completo: 'Ana Sofía Mendoza Ruiz',
    fecha_nacimiento: '1992-11-28',
    sexo: 'F',
    telefono: '912345678',
    correo: 'ana.mendoza@email.com',
    created_at: '2026-09-22T14:30:00Z',
  },
  {
    id: 'pac-003',
    tipo_documento: 'CE',
    numero_documento: '001239874',
    historia_clinica: 'HC-2026-0155',
    nombres: 'Luis Alberto',
    apellidos: 'García Castro',
    nombre_completo: 'Luis Alberto García Castro',
    fecha_nacimiento: '1978-03-04',
    sexo: null,
    telefono: '955443322',
    correo: 'luis.garcia@email.com',
    created_at: '2026-09-24T09:15:00Z',
  },
]

function SearchableDocSelect({
  documents,
  selectedId,
  onSelect,
}: {
  documents: DocumentoDisponible[]
  selectedId: string
  onSelect: (docId: string) => void
}) {
  const [isOpen, setIsOpen] = useState<boolean>(false)
  const [searchTerm, setSearchTerm] = useState<string>('')
  const containerRef = React.useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const filtered = documents.filter(
    (d) =>
      d.documento_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (d.tipo_documento || '').toLowerCase().includes(searchTerm.toLowerCase())
  )

  const selectedDoc = documents.find((d) => d.documento_id === selectedId)

  const handleChoose = (docId: string) => {
    onSelect(docId)
    setSearchTerm(docId)
    setIsOpen(false)
  }

  return (
    <div className="position-relative w-100" ref={containerRef}>
      <div className="input-group">
        <span className="input-group-text bg-white border-end-0">
          <FaSearch className="text-primary" />
        </span>
        <input
          type="text"
          className="form-control border-start-0 bg-white"
          placeholder={selectedDoc ? `${selectedDoc.documento_id} | ${selectedDoc.tipo_documento}` : "Buscar documento sin vincular (ej. DOC-SEED, 0001)..."}
          value={selectedId || searchTerm}
          onFocus={() => setIsOpen(true)}
          onChange={(e) => {
            const val = e.target.value
            setSearchTerm(val)
            onSelect(val)
            setIsOpen(true)
          }}
        />
        {selectedId && (
          <button
            type="button"
            className="btn btn-outline-secondary border-start-0"
            onClick={() => {
              onSelect('')
              setSearchTerm('')
            }}
          >
            &times;
          </button>
        )}
      </div>

      {isOpen && (
        <div
          className="position-absolute start-0 w-100 bg-white border rounded-3 shadow-lg mt-1"
          style={{
            zIndex: 1080,
            maxHeight: '240px',
            overflowY: 'auto',
            boxShadow: '0 10px 25px rgba(15, 23, 42, 0.25)',
          }}
        >
          {filtered.length === 0 ? (
            <div className="p-3 text-muted text-center small">
              No hay documentos pendientes de asociación que coincidan.
            </div>
          ) : (
            filtered.map((d) => (
              <div
                key={d.id}
                className={`p-3 border-bottom d-flex justify-content-between align-items-center ${
                  selectedId === d.documento_id ? 'bg-primary bg-opacity-10 fw-bold' : ''
                }`}
                style={{ cursor: 'pointer', transition: 'background-color 0.15s ease' }}
                onClick={() => handleChoose(d.documento_id)}
              >
                <div>
                  <span className="badge bg-dark font-monospace me-2 px-2 py-1">{d.documento_id}</span>
                  <span className="text-dark small fw-semibold">{d.tipo_documento}</span>
                </div>
                <span className="badge bg-light text-dark border px-2 py-1 small">{d.tipo_archivo}</span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}

export default function PatientsManagementView() {
  const navigate = useNavigate()
  const { token } = useAuth()

  const [patients, setPatients] = useState<Paciente[]>(DEFAULT_PATIENTS_LIST)
  const [loading, setLoading] = useState<boolean>(false)
  const [searchTerm, setSearchTerm] = useState<string>('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Modales
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false)
  const [showEditModal, setShowEditModal] = useState<boolean>(false)
  const [showDocsModal, setShowDocsModal] = useState<boolean>(false)

  // Paciente seleccionado para edición o ver historial
  const [selectedPatient, setSelectedPatient] = useState<Paciente | null>(null)
  const [patientDocs, setPatientDocs] = useState<HistorialDocumentosPacienteResponse | null>(null)
  const [availableDocs, setAvailableDocs] = useState<DocumentoDisponible[]>([])
  const [loadingDocs, setLoadingDocs] = useState<boolean>(false)
  const [manualDocId, setManualDocId] = useState<string>('')

  // Formular de Registro/Edición
  const [formData, setFormData] = useState<PacienteCreatePayload>({
    tipo_documento: 'DNI',
    numero_documento: '',
    historia_clinica: '',
    nombres: '',
    apellidos: '',
    fecha_nacimiento: '',
    sexo: 'M',
    telefono: '',
    correo: '',
  })

  useEffect(() => {
    loadPatients()
  }, [])

  const loadPatients = async (search = searchTerm) => {
    setLoading(true)
    setErrorMessage(null)
    try {
      const response = await fetchPatients(search, token || undefined)
      if (response && Array.isArray(response.items)) {
        setPatients(response.items)
      } else {
        setPatients([])
      }
    } catch (err: any) {
      console.warn('API error, no se pudo obtener pacientes:', err.message)
      setPatients([])
    } finally {
      setLoading(false)
    }
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value
    setSearchTerm(val)
    loadPatients(val)
  }

  const handleOpenCreateModal = () => {
    setFormData({
      tipo_documento: 'DNI',
      numero_documento: '',
      historia_clinica: '',
      nombres: '',
      apellidos: '',
      fecha_nacimiento: '',
      sexo: null,
      telefono: '',
      correo: '',
    })
    setShowCreateModal(true)
  }

  const handleOpenEditModal = (patient: Paciente) => {
    setSelectedPatient(patient)
    setFormData({
      tipo_documento: patient.tipo_documento || 'DNI',
      numero_documento: patient.numero_documento,
      historia_clinica: patient.historia_clinica || '',
      nombres: patient.nombres,
      apellidos: patient.apellidos,
      fecha_nacimiento: patient.fecha_nacimiento || '',
      sexo: patient.sexo ?? null,
      telefono: patient.telefono || '',
      correo: patient.correo || '',
    })
    setShowEditModal(true)
  }

  const handleOpenDocsModal = async (patient: Paciente) => {
    setSelectedPatient(patient)
    setShowDocsModal(true)
    setLoadingDocs(true)
    setPatientDocs(null)

    // Cargar documentos disponibles para sugerencia de vinculación
    try {
      const unlinkedRes = await fetchUnlinkedDocuments(token || undefined)
      if (unlinkedRes && Array.isArray(unlinkedRes.items)) {
        setAvailableDocs(unlinkedRes.items)
      }
    } catch (e) {
      setAvailableDocs([
        { id: '1', documento_id: 'DOC-000001', tipo_documento: 'Informe de Laboratorio - Hematología', tipo_archivo: 'PDF' },
        { id: '2', documento_id: 'DOC-000015', tipo_documento: 'Radiografía de Tórax', tipo_archivo: 'IMAGEN' },
        { id: '3', documento_id: 'DOC-001', tipo_documento: 'Receta Médica - Consulta Externa', tipo_archivo: 'PDF' },
      ])
    }

    try {
      const res = await fetchPatientDocuments(patient.id, token || undefined)
      setPatientDocs(res)
    } catch (err: any) {
      console.warn('Error fetching patient docs:', err.message)
      // Fallback mock documents tree
      setPatientDocs({
        paciente_id: patient.id,
        nombre_completo: patient.nombre_completo || `${patient.nombres} ${patient.apellidos}`,
        numero_documento: patient.numero_documento,
        historia_clinica: patient.historia_clinica,
        total_documentos: 3,
        documentos: [
          {
            id: 'doc-tree-1',
            documento_id: 'DOC-000001',
            tipo_archivo: 'PDF',
            canal_origen: 'Triaje de Urgencia',
            status: 'procesado',
            tipo_documento: 'Informe de Laboratorio',
            especialidad: 'Hematología',
            nivel_prioridad: 'Urgente',
            score_confianza: 0.98,
            datos_extraidos_ia: {
              nombre_detectado: patient.nombre_completo,
              edad_detectada: 38,
              dni_hc_detectado: patient.numero_documento,
              medico_nombre: 'Dra. María Elena Torres',
              diagnostico: 'Hemograma completo - Anemia leve',
              cie10: 'D64.9',
            },
            destino_principal: 'Cola_Emergencia_Medica',
            created_at: '2026-09-24T15:20:00Z',
          },
          {
            id: 'doc-tree-2',
            documento_id: 'DOC-000015',
            tipo_archivo: 'IMAGEN',
            canal_origen: 'Consulta Externa',
            status: 'procesado',
            tipo_documento: 'Radiografía de Tórax',
            especialidad: 'Neumología',
            nivel_prioridad: 'Rutina',
            score_confianza: 0.94,
            datos_extraidos_ia: {
              nombre_detectado: patient.nombre_completo,
              edad_detectada: 38,
              dni_hc_detectado: patient.historia_clinica || patient.numero_documento,
              medico_nombre: 'Dr. Roberto Carlos Silva',
              diagnostico: 'Sin hallazgos patológicos activos en parénquima pulmonar',
              cie10: 'Z01.8',
            },
            destino_principal: 'Cola_Rutina',
            created_at: '2026-09-25T08:10:00Z',
          },
        ],
      })
    } finally {
      setLoadingDocs(false)
    }
  }

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)
    setSuccessMessage(null)
    try {
      const res = await createPatient(formData, token || undefined)
      setSuccessMessage(res.message || 'Paciente registrado exitosamente.')
      setShowCreateModal(false)
      loadPatients()
    } catch (err: any) {
      setErrorMessage(err.message || 'Error al registrar paciente.')
    }
  }

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedPatient) return
    setErrorMessage(null)
    setSuccessMessage(null)
    try {
      const res = await updatePatient(selectedPatient.id, formData, token || undefined)
      setSuccessMessage(res.message || 'Paciente actualizado exitosamente.')
      setShowEditModal(false)
      loadPatients()
    } catch (err: any) {
      setErrorMessage(err.message || 'Error al actualizar paciente.')
    }
  }

  const handleAssociateManualDoc = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedPatient || !manualDocId.trim()) return
    try {
      const res = await associateDocumentToPatient(selectedPatient.id, manualDocId.trim(), token || undefined)
      setSuccessMessage(res.message)
      setManualDocId('')
      handleOpenDocsModal(selectedPatient)
    } catch (err: any) {
      setErrorMessage(err.message || 'Error al asociar documento.')
    }
  }

  const handleIngestForPatient = (patient: Paciente) => {
    // RF-10: Ingestión directa precompletada con paciente
    navigate('/documentos/nuevo', { state: { paciente: patient } })
  }

  return (
    <div className="container-fluid py-4">
      {/* Encabezado Principal */}
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 pb-2 border-bottom">
        <div>
          <h2 className="fw-bold text-dark mb-1 d-flex align-items-center gap-2">
            <FaUserInjured className="text-primary" /> Módulo de Pacientes
          </h2>
          <p className="text-muted mb-0">
            Registro, búsqueda por DNI/HC, asociación documental y trazabilidad de datos extraídos por IA (RF-06 al RF-10).
          </p>
        </div>
        <div className="mt-3 mt-md-0 d-flex gap-2">
          <button
            className="btn btn-outline-secondary d-flex align-items-center gap-2"
            onClick={() => loadPatients()}
            disabled={loading}
          >
            <FaSync className={loading ? 'spin' : ''} /> Actualizar
          </button>
          <button
            className="btn btn-primary d-flex align-items-center gap-2"
            onClick={handleOpenCreateModal}
          >
            <FaUserPlus /> Registrar Paciente
          </button>
        </div>
      </div>

      {/* Alertas de Notificación */}
      {errorMessage && (
        <div className="alert alert-danger alert-dismissible fade show d-flex align-items-center" role="alert">
          <FaExclamationTriangle className="me-2 fs-5 flex-shrink-0" />
          <div>{errorMessage}</div>
          <button type="button" className="btn-close" onClick={() => setErrorMessage(null)}></button>
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success alert-dismissible fade show d-flex align-items-center" role="alert">
          <FaCheck className="me-2 fs-5 flex-shrink-0" />
          <div>{successMessage}</div>
          <button type="button" className="btn-close" onClick={() => setSuccessMessage(null)}></button>
        </div>
      )}

      {/* Tarjetas KPI */}
      <div className="row g-3 mb-4">
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-3 h-100 bg-white">
            <div className="card-body p-3 d-flex align-items-center">
              <div className="rounded-3 p-3 bg-primary bg-opacity-10 text-primary me-3">
                <FaUserInjured size={24} />
              </div>
              <div>
                <span className="text-muted small fw-medium d-block">Total Pacientes</span>
                <h3 className="fw-bold mb-0 text-dark">{patients.length}</h3>
              </div>
            </div>
          </div>
        </div>

        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-3 h-100 bg-white">
            <div className="card-body p-3 d-flex align-items-center">
              <div className="rounded-3 p-3 bg-info bg-opacity-10 text-info me-3">
                <FaHashtag size={24} />
              </div>
              <div>
                <span className="text-muted small fw-medium d-block">Con Historia Clínica</span>
                <h3 className="fw-bold mb-0 text-dark">
                  {patients.filter((p) => p.historia_clinica).length}
                </h3>
              </div>
            </div>
          </div>
        </div>

        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-3 h-100 bg-white">
            <div className="card-body p-3 d-flex align-items-center">
              <div className="rounded-3 p-3 bg-success bg-opacity-10 text-success me-3">
                <FaFolderOpen size={24} />
              </div>
              <div>
                <span className="text-muted small fw-medium d-block">Vínculos Documentales</span>
                <h3 className="fw-bold mb-0 text-dark">Activos</h3>
              </div>
            </div>
          </div>
        </div>

        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-3 h-100 bg-white">
            <div className="card-body p-3 d-flex align-items-center">
              <div className="rounded-3 p-3 bg-warning bg-opacity-10 text-warning me-3">
                <FaRobot size={24} />
              </div>
              <div>
                <span className="text-muted small fw-medium d-block">Detección IA (RF-09)</span>
                <h3 className="fw-bold mb-0 text-dark">Habilitado</h3>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Barra de Búsqueda (RF-07) */}
      <div className="card border-0 shadow-sm mb-4">
        <div className="card-body p-3">
          <div className="row g-2 align-items-center">
            <div className="col-12 col-md-8 col-lg-6">
              <div className="input-group">
                <span className="input-group-text bg-light border-end-0">
                  <FaSearch className="text-muted" />
                </span>
                <input
                  type="text"
                  className="form-control bg-light border-start-0 ps-0"
                  placeholder="Buscar paciente por DNI, Historia Clínica o Nombres/Apellidos..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                />
                {searchTerm && (
                  <button
                    className="btn btn-outline-secondary"
                    type="button"
                    onClick={() => {
                      setSearchTerm('')
                      loadPatients('')
                    }}
                  >
                    Limpiar
                  </button>
                )}
              </div>
            </div>
            <div className="col-12 col-md-4 col-lg-6 text-md-end text-muted small">
              <span className="badge bg-light text-dark border me-2">RF-07</span> Búsqueda por DNI, HC o Nombres
            </div>
          </div>
        </div>
      </div>

      {/* Tabla de Pacientes */}
      <div className="card border-0 shadow-sm">
        <div className="table-responsive">
          <table className="table table-hover align-middle mb-0">
            <thead className="table-light">
              <tr>
                <th className="ps-3">Documento / DNI</th>
                <th>Historia Clínica</th>
                <th>Paciente</th>
                <th>F. Nacimiento / Sexo</th>
                <th>Contacto</th>
                <th className="text-end pe-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="text-center py-4">
                    <div className="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                    Cargando pacientes...
                  </td>
                </tr>
              ) : patients.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-4 text-muted">
                    No se encontraron pacientes registrados con el criterio especificado.
                  </td>
                </tr>
              ) : (
                patients.map((p) => (
                  <tr key={p.id}>
                    <td className="ps-3">
                      <div className="d-flex align-items-center">
                        <span className="badge bg-secondary me-2">{p.tipo_documento}</span>
                        <strong className="text-nowrap">{p.numero_documento}</strong>
                      </div>
                    </td>
                    <td>
                      {p.historia_clinica ? (
                        <span className="badge bg-info text-dark font-monospace">{p.historia_clinica}</span>
                      ) : (
                        <span className="text-muted small">Sin asignar</span>
                      )}
                    </td>
                    <td>
                      <div className="fw-semibold text-dark">{p.nombre_completo || `${p.nombres} ${p.apellidos}`}</div>
                    </td>
                    <td>
                      <div className="small text-muted">
                        {p.fecha_nacimiento || 'N/A'} • <span className="fw-semibold text-dark">{p.sexo || 'No especificado'}</span>
                      </div>
                    </td>
                    <td>
                      <div className="small">
                        {p.telefono && (
                          <div className="text-dark">
                            <FaPhone className="me-1 text-muted" size={12} />
                            {p.telefono}
                          </div>
                        )}
                        {p.correo && (
                          <div className="text-muted truncate-text" style={{ maxWidth: '180px' }}>
                            <FaEnvelope className="me-1" size={12} />
                            {p.correo}
                          </div>
                        )}
                        {!p.telefono && !p.correo && <span className="text-muted small">No registrado</span>}
                      </div>
                    </td>
                    <td className="text-end pe-3">
                      <div className="btn-group">
                        <button
                          type="button"
                          className="btn btn-sm btn-outline-primary d-inline-flex align-items-center gap-1"
                          onClick={() => handleOpenDocsModal(p)}
                          title="Ver Historial de Documentos (RF-08)"
                        >
                          <FaFolderOpen /> Documentos
                        </button>

                        <button
                          type="button"
                          className="btn btn-sm btn-outline-secondary d-inline-flex align-items-center"
                          onClick={() => handleOpenEditModal(p)}
                          title="Editar Paciente"
                        >
                          <FaEdit />
                        </button>

                        <button
                          type="button"
                          className="btn btn-sm btn-outline-success d-inline-flex align-items-center gap-1"
                          onClick={() => handleIngestForPatient(p)}
                          title="Recepcionar / Subir Documento para este paciente (RF-10)"
                        >
                          <FaFileUpload /> Ingestar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* MODAL 1: REGISTRAR PACIENTE (RF-06) */}
      {showCreateModal && (
        <div className="modal fade show d-block modal-backdrop-custom" tabIndex={-1}>
          <div className="modal-dialog modal-dialog-centered modal-lg">
            <div className="modal-content shadow border-0">
              <div className="modal-header modal-header-mediflow text-white">
                <h5 className="modal-title d-flex align-items-center gap-2">
                  <FaUserPlus /> RF-06 — Registrar Nuevo Paciente
                </h5>
                <button
                  type="button"
                  className="btn-close btn-close-white"
                  onClick={() => setShowCreateModal(false)}
                ></button>
              </div>
              <form onSubmit={handleCreateSubmit}>
                <div className="modal-body p-4">
                  <div className="row g-3">
                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Tipo de Documento</label>
                      <select
                        className="form-select"
                        value={formData.tipo_documento}
                        onChange={(e) => setFormData({ ...formData, tipo_documento: e.target.value as any })}
                        required
                      >
                        <option value="DNI">DNI</option>
                        <option value="CE">Carnet de Extranjería (CE)</option>
                        <option value="PASAPORTE">Pasaporte</option>
                      </select>
                    </div>

                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Número de Documento *</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Ej. 45678912"
                        value={formData.numero_documento}
                        onChange={(e) => setFormData({ ...formData, numero_documento: e.target.value })}
                        required
                      />
                    </div>

                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Historia Clínica</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Ej. HC-2026-0089"
                        value={formData.historia_clinica}
                        onChange={(e) => setFormData({ ...formData, historia_clinica: e.target.value })}
                      />
                    </div>

                    <div className="col-12 col-md-6">
                      <label className="form-label fw-medium">Nombres *</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Ej. Juan Carlos"
                        value={formData.nombres}
                        onChange={(e) => setFormData({ ...formData, nombres: e.target.value })}
                        required
                      />
                    </div>

                    <div className="col-12 col-md-6">
                      <label className="form-label fw-medium">Apellidos *</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Ej. Pérez Ramos"
                        value={formData.apellidos}
                        onChange={(e) => setFormData({ ...formData, apellidos: e.target.value })}
                        required
                      />
                    </div>

                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Fecha de Nacimiento</label>
                      <input
                        type="date"
                        className="form-control"
                        value={formData.fecha_nacimiento}
                        onChange={(e) => setFormData({ ...formData, fecha_nacimiento: e.target.value })}
                      />
                    </div>

                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Sexo</label>
                      <select
                        className="form-select"
                        value={formData.sexo ?? ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          sexo: e.target.value
                            ? e.target.value as 'M' | 'F' | 'OTRO'
                            : null,
                        })}
                      >
                        <option value="">No especificado</option>
                        <option value="M">Masculino (M)</option>
                        <option value="F">Femenino (F)</option>
                        <option value="OTRO">Otro</option>
                      </select>
                    </div>

                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Teléfono</label>
                      <input
                        type="text"
                        className="form-control"
                        placeholder="Ej. 987654321"
                        value={formData.telefono}
                        onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                      />
                    </div>

                    <div className="col-12">
                      <label className="form-label fw-medium">Correo Electrónico</label>
                      <input
                        type="email"
                        className="form-control"
                        placeholder="paciente@correo.com"
                        value={formData.correo}
                        onChange={(e) => setFormData({ ...formData, correo: e.target.value })}
                      />
                    </div>
                  </div>

                  <div className="mt-3 p-3 bg-light rounded-3 text-muted small">
                    <FaCheck className="text-success me-1" /> El paciente no requiere usuario ni contraseña para el MVP.
                  </div>
                </div>
                <div className="modal-footer bg-light">
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => setShowCreateModal(false)}
                  >
                    Cancelar
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Guardar Paciente
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: EDITAR PACIENTE */}
      {showEditModal && selectedPatient && (
        <div className="modal fade show d-block modal-backdrop-custom" tabIndex={-1}>
          <div className="modal-dialog modal-dialog-centered modal-lg">
            <div className="modal-content shadow border-0">
              <div className="modal-header modal-header-mediflow text-white">
                <h5 className="modal-title d-flex align-items-center gap-2">
                  <FaEdit /> Editar Datos del Paciente
                </h5>
                <button
                  type="button"
                  className="btn-close btn-close-white"
                  onClick={() => setShowEditModal(false)}
                ></button>
              </div>
              <form onSubmit={handleEditSubmit}>
                <div className="modal-body p-4">
                  <div className="row g-3">
                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Tipo de Documento</label>
                      <select
                        className="form-select"
                        value={formData.tipo_documento}
                        onChange={(e) => setFormData({ ...formData, tipo_documento: e.target.value as any })}
                      >
                        <option value="DNI">DNI</option>
                        <option value="CE">CE</option>
                        <option value="PASAPORTE">PASAPORTE</option>
                      </select>
                    </div>

                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Número de Documento</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.numero_documento}
                        onChange={(e) => setFormData({ ...formData, numero_documento: e.target.value })}
                        required
                      />
                    </div>

                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Historia Clínica</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.historia_clinica}
                        onChange={(e) => setFormData({ ...formData, historia_clinica: e.target.value })}
                      />
                    </div>

                    <div className="col-12 col-md-6">
                      <label className="form-label fw-medium">Nombres</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.nombres}
                        onChange={(e) => setFormData({ ...formData, nombres: e.target.value })}
                        required
                      />
                    </div>

                    <div className="col-12 col-md-6">
                      <label className="form-label fw-medium">Apellidos</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.apellidos}
                        onChange={(e) => setFormData({ ...formData, apellidos: e.target.value })}
                        required
                      />
                    </div>

                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Fecha Nacimiento</label>
                      <input
                        type="date"
                        className="form-control"
                        value={formData.fecha_nacimiento}
                        onChange={(e) => setFormData({ ...formData, fecha_nacimiento: e.target.value })}
                      />
                    </div>

                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Sexo</label>
                      <select
                        className="form-select"
                        value={formData.sexo ?? ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          sexo: e.target.value
                            ? e.target.value as 'M' | 'F' | 'OTRO'
                            : null,
                        })}
                      >
                        <option value="">No especificado</option>
                        <option value="M">Masculino (M)</option>
                        <option value="F">Femenino (F)</option>
                        <option value="OTRO">Otro</option>
                      </select>
                    </div>

                    <div className="col-12 col-md-4">
                      <label className="form-label fw-medium">Teléfono</label>
                      <input
                        type="text"
                        className="form-control"
                        value={formData.telefono}
                        onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                      />
                    </div>

                    <div className="col-12">
                      <label className="form-label fw-medium">Correo Electrónico</label>
                      <input
                        type="email"
                        className="form-control"
                        value={formData.correo}
                        onChange={(e) => setFormData({ ...formData, correo: e.target.value })}
                      />
                    </div>
                  </div>
                </div>
                <div className="modal-footer bg-light">
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => setShowEditModal(false)}
                  >
                    Cancelar
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Actualizar Paciente
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: ÁRBOL / HISTORIAL DE DOCUMENTOS DEL PACIENTE (RF-08 & RF-09) */}
      {showDocsModal && selectedPatient && (
        <div className="modal fade show d-block modal-backdrop-custom" tabIndex={-1}>
          <div className="modal-dialog modal-dialog-centered modal-xl">
            <div className="modal-content shadow border-0">
              <div className="modal-header modal-header-mediflow">
                <h5 className="modal-title text-white d-flex align-items-center gap-2 mb-0">
                  <FaFolderOpen className="text-info" /> Historial Documental y Detección IA (RF-08 / RF-09)
                </h5>
                <button
                  type="button"
                  className="btn-close btn-close-white"
                  onClick={() => setShowDocsModal(false)}
                ></button>
              </div>

              <div className="modal-body p-4">
                {/* Resumen del Paciente */}
                <div className="card bg-light border-0 mb-4 p-3 rounded-3 shadow-sm">
                  <div className="row align-items-center">
                    <div className="col-12 col-md-8">
                      <h4 className="fw-bold mb-1 text-dark">
                        {selectedPatient.nombre_completo || `${selectedPatient.nombres} ${selectedPatient.apellidos}`}
                      </h4>
                      <div className="d-flex flex-wrap gap-3 text-muted small">
                        <span>
                          <strong>DNI:</strong> {selectedPatient.numero_documento}
                        </span>
                        <span>
                          <strong>Historia Clínica:</strong> {selectedPatient.historia_clinica || 'Sin asignar'}
                        </span>
                        <span>
                          <strong>Sexo / Nac.:</strong> {selectedPatient.sexo || 'No especificado'} ({selectedPatient.fecha_nacimiento || 'N/A'})
                        </span>
                      </div>
                    </div>
                    <div className="col-12 col-md-4 text-md-end mt-2 mt-md-0">
                      <span className="badge bg-primary fs-6 px-3 py-2">
                        {patientDocs ? patientDocs.total_documentos : 0} Documentos Asociados
                      </span>
                    </div>
                  </div>
                </div>

                {/* Formulario Elegante con Search Select para Asociar Documentos Sin Vincular */}
                {(() => {
                  const linkedIds = new Set((patientDocs?.documentos || []).map((d) => d.documento_id))
                  const unlinkedOnly = availableDocs.filter((d) => !linkedIds.has(d.documento_id))

                  return (
                    <form onSubmit={handleAssociateManualDoc} className="mb-4">
                      <div className="card border-0 bg-light p-3 rounded-3 shadow-sm">
                        <label className="form-label fw-bold text-dark small mb-2 d-flex align-items-center gap-2">
                          <FaLink className="text-primary" /> Vincular Nuevo Documento (Solo no asociados):
                        </label>
                        <div className="row g-2 align-items-center">
                          <div className="col-12 col-md-9">
                            <SearchableDocSelect
                              documents={unlinkedOnly}
                              selectedId={manualDocId}
                              onSelect={(docId) => setManualDocId(docId)}
                            />
                          </div>
                          <div className="col-12 col-md-3">
                            <button
                              type="submit"
                              className="btn btn-primary w-100 fw-semibold d-flex align-items-center justify-content-center gap-1"
                              disabled={!manualDocId.trim()}
                            >
                              <FaLink /> Vincular Documento
                            </button>
                          </div>
                        </div>
                      </div>
                    </form>
                  )
                })()}

                {/* Árbol de Documentos */}
                {loadingDocs ? (
                  <div className="text-center py-5">
                    <div className="spinner-border text-primary" role="status"></div>
                    <p className="mt-2 text-muted">Cargando expediente documental del paciente...</p>
                  </div>
                ) : patientDocs && patientDocs.documentos.length > 0 ? (
                  <div className="patient-docs-tree">
                    <div className="fw-bold text-dark mb-3 d-flex align-items-center gap-2">
                      <FaFileMedical className="text-primary" /> Documentos del Expediente
                    </div>
                    <div className="list-group">
                      {patientDocs.documentos.map((doc) => (
                        <div key={doc.id} className="list-group-item p-3 mb-2 rounded-3 border shadow-sm">
                          <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-2">
                            <div className="d-flex align-items-center gap-2">
                              <span className="badge bg-dark font-monospace">{doc.documento_id}</span>
                              <span className="fw-bold text-primary">{doc.tipo_documento || 'Documento Clínico'}</span>
                              <span className="badge bg-light text-dark border">{doc.tipo_archivo}</span>
                              {doc.nivel_prioridad === 'Urgente' ? (
                                <span className="badge bg-danger">Urgente</span>
                              ) : (
                                <span className="badge bg-secondary">Rutina</span>
                              )}
                            </div>
                            <div className="text-muted small mt-1 mt-md-0">
                              {doc.created_at ? new Date(doc.created_at).toLocaleString() : ''}
                            </div>
                          </div>

                          {/* RF-09: Datos extraídos por IA conservados */}
                          {doc.datos_extraidos_ia && (
                            <div className="p-3 bg-light rounded-3 mt-2 border-start border-3 border-primary small shadow-sm">
                              <div className="d-flex align-items-center gap-1 text-info fw-bold mb-1">
                                <FaRobot /> Datos Extraídos por IA (RF-09 Conservados):
                              </div>
                              <div className="row g-2">
                                <div className="col-12 col-md-4">
                                  <strong>Paciente IA:</strong> {doc.datos_extraidos_ia.nombre_detectado || 'N/D'} (
                                  {doc.datos_extraidos_ia.edad_detectada ? `${doc.datos_extraidos_ia.edad_detectada} años` : 'N/D'})
                                </div>
                                <div className="col-12 col-md-4">
                                  <strong>DNI/HC IA:</strong> {doc.datos_extraidos_ia.dni_hc_detectado || 'N/D'}
                                </div>
                                <div className="col-12 col-md-4">
                                  <strong>Médico Solicitante:</strong> {doc.datos_extraidos_ia.medico_nombre || 'N/D'}
                                </div>
                                {doc.datos_extraidos_ia.diagnostico && (
                                  <div className="col-12">
                                    <strong>Diagnóstico:</strong> {doc.datos_extraidos_ia.diagnostico}{' '}
                                    {doc.datos_extraidos_ia.cie10 && (
                                      <span className="badge bg-primary ms-1">CIE-10: {doc.datos_extraidos_ia.cie10}</span>
                                    )}
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-5 text-muted">
                    <FaFolderOpen size={48} className="mb-3 opacity-50" />
                    <h5>No hay documentos asociados aun</h5>
                    <p className="small">
                      Puede asociar un documento indicando su ID arriba o hacer clic en Ingestar para subir uno nuevo.
                    </p>
                  </div>
                )}
              </div>

              <div className="modal-footer bg-light">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowDocsModal(false)}
                >
                  Cerrar Expediente
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
