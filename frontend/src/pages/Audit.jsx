import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Loading from "../components/common/Loading";
import EmptyState from "../components/common/EmptyState";
import ErrorMessage from "../components/common/ErrorMessage";
import { auditApi } from "../api/auditApi";
import { formatConfidence } from "../utils/formatConfidence";
import { formatDateShort } from "../utils/formatDate";
import { FaUserCheck, FaClipboardList, FaExclamationTriangle } from "react-icons/fa";

const Audit = () => {
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAudits = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await auditApi.obtenerAuditorias();
      setAudits(data);
    } catch (err) {
      setError("Error al cargar los casos de auditoría pendiente.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudits();
  }, []);

  if (loading) return <Loading message="Cargando casos de auditoría humana..." />;
  if (error) return <ErrorMessage title="Error de Auditoría" message={error} onRetry={fetchAudits} />;

  return (
    <div className="audit-page">
      <div className="d-flex flex-wrap align-items-center justify-content-between mb-4">
        <div>
          <h3 className="fw-bold text-dark mb-1 d-flex align-items-center">
            <FaClipboardList className="text-warning me-2" /> Auditoría Humana de Documentos
          </h3>
          <p className="text-muted small mb-0">
            Revisión manual requerida para casos con confianza baja, inconsistencias o datos incompletos
          </p>
        </div>
      </div>

      <div className="card border-0 shadow-sm rounded-3">
        <div className="card-body p-0">
          {!audits.length ? (
            <EmptyState
              title="No hay documentos pendientes de auditoría"
              message="Actualmente todos los documentos han sido triados automáticamente con alta confianza o ya han sido auditados."
            />
          ) : (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
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
                            className="btn btn-warning text-dark fw-bold btn-sm px-3 shadow-sm"
                          >
                            <FaUserCheck className="me-1" /> REVISAR
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
