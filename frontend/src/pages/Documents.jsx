import React, { useState } from "react";
import { Link } from "react-router-dom";
import DocumentTable from "../components/documents/DocumentTable";
import Loading from "../components/common/Loading";
import EmptyState from "../components/common/EmptyState";
import ErrorMessage from "../components/common/ErrorMessage";
import { useDocuments } from "../hooks/useDocuments";
import { FaFileUpload, FaSearch, FaFilter } from "react-icons/fa";

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
    <div className="documents-page">
      <div className="d-flex flex-wrap align-items-center justify-content-between mb-4">
        <div>
          <h3 className="fw-bold text-dark mb-1">Historial de Documentos</h3>
          <p className="text-muted small mb-0">Listado general de documentos procesados y registrados en MediFlow</p>
        </div>
        <Link to="/documentos/nuevo" className="btn btn-primary fw-bold px-3 py-2 shadow-sm">
          <FaFileUpload className="me-2" /> Nuevo Documento
        </Link>
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
