import { useState } from "react";
import { Link } from "react-router-dom";
import PriorityBadge from "../triage/PriorityBadge";
import DocumentStatusBadge from "./DocumentStatusBadge";
import { formatConfidence } from "../../utils/formatConfidence";
import { formatDateShort } from "../../utils/formatDate";
import { FaEye, FaUserCheck, FaChevronLeft, FaChevronRight } from "react-icons/fa";
import type { ClinicalDocument } from "../../types/documents";
import { normalizeClinicalDocumentType } from "../../constants/clinicalDocumentTypes";

export interface DocumentTableProps {
  documents?: ClinicalDocument[];
  pageSize?: number;
}

const DocumentTable = ({ documents = [], pageSize: initialPageSize = 10 }: DocumentTableProps) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);

  if (!documents.length) {
    return <div className="text-center py-4 text-muted">No se encontraron documentos en esta vista.</div>;
  }

  const totalPages = Math.max(1, Math.ceil(documents.length / pageSize));
  const safeCurrentPage = Math.min(currentPage, totalPages);

  const startIndex = (safeCurrentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, documents.length);
  const paginatedDocuments = documents.slice(startIndex, endIndex);

  return (
    <div>
      <div className="w-full">
        <table className="table table-hover clinical-data-table mb-0 w-full align-middle">
          <caption className="visually-hidden">Listado de documentos clínicos procesados</caption>
          <thead className="bg-light">
            <tr className="text-secondary small text-uppercase fw-bold text-xs">
              <th className="ps-3 sm:ps-4 whitespace-nowrap">ID Documento</th>
              <th className="whitespace-nowrap">Nombre Archivo</th>
              <th className="whitespace-nowrap">Tipo Documento</th>
              <th className="whitespace-nowrap">Paciente</th>
              <th className="whitespace-nowrap">Fecha</th>
              <th className="whitespace-nowrap">Prioridad</th>
              <th className="whitespace-nowrap">Confianza</th>
              <th className="whitespace-nowrap">Estado</th>
              <th className="whitespace-nowrap">Destino</th>
              <th className="text-end pe-3 sm:pe-4 whitespace-nowrap">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {paginatedDocuments.map((doc) => {
              const conf = formatConfidence(doc.clasificacion?.score_confianza);
              const requiereAuditoria = doc.estado === "AUDITORIA" || doc.decision_enrutamiento?.requiere_auditoria;
              const tipoDoc = normalizeClinicalDocumentType(doc.clasificacion?.tipo_documento);

              return (
                <tr key={doc.documento_id}>
                  <td className="ps-3 sm:ps-4 whitespace-nowrap">
                    <span className="badge bg-light text-primary border font-monospace px-2 py-1 rounded-md text-xs fw-bold">
                      {doc.documento_id}
                    </span>
                  </td>
                  <td>
                    <div className="fw-semibold text-dark text-xs leading-snug break-all" title={doc.nombre_archivo}>
                      {doc.nombre_archivo}
                    </div>
                  </td>
                  <td>
                    <span className="text-xs text-dark fw-medium leading-snug block whitespace-normal" title={tipoDoc}>
                      {tipoDoc}
                    </span>
                  </td>
                  <td>
                    <span className="text-xs fw-semibold text-dark leading-snug block whitespace-normal" title={doc.datos_extraidos?.paciente?.nombre || "Paciente Clínico"}>
                      {doc.datos_extraidos?.paciente?.nombre || "Paciente Clínico"}
                    </span>
                  </td>
                  <td className="text-xs text-muted whitespace-nowrap">{formatDateShort(doc.fecha_creacion)}</td>
                  <td className="whitespace-nowrap">
                    <PriorityBadge priority={doc.clasificacion?.prioridad} />
                  </td>
                  <td className="whitespace-nowrap">
                    <span className={`badge ${conf.badgeClass} rounded-pill px-2.5 py-0.5 fw-bold text-xs`}>{conf.formattedText}</span>
                  </td>
                  <td className="whitespace-nowrap">
                    <DocumentStatusBadge estado={doc.estado} />
                  </td>
                  <td>
                    <span className="fw-medium text-xs text-muted leading-snug block whitespace-normal" title={doc.decision_enrutamiento?.destino || "-"}>
                      {doc.decision_enrutamiento?.destino || "-"}
                    </span>
                  </td>
                  <td className="text-end pe-3 sm:pe-4 whitespace-nowrap">
                    <div className="inline-flex items-center justify-end gap-1.5">
                      <Link
                        to={`/documentos/${doc.documento_id}`}
                        className="btn btn-sm btn-outline-primary px-2.5 py-1 text-xs d-inline-flex align-items-center gap-1 shadow-2xs no-underline"
                        title="Ver detalle del documento"
                      >
                        <FaEye size={11} /> <span>Ver</span>
                      </Link>
                      {requiereAuditoria && (
                        <Link
                          to={`/auditoria/${doc.documento_id}`}
                          className="btn btn-sm btn-warning text-dark px-2.5 py-1 text-xs d-inline-flex align-items-center gap-1 shadow-2xs no-underline"
                          title="Ir a Auditoría Humana"
                        >
                          <FaUserCheck size={11} /> <span>Revisar</span>
                        </Link>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-between px-3 py-3 sm:px-4 sm:py-3 border-top bg-light gap-3">
        <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 sm:gap-3 text-center sm:text-left">
          <span className="small text-muted" data-testid="pagination-info">
            Mostrando <strong className="text-dark">{startIndex + 1}</strong> a <strong className="text-dark">{endIndex}</strong> de <strong className="text-dark">{documents.length}</strong> documentos
          </span>
          <div className="d-flex align-items-center">
            <label htmlFor="pageSizeSelect" className="small text-muted me-2 mb-0">Por página:</label>
            <select
              id="pageSizeSelect"
              className="form-select form-select-sm"
              style={{ width: "75px" }}
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              data-testid="page-size-select"
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
            </select>
          </div>
        </div>

        <div className="flex items-center gap-1 flex-wrap justify-center">
          <button
            type="button"
            className="btn btn-sm btn-outline-secondary d-flex align-items-center gap-1 px-3 py-1.5"
            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            disabled={safeCurrentPage === 1}
            data-testid="pagination-prev"
          >
            <FaChevronLeft className="small" /> Anterior
          </button>

          {Array.from({ length: totalPages }, (_, i) => i + 1)
            .filter((page) => {
              return page === 1 || page === totalPages || Math.abs(page - safeCurrentPage) <= 1;
            })
            .map((page, index, arr) => {
              const prev = arr[index - 1];
              const showEllipsis = prev && page - prev > 1;
              return (
                <span key={page} className="d-flex align-items-center">
                  {showEllipsis && <span className="px-1 text-muted">...</span>}
                  <button
                    type="button"
                    className={`btn btn-sm px-3 py-1.5 ${safeCurrentPage === page ? "btn-primary fw-bold" : "btn-outline-light text-dark border"}`}
                    onClick={() => setCurrentPage(page)}
                    data-testid={`page-btn-${page}`}
                  >
                    {page}
                  </button>
                </span>
              );
            })}

          <button
            type="button"
            className="btn btn-sm btn-outline-secondary d-flex align-items-center gap-1 px-3 py-1.5"
            onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
            disabled={safeCurrentPage === totalPages}
            data-testid="pagination-next"
          >
            Siguiente <FaChevronRight className="small" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentTable;
