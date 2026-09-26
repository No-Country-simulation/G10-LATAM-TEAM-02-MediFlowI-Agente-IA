import { useState } from "react";
import { Link } from "react-router-dom";
import DocumentTable from "../components/documents/DocumentTable";
import Loading from "../components/common/Loading";
import EmptyState from "../components/common/EmptyState";
import ErrorMessage from "../components/common/ErrorMessage";
import PageHeader from "../components/common/PageHeader";
import StatsCard from "../components/dashboard/StatsCard";
import { useDocuments } from "../hooks/useDocuments";
import { CLINICAL_DOCUMENT_TYPES, normalizeClinicalDocumentType } from "../constants/clinicalDocumentTypes";
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
    if (estadoFilter && doc.estado?.toUpperCase() !== estadoFilter.toUpperCase()) {
      return false;
    }
    if (prioridadFilter && doc.clasificacion?.prioridad?.toUpperCase() !== prioridadFilter.toUpperCase()) {
      return false;
    }
    if (tipoFilter && normalizeClinicalDocumentType(doc.clasificacion?.tipo_documento) !== tipoFilter) {
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
    <div className="clinical-page documents-page">
      <PageHeader
        eyebrow="Trazabilidad"
        title="Documentos clínicos"
        description="Consulta, filtra y revisa el historial de documentos procesados por MediFlow."
        icon={<FaFileMedical />}
        actions={(
          <>
          <button
            type="button"
            className="btn btn-outline-secondary"
            onClick={refetch}
            aria-label="Actualizar lista de documentos"
          >
            <FaSync className="me-2" /> Actualizar
          </button>
          <Link to="/documentos/nuevo" className="btn btn-primary px-3">
            <FaFileUpload className="me-2" /> Cargar documento
          </Link>
          </>
        )}
      />

      {/* KPI Cards */}
      <div className="row g-3 mb-4">
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard title="Total" value={documents.length} icon={<FaFileMedical />} subtitle="Documentos registrados" />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard title="Procesados" value={documents.filter((d) => d.estado === 'PROCESADO').length} icon={<FaCheckCircle />} variant="success" subtitle="Sin revisión pendiente" />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard title="En auditoría" value={documents.filter((d) => d.estado === 'AUDITORIA' || d.decision_enrutamiento?.requiere_auditoria).length} icon={<FaUserCheck />} variant="warning" subtitle="Requieren decisión humana" />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard title="Urgentes" value={documents.filter((d) => d.clasificacion?.prioridad === 'URGENTE').length} icon={<FaExclamationTriangle />} variant="danger" subtitle="Atención prioritaria" />
        </div>
      </div>

      {/* Filter panel */}
      <div className="clinical-filter-bar">
          <div className="row g-2 align-items-center">
            <div className="col-12 col-md-4">
              <label className="clinical-filter-label" htmlFor="document-search">Buscar</label>
              <div className="input-group">
                <span className="input-group-text bg-white border-end-0 text-muted">
                  <FaSearch />
                </span>
                <input
                  type="text"
                  id="document-search"
                  className="form-control border-start-0 ps-0"
                  placeholder="Buscar por paciente, DNI, ID o archivo..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {/* Filter Estado */}
            <div className="col-6 col-md-2">
              <label className="clinical-filter-label" htmlFor="status-filter">Estado</label>
              <select
                id="status-filter"
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
              <label className="clinical-filter-label" htmlFor="priority-filter">Prioridad</label>
              <select
                id="priority-filter"
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
              <label className="clinical-filter-label" htmlFor="type-filter">Tipo clínico</label>
              <select
                id="type-filter"
                className="form-control"
                aria-label="Filtrar por tipo clínico"
                value={tipoFilter}
                onChange={(e) => setTipoFilter(e.target.value)}
              >
                <option value="">Todos los tipos clínicos</option>
                {CLINICAL_DOCUMENT_TYPES.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            {/* Clear button */}
            <div className="col-6 col-md-2 text-end align-self-end">
              <button className="btn btn-outline-secondary w-100 fw-semibold" onClick={handleClearFilters}>
                <FaFilter className="me-1" /> Limpiar
              </button>
            </div>
          </div>
      </div>

      {/* Main content table */}
      <div className="clinical-surface">
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
