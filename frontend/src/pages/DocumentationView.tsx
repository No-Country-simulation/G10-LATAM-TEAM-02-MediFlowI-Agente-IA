import { useState } from 'react'
import { FaUserShield, FaStethoscope, FaClipboardCheck, FaSlidersH, FaCheckCircle, FaTimesCircle, FaBookOpen } from 'react-icons/fa'
import '../App.css'

export default function DocumentationView() {
  const [activeTab, setActiveTab] = useState<'roles' | 'triage' | 'storage'>('roles')

  return (
    <div className="container-fluid py-4 px-4">
      {/* Header de Documentación */}
      <div className="d-flex align-items-center justify-content-between mb-4 border-bottom pb-3">
        <div>
          <h3 className="fw-bold text-dark mb-1 d-flex align-items-center">
            <FaBookOpen className="text-primary me-2" /> Documentación y Guía del Sistema MediFlow
          </h3>
          <p className="text-muted small mb-0">
            Manual operativo, especificaciones de roles (RBAC) y guías de uso del Agente IA de Triaje Clínico
          </p>
        </div>
        <span className="badge bg-primary bg-opacity-10 text-primary px-3 py-2 rounded-pill fw-semibold fs-7">
          Versión 2.0 — MediFlow Docs
        </span>
      </div>

      {/* Pestañas de Navegación en Documentación */}
      <ul className="nav nav-tabs mb-4 border-bottom-0">
        <li className="nav-item">
          <button
            className={`nav-link fw-bold px-4 py-2.5 rounded-top-3 ${activeTab === 'roles' ? 'active bg-primary text-white' : 'text-secondary bg-light me-2'}`}
            onClick={() => setActiveTab('roles')}
          >
            <FaUserShield className="me-2" /> 1. Usuarios y Roles (RBAC)
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link fw-bold px-4 py-2.5 rounded-top-3 ${activeTab === 'triage' ? 'active bg-primary text-white' : 'text-secondary bg-light me-2'}`}
            onClick={() => setActiveTab('triage')}
          >
            <FaStethoscope className="me-2" /> 2. Flujo de Triaje IA & HITL
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link fw-bold px-4 py-2.5 rounded-top-3 ${activeTab === 'storage' ? 'active bg-primary text-white' : 'text-secondary bg-light'}`}
            onClick={() => setActiveTab('storage')}
          >
            <FaSlidersH className="me-2" /> 3. Almacenamiento Local vs OCI
          </button>
        </li>
      </ul>

      {/* SECCIÓN 1: USUARIOS Y ROLES (RBAC) */}
      {activeTab === 'roles' && (
        <div className="row g-4">
          <div className="col-12">
            <div className="card border-0 shadow-sm rounded-4 p-4 mb-4 bg-white">
              <h4 className="fw-bold text-dark mb-3 d-flex align-items-center">
                <FaUserShield className="text-primary me-2" /> Control de Acceso Basado en Roles (RBAC — RF-04 & RF-05)
              </h4>
              <p className="text-muted leading-relaxed">
                El sistema MediFlow implementa una política estricta de seguridad y control de acceso por roles. Cada trabajador de la clínica accede únicamente a los módulos pertinentes a su responsabilidad médica u operativa.
              </p>

              {/* GRID DE ROLES */}
              <div className="row g-3 mt-2 mb-4">
                {/* 1. ADMINISTRADOR */}
                <div className="col-12 col-md-6 col-xl-3">
                  <div className="card h-100 border border-primary bg-primary bg-opacity-10 rounded-4 p-3">
                    <div className="d-flex align-items-center justify-content-between mb-2">
                      <span className="badge bg-primary text-white px-3 py-1 rounded-pill">ADMINISTRADOR</span>
                      <FaUserShield className="text-primary fs-4" />
                    </div>
                    <h6 className="fw-bold text-dark mb-2">Acceso Total del Sistema</h6>
                    <ul className="small text-secondary ps-3 mb-0">
                      <li><strong>Gestión de Usuarios</strong>: Crear, editar, activar/desactivar y cambiar roles.</li>
                      <li><strong>Configuración</strong>: Control manual de almacenamiento Local vs OCI.</li>
                      <li><strong>Triaje & Ingesta</strong>: Procesar y clasificar documentos clínicos.</li>
                      <li><strong>Auditoría HITL</strong>: Resolver casos ambiguos y auditar decisiones.</li>
                    </ul>
                  </div>
                </div>

                {/* 2. OPERADOR */}
                <div className="col-12 col-md-6 col-xl-3">
                  <div className="card h-100 border border-success bg-success bg-opacity-10 rounded-4 p-3">
                    <div className="d-flex align-items-center justify-content-between mb-2">
                      <span className="badge bg-success text-white px-3 py-1 rounded-pill">OPERADOR</span>
                      <FaStethoscope className="text-success fs-4" />
                    </div>
                    <h6 className="fw-bold text-dark mb-2">Carga y Procesamiento</h6>
                    <ul className="small text-secondary ps-3 mb-0">
                      <li><strong>Ingesta Médica</strong>: Cargar informes en PDF, recetas e imágenes clínicas.</li>
                      <li><strong>Ejecución IA</strong>: Obtener clasificación automática y diagnóstico inicial.</li>
                      <li><strong>Consulta de Historial</strong>: Ver documentos procesados por el operador.</li>
                      <li><em>Restricción</em>: No puede modificar usuarios ni configuraciones del sistema.</li>
                    </ul>
                  </div>
                </div>

                {/* 3. AUDITOR */}
                <div className="col-12 col-md-6 col-xl-3">
                  <div className="card h-100 border border-warning bg-warning bg-opacity-10 rounded-4 p-3">
                    <div className="d-flex align-items-center justify-content-between mb-2">
                      <span className="badge bg-warning text-dark px-3 py-1 rounded-pill">AUDITOR</span>
                      <FaClipboardCheck className="text-warning fs-4" />
                    </div>
                    <h6 className="fw-bold text-dark mb-2">Revisión Clínica HITL</h6>
                    <ul className="small text-secondary ps-3 mb-0">
                      <li><strong>Human-in-the-Loop</strong>: Auditar casos etiquetados como ambiguos.</li>
                      <li><strong>Acciones Médicas</strong>: Aprobar, Reclasificar o Rechazar decisiones IA.</li>
                      <li><strong>Trazabilidad</strong>: Registrar comentarios médicos de auditoría.</li>
                      <li><em>Restricción</em>: Sin permisos de administración de cuentas ni almacenamiento.</li>
                    </ul>
                  </div>
                </div>

                {/* 4. SUPERVISOR */}
                <div className="col-12 col-md-6 col-xl-3">
                  <div className="card h-100 border border-info bg-info bg-opacity-10 rounded-4 p-3">
                    <div className="d-flex align-items-center justify-content-between mb-2">
                      <span className="badge bg-info text-white px-3 py-1 rounded-pill">SUPERVISOR</span>
                      <FaSlidersH className="text-info fs-4" />
                    </div>
                    <h6 className="fw-bold text-dark mb-2">Consulta & KPIs (Read-Only)</h6>
                    <ul className="small text-secondary ps-3 mb-0">
                      <li><strong>Dashboard Clínico</strong>: Visualizar métricas y tiempos de atención.</li>
                      <li><strong>Monitoreo de Auditorías</strong>: Consultar resoluciones de la comisión médica.</li>
                      <li><strong>Modo Lectura</strong>: Acceso total a consulta sin permisos de edición.</li>
                      <li><em>Restricción</em>: No puede alterar estados de triaje ni mutar datos.</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* MATRIZ DE PERMISOS POR ROL */}
              <h5 className="fw-bold text-dark mb-3">Matriz Resumen de Permisos (RBAC Matrix)</h5>
              <div className="table-responsive rounded-3 border">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Funcionalidad / Módulo</th>
                      <th className="text-center">ADMINISTRADOR</th>
                      <th className="text-center">OPERADOR</th>
                      <th className="text-center">AUDITOR</th>
                      <th className="text-center">SUPERVISOR</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><strong>Dashboard & KPIs Clínicos</strong></td>
                      <td className="text-center"><FaCheckCircle className="text-success" /></td>
                      <td className="text-center"><FaCheckCircle className="text-success" /></td>
                      <td className="text-center"><FaCheckCircle className="text-success" /></td>
                      <td className="text-center"><span className="badge bg-info text-white">Consulta</span></td>
                    </tr>
                    <tr>
                      <td><strong>Ingesta & Clasificación IA</strong></td>
                      <td className="text-center"><FaCheckCircle className="text-success" /></td>
                      <td className="text-center"><FaCheckCircle className="text-success" /></td>
                      <td className="text-center"><FaTimesCircle className="text-muted opacity-50" /></td>
                      <td className="text-center"><FaTimesCircle className="text-muted opacity-50" /></td>
                    </tr>
                    <tr>
                      <td><strong>Auditoría HITL (Aprobar/Reclasificar)</strong></td>
                      <td className="text-center"><FaCheckCircle className="text-success" /></td>
                      <td className="text-center"><FaTimesCircle className="text-muted opacity-50" /></td>
                      <td className="text-center"><FaCheckCircle className="text-success" /></td>
                      <td className="text-center"><span className="badge bg-info text-white">Consulta</span></td>
                    </tr>
                    <tr>
                      <td><strong>Gestión de Usuarios & Roles</strong></td>
                      <td className="text-center"><FaCheckCircle className="text-success" /></td>
                      <td className="text-center"><FaTimesCircle className="text-muted opacity-50" /></td>
                      <td className="text-center"><FaTimesCircle className="text-muted opacity-50" /></td>
                      <td className="text-center"><FaTimesCircle className="text-muted opacity-50" /></td>
                    </tr>
                    <tr>
                      <td><strong>Configuración Almacenamiento (Local/OCI)</strong></td>
                      <td className="text-center"><FaCheckCircle className="text-success" /></td>
                      <td className="text-center"><FaTimesCircle className="text-muted opacity-50" /></td>
                      <td className="text-center"><FaTimesCircle className="text-muted opacity-50" /></td>
                      <td className="text-center"><FaTimesCircle className="text-muted opacity-50" /></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SECCIÓN 2: FLUJO DE TRIAJE IA */}
      {activeTab === 'triage' && (
        <div className="card border-0 shadow-sm rounded-4 p-4 bg-white">
          <h4 className="fw-bold text-dark mb-3">Flujo del Agente Autónomo (LangGraph + Gemini)</h4>
          <p className="text-muted">
            El agente procesa cada documento clínico a través de 5 nodos secuenciales: <strong>Ingesta</strong> ➔ <strong>Extracción (OCR/NLP)</strong> ➔ <strong>Clasificación Especialidad</strong> ➔ <strong>Evaluación de Confianza</strong> ➔ <strong>Enrutamiento o Auditoría HITL</strong>.
          </p>
        </div>
      )}

      {/* SECCIÓN 3: ALMACENAMIENTO */}
      {activeTab === 'storage' && (
        <div className="card border-0 shadow-sm rounded-4 p-4 bg-white">
          <h4 className="fw-bold text-dark mb-3">Regla de Almacenamiento de Archivos (LOCAL / OCI)</h4>
          <p className="text-muted">
            PostgreSQL (`mediflow_dev`) actúa como Fuente Única de Verdad para metadatos y auditoría. El almacenamiento de binarios (PDFs/Imágenes) se configura manualmente en la pestaña de Configuración.
          </p>
        </div>
      )}
    </div>
  )
}
