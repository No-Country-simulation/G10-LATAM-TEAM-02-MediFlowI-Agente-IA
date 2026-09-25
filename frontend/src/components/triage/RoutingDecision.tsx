import { FaRoute, FaExclamationTriangle, FaCheckCircle } from "react-icons/fa";

interface RoutingDecisionProps {
  decision?: { destino?: string; requiere_auditoria?: boolean; motivo_auditoria?: string | null }
  clasificacion?: unknown
}

const RoutingDecision = ({ decision = {} }: RoutingDecisionProps) => {
  const destino = decision.destino || "NO ASIGNADO";
  const requiereAuditoria = decision.requiere_auditoria || false;
  const motivo = decision.motivo_auditoria;

  return (
    <div className="card border-0 shadow-sm mb-4">
      <div className="card-header bg-primary text-white py-3">
        <h5 className="mb-0 fw-bold d-flex align-items-center">
          <FaRoute className="me-2" /> Decisión de Enrutamiento y Triaje
        </h5>
      </div>
      <div className="card-body">
        <div className="row align-items-center">
          <div className="col-md-6 mb-3 mb-md-0">
            <span className="text-muted small d-block">Destino Asignado:</span>
            <div className="fs-3 fw-bold text-primary mt-1">
              {destino}
            </div>
          </div>

          <div className="col-md-6">
            <span className="text-muted small d-block mb-1">Estado de Revisión:</span>
            {requiereAuditoria ? (
              <div className="alert alert-warning mb-0 py-2 px-3 d-flex align-items-center">
                <FaExclamationTriangle className="me-2 text-warning fs-5 flex-shrink-0" />
                <div>
                  <strong className="d-block">Derivado a Auditoría Humana</strong>
                  <span className="small text-dark">{motivo || "Caso ambiguo o datos incompletos"}</span>
                </div>
              </div>
            ) : (
              <div className="alert alert-success mb-0 py-2 px-3 d-flex align-items-center">
                <FaCheckCircle className="me-2 text-success fs-5 flex-shrink-0" />
                <div>
                  <strong className="d-block">Enrutamiento Automático Exitoso</strong>
                  <span className="small text-muted">Procesado sin requerir intervención manual</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RoutingDecision;
