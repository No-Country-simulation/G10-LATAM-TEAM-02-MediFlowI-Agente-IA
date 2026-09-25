import React from "react";
import { Link } from "react-router-dom";
import PriorityBadge from "../triage/PriorityBadge";
import DocumentStatusBadge from "./DocumentStatusBadge";
import { formatConfidence } from "../../utils/formatConfidence";
import { formatDateShort } from "../../utils/formatDate";
import { FaEye, FaUserCheck } from "react-icons/fa";

const DocumentTable = ({ documents = [], showAuditAction = false }) => {
  if (!documents.length) {
    return <div className="text-center py-4 text-muted">No se encontraron documentos en esta vista.</div>;
  }

  return (
    <div className="table-responsive">
      <table className="table table-hover align-middle mb-0">
        <thead className="bg-light">
          <tr className="text-secondary small text-uppercase fw-bold">
            <th className="ps-4">ID Documento</th>
            <th>Nombre Archivo</th>
            <th>Tipo Documento</th>
            <th>Paciente</th>
            <th>Fecha</th>
            <th>Prioridad</th>
            <th>Confianza</th>
            <th>Estado</th>
            <th>Destino Asignado</th>
            <th className="text-end pe-4">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => {
            const conf = formatConfidence(doc.clasificacion?.score_confianza);
            const requiereAuditoria = doc.estado === "AUDITORIA" || doc.decision_enrutamiento?.requiere_auditoria;
            const tipoDoc = (!doc.clasificacion?.tipo_documento || doc.clasificacion?.tipo_documento === "Error" || doc.clasificacion?.tipo_documento === "Desconocido")
              ? "Documento Clínico"
              : doc.clasificacion.tipo_documento;

            return (
              <tr key={doc.documento_id}>
                <td className="ps-4">
                  <span className="badge bg-light text-primary border font-monospace px-2.5 py-1.5 rounded-2 fs-7 fw-bold text-nowrap">
                    {doc.documento_id}
                  </span>
                </td>
                <td className="fw-semibold text-dark text-nowrap me-2" style={{ maxWidth: '220px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {doc.nombre_archivo}
                </td>
                <td>
                  <span className="small text-dark fw-medium">{tipoDoc}</span>
                </td>
                <td className="text-nowrap">
                  <span className="small fw-semibold text-dark">{doc.datos_extraidos?.paciente?.nombre || "Paciente Clínico"}</span>
                </td>
                <td className="small text-muted text-nowrap">{formatDateShort(doc.fecha_creacion)}</td>
                <td>
                  <PriorityBadge priority={doc.clasificacion?.prioridad} />
                </td>
                <td>
                  <span className={`badge ${conf.badgeClass} rounded-pill px-2.5 py-1 fw-bold`}>{conf.formattedText}</span>
                </td>
                <td>
                  <DocumentStatusBadge estado={doc.estado} />
                </td>
                <td className="fw-medium small text-muted text-nowrap">{doc.decision_enrutamiento?.destino || "-"}</td>
                <td className="text-end pe-4">
                  <div className="d-flex align-items-center justify-content-end gap-1.5">
                    <Link
                      to={`/documentos/${doc.documento_id}`}
                      className="btn btn-sm btn-outline-primary rounded-pill fw-semibold px-3 d-flex align-items-center gap-1"
                      title="Ver detalle del documento"
                    >
                      <FaEye /> Ver
                    </Link>
                    {requiereAuditoria && (
                      <Link
                        to={`/auditoria/${doc.documento_id}`}
                        className="btn btn-sm btn-warning text-dark rounded-pill fw-bold px-3 d-flex align-items-center gap-1 shadow-sm"
                        title="Ir a Auditoría Humana"
                      >
                        <FaUserCheck /> Revisar
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
  );
};

export default DocumentTable;
