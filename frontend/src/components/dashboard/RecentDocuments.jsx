import React from "react";
import { Link } from "react-router-dom";
import PriorityBadge from "../triage/PriorityBadge";
import DocumentStatusBadge from "../documents/DocumentStatusBadge";
import { formatConfidence } from "../../utils/formatConfidence";
import { FaEye, FaUserCheck, FaArrowRight } from "react-icons/fa";

const RecentDocuments = ({ documents = [] }) => {
  return (
    <div className="card border-0 shadow-sm rounded-3">
      <div className="card-header bg-white py-3 d-flex justify-content-between align-items-center border-bottom">
        <h5 className="mb-0 fw-bold text-dark">Documentos Recientes</h5>
        <Link to="/documentos" className="btn btn-sm btn-outline-primary fw-semibold">
          Ver Historial Completo <FaArrowRight className="ms-1" />
        </Link>
      </div>
      <div className="card-body p-0">
        {!documents.length ? (
          <div className="text-center py-4 text-muted">No hay documentos recientes.</div>
        ) : (
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light">
                <tr>
                  <th>ID</th>
                  <th>Tipo</th>
                  <th>Prioridad</th>
                  <th>Confianza</th>
                  <th>Estado</th>
                  <th className="text-end px-4">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => {
                  const conf = formatConfidence(doc.clasificacion?.score_confianza);
                  const requiereAuditoria = doc.estado === "AUDITORIA" || doc.decision_enrutamiento?.requiere_auditoria;

                  return (
                    <tr key={doc.documento_id}>
                      <td className="fw-bold text-primary">{doc.documento_id}</td>
                      <td className="fw-medium">{doc.clasificacion?.tipo_documento || "Receta / Informe"}</td>
                      <td>
                        <PriorityBadge priority={doc.clasificacion?.prioridad} />
                      </td>
                      <td>
                        <span className={`badge ${conf.badgeClass}`}>{conf.formattedText}</span>
                      </td>
                      <td>
                        <DocumentStatusBadge estado={doc.estado} />
                      </td>
                      <td className="text-end px-4">
                        <div className="btn-group btn-group-sm">
                          <Link
                            to={`/documentos/${doc.documento_id}`}
                            className="btn btn-outline-primary"
                            title="Ver resultado del triaje"
                          >
                            <FaEye className="me-1" /> Ver Resultado
                          </Link>
                          {requiereAuditoria && (
                            <Link
                              to={`/auditoria/${doc.documento_id}`}
                              className="btn btn-warning text-dark"
                              title="Ir a auditoría humana"
                            >
                              <FaUserCheck className="me-1" /> Auditoría
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
        )}
      </div>
    </div>
  );
};

export default RecentDocuments;
