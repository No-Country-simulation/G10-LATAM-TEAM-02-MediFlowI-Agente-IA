import { useCallback, useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Loading from "../components/common/Loading";
import EmptyState from "../components/common/EmptyState";
import ErrorMessage from "../components/common/ErrorMessage";
import { auditApi } from "../api/auditApi";
import { formatConfidence } from "../utils/formatConfidence";
import { formatDateShort } from "../utils/formatDate";
import { FaUserCheck, FaClipboardList, FaExclamationTriangle } from "react-icons/fa";
import PageHeader from "../components/common/PageHeader";
import type { ClinicalDocument } from '../types/documents'

const Audit = () => {
  const [audits, setAudits] = useState<ClinicalDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAudits = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await auditApi.obtenerAuditorias();
      setAudits(data);
    } catch {
      setError("Error al cargar los casos de auditoría pendiente.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    queueMicrotask(() => void fetchAudits());
  }, [fetchAudits]);

  if (loading) return <Loading message="Cargando casos de auditoría humana..." />;
  if (error) return <ErrorMessage title="Error de Auditoría" message={error} onRetry={fetchAudits} />;

  return (
    <div className="clinical-page audit-page">
      <PageHeader
        eyebrow="Human-in-the-Loop"
        title="Auditoría clínica"
        description="Revisa documentos con baja confianza, inconsistencias o información incompleta."
        icon={<FaClipboardList />}
      />

      <div className="clinical-surface">
        <div className="card-body p-0">
          {!audits.length ? (
            <EmptyState
              title="No hay documentos pendientes de auditoría"
              message="Actualmente todos los documentos han sido triados automáticamente con alta confianza o ya han sido auditados."
            />
          ) : (
            <div className="table-responsive">
              <table className="table table-hover clinical-data-table">
                <caption className="visually-hidden">Documentos pendientes de auditoría humana</caption>
                <thead className="table-light">
                  <tr>
                    <th>ID</th>
                    <th>Documento</th>
                    <th>Confianza</th>
                    <th>Motivo de Derivación</th>
                    <th>Fecha</th>
                    <th className="text-center">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {audits.map((item) => {
                    const conf = formatConfidence(item.clasificacion?.score_confianza);
                    const motivo =
                      item.decision_enrutamiento?.motivo_auditoria ||
                      "Confianza baja o datos incompletos detectados";

                    return (
                      <tr key={item.documento_id}>
                        <td className="fw-bold text-primary">{item.documento_id}</td>
                        <td className="fw-medium text-dark">{item.nombre_archivo}</td>
                        <td>
                          <span className={`badge ${conf.badgeClass}`}>{conf.formattedText} ({conf.level})</span>
                        </td>
                        <td>
                          <span className="d-flex align-items-center text-dark small">
                            <FaExclamationTriangle className="text-warning me-1 flex-shrink-0" />
                            {motivo}
                          </span>
                        </td>
                        <td className="small text-muted">{formatDateShort(item.fecha_creacion)}</td>
                        <td className="text-center">
                          <Link
                            to={`/auditoria/${item.documento_id}`}
                            className="btn btn-warning text-dark btn-sm px-3"
                          >
                            <FaUserCheck className="me-1" /> Revisar
                          </Link>
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
    </div>
  );
};

export default Audit;
