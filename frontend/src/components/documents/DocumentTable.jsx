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
        <thead className="table-light">
          <tr>
            <th>ID</th>
            <th>Nombre Archivo</th>
            <th>Tipo Documento</th>
            <th>Paciente</th>
            <th>Fecha</th>
            <th>Prioridad</th>
            <th>Confianza</th>
            <th>Estado</th>
            <th>Destino</th>
            <th className="text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => {
            const conf = formatConfidence(doc.clasificacion?.score_confianza);
            const requiereAuditoria = doc.estado === "AUDITORIA" || doc.decision_enrutamiento?.requiere_auditoria;

            return (
              <tr key={doc.documento_id}>
                <td className="fw-bold text-primary">{doc.documento_id}</td>
                <td className="fw-medium text-dark">{doc.nombre_archivo}</td>
                <td>{doc.clasificacion?.tipo_documento || "Desconocido"}</td>
                <td>{doc.datos_extraidos?.paciente?.nombre || "-"}</td>
                <td className="small text-muted">{formatDateShort(doc.fecha_creacion)}</td>
                <td>
                  <PriorityBadge priority={doc.clasificacion?.prioridad} />
                </td>
                <td>
                  <span className={`badge ${conf.badgeClass}`}>{conf.formattedText}</span>
                </td>
                <td>
                  <DocumentStatusBadge estado={doc.estado} />
                </td>
                <td className="fw-medium small">{doc.decision_enrutamiento?.destino || "-"}</td>
                <td className="text-center">
                  <div className="btn-group btn-group-sm">
                    <Link
                      to={`/documentos/${doc.documento_id}`}
                      className="btn btn-outline-primary"
                      title="Ver resultado de triaje"
                    >
                      <FaEye className="me-1" /> Ver
                    </Link>
                    {requiereAuditoria && (
                      <Link
                        to={`/auditoria/${doc.documento_id}`}
                        className="btn btn-warning text-dark"
                        title="Ir a Auditoría Humana"
                      >
                        <FaUserCheck className="me-1" /> Revisar
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
