import DocumentStatusBadge from "./DocumentStatusBadge";
import PriorityBadge from "../triage/PriorityBadge";
import { formatDate } from "../../utils/formatDate";
import type { ClinicalDocument } from "../../types/documents";

const DocumentInfo = ({ document }: { document: ClinicalDocument }) => {
  return (
    <div className="card border-0 shadow-sm mb-4">
      <div className="card-body">
        <div className="d-flex flex-wrap justify-content-between align-items-center mb-3">
          <div>
            <h4 className="fw-bold mb-1 text-primary">{document.documento_id}</h4>
            <span className="text-muted small">Archivo: {document.nombre_archivo} | Canal: {document.canal_origen || "General"}</span>
          </div>
          <div className="d-flex gap-2 align-items-center">
            <PriorityBadge priority={document.clasificacion?.prioridad} />
            <DocumentStatusBadge estado={document.estado} />
          </div>
        </div>
        <div className="text-muted small">
          Fecha de Recepción: <strong className="text-dark">{formatDate(document.fecha_creacion)}</strong>
        </div>
      </div>
    </div>
  );
};

export default DocumentInfo;
