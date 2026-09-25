import React, { useState } from "react";
import { Link } from "react-router-dom";
import DocumentTable from "../components/documents/DocumentTable";
import Loading from "../components/common/Loading";
import EmptyState from "../components/common/EmptyState";
import ErrorMessage from "../components/common/ErrorMessage";
import { useDocuments } from "../hooks/useDocuments";
import {
  FaFileUpload,
  FaSearch,
  FaFilter,
  FaFileMedical,
  FaCheckCircle,
  FaUserCheck,
  FaExclamationTriangle,
  FaSync,
} from "react-icons/fa";

const Documents = () => {
  const { documents, loading, error, refetch } = useDocuments();

  const [estadoFilter, setEstadoFilter] = useState("");
  const [prioridadFilter, setPrioridadFilter] = useState("");
  const [tipoFilter, setTipoFilter] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  const filteredDocuments = documents.filter((doc) => {
    if (estadoFilter && doc.estado.toUpperCase() !== estadoFilter.toUpperCase()) {
      return false;
    }
    if (prioridadFilter && doc.clasificacion?.prioridad?.toUpperCase() !== prioridadFilter.toUpperCase()) {
      return false;
    }
    if (tipoFilter && !doc.clasificacion?.tipo_documento?.toLowerCase().includes(tipoFilter.toLowerCase())) {
      return false;
    }
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      const pNombre = (doc.datos_extraidos?.paciente?.nombre || "").toLowerCase();
      const pDni = (doc.datos_extraidos?.paciente?.dni || "").toLowerCase();
      const docId = (doc.documento_id || "").toLowerCase();
      const docName = (doc.nombre_archivo || "").toLowerCase();
      return pNombre.includes(term) || pDni.includes(term) || docId.includes(term) || docName.includes(term);
    }
    return true;
  });

  const handleClearFilters = () => {
    setEstadoFilter("");
    setPrioridadFilter("");
    setTipoFilter("");
    setSearchTerm("");
  };

  return (
    <div className="container-fluid py-4 px-4">
      {/* Header */}
      <div className="d-flex flex-wrap align-items-center justify-content-between mb-4 gap-2">
        <div>
          <h3 className="fw-bold text-dark mb-1 d-flex align-items-center gap-2">
            <FaFileMedical className="text-primary" /> Historial de Documentos
          </h3>
          <p className="text-muted small mb-0">
            Listado general y trazabilidad de documentos clínicos procesados en MediFlow (PostgreSQL)
          </p>
        </div>
        <div className="d-flex align-items-center gap-2">
          <button
            type="button"
            className="btn btn-outline-secondary btn-sm rounded-circle p-2 d-flex align-items-center justify-content-center"
            onClick={refetch}
            title="Refrescar lista"
            style={{ width: "36px", height: "36px" }}
          >
            <FaSync />
          </button>
          <Link to="/documentos/nuevo" className="btn btn-primary fw-bold px-3.5 py-2 rounded-pill shadow-sm d-flex align-items-center gap-2">
            <FaFileUpload /> Nuevo Documento
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="row g-3 mb-4">
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">Total Registros</span>
                <h3 className="fw-bold text-dark mb-0 mt-1">{documents.length}</h3>
              </div>
              <div className="bg-primary bg-opacity-10 text-primary p-3 rounded-circle">
                <FaFileMedical className="fs-4" />
              </div>
            </div>
          </div>
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">Procesados</span>
                <h3 className="fw-bold text-success mb-0 mt-1">
                  {documents.filter((d) => d.estado === 'PROCESADO').length}
                </h3>
              </div>
              <div className="bg-success bg-opacity-10 text-success p-3 rounded-circle">
                <FaCheckCircle className="fs-4" />
              </div>
            </div>
          </div>
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">En Auditoría HITL</span>
                <h3 className="fw-bold text-warning mb-0 mt-1">
                  {documents.filter((d) => d.estado === 'AUDITORIA' || d.decision_enrutamiento?.requiere_auditoria).length}
                </h3>
              </div>
              <div className="bg-warning bg-opacity-10 text-warning p-3 rounded-circle">
                <FaUserCheck className="fs-4" />
              </div>
            </div>
          </div>
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <div className="card border-0 shadow-sm rounded-4 p-3 bg-white">
            <div className="d-flex align-items-center justify-content-between">
              <div>
                <span className="text-muted small fw-semibold">Casos Urgentes</span>
                <h3 className="fw-bold text-danger mb-0 mt-1">
                  {documents.filter((d) => d.clasificacion?.prioridad === 'URGENTE').length}
                </h3>
              </div>
              <div className="bg-danger bg-opacity-10 text-danger p-3 rounded-circle">
                <FaExclamationTriangle className="fs-4" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter panel */}
      <div className="card border-0 shadow-sm mb-4">
        <div className="card-body p-3">
          <div className="row g-2 align-items-center">
            {/* Search Input */}
            <div className="col-12 col-md-4">
              <div className="input-group">
                <span className="input-group-text bg-white border-end-0 text-muted">
                  <FaSearch />
                </span>
                <input
                  type="text"
                  className="form-control border-start-0 ps-0"
                  placeholder="Buscar por paciente, DNI, ID o archivo..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {/* Filter Estado */}
            <div className="col-6 col-md-2">
              <select
                className="form-select"
                value={estadoFilter}
                onChange={(e) => setEstadoFilter(e.target.value)}
              >
                <option value="">Todos los Estados</option>
                <option value="RECIBIDO">RECIBIDO</option>
                <option value="PROCESANDO">PROCESANDO</option>
                <option value="PROCESADO">PROCESADO</option>
                <option value="AUDITORIA">AUDITORIA</option>
                <option value="RECHAZADO">RECHAZADO</option>
                <option value="ERROR">ERROR</option>
              </select>
            </div>

            {/* Filter Prioridad */}
            <div className="col-6 col-md-2">
              <select
                className="form-select"
                value={prioridadFilter}
                onChange={(e) => setPrioridadFilter(e.target.value)}
              >
                <option value="">Todas las Prioridades</option>
                <option value="NORMAL">NORMAL</option>
                <option value="PRIORITARIO">PRIORITARIO</option>
                <option value="URGENTE">URGENTE</option>
              </select>
            </div>

            {/* Filter Tipo */}
            <div className="col-6 col-md-2">
              <input
                type="text"
                className="form-control"
                placeholder="Tipo (ej. Receta)"
                value={tipoFilter}
                onChange={(e) => setTipoFilter(e.target.value)}
              />
            </div>

            {/* Clear button */}
            <div className="col-6 col-md-2 text-end">
              <button className="btn btn-outline-secondary w-100 fw-semibold" onClick={handleClearFilters}>
                <FaFilter className="me-1" /> Limpiar
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content table */}
      <div className="card border-0 shadow-sm rounded-3">
        <div className="card-body p-0">
          {loading ? (
            <Loading message="Cargando historial de documentos..." />
          ) : error ? (
            <ErrorMessage title="Error al cargar documentos" message={error} onRetry={refetch} />
          ) : filteredDocuments.length === 0 ? (
            <EmptyState
              title="No se encontraron documentos"
              message="Pruebe ajustando los filtros de búsqueda o cargando un nuevo documento."
              actionLabel="Limpiar Filtros"
              onAction={handleClearFilters}
            />
          ) : (
            <DocumentTable documents={filteredDocuments} />
          )}
        </div>
      </div>
    </div>
  );
};

export default Documents;
