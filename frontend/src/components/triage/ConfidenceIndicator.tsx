import { formatConfidence } from "../../utils/formatConfidence";

const ConfidenceIndicator = ({ score }: { score?: number }) => {
  const conf = formatConfidence(score);

  return (
    <div className="confidence-indicator w-100">
      <div className="d-flex justify-content-between align-items-center mb-1.5">
        <span className="fw-semibold text-secondary small">Score de Confianza IA:</span>
        <span className={`badge ${conf.badgeClass} fw-bold fs-7`}>
          {conf.formattedText} ({conf.level})
        </span>
      </div>
      <div className="position-relative">
        <div className="progress rounded-pill shadow-inner" style={{ height: "14px" }}>
          <div
            className={`progress-bar ${conf.progressClass} progress-bar-striped progress-bar-animated rounded-pill`}
            role="progressbar"
            style={{ width: `${conf.percentage}%` }}
            aria-valuenow={conf.percentage}
            aria-valuemin={0}
            aria-valuemax={100}
          ></div>
        </div>
        {/* Threshold indicator line at 60% */}
        <div
          className="position-absolute top-0 bottom-0 border-end border-2 border-dark"
          style={{ left: "60%", opacity: 0.35 }}
          title="Umbral de Auditoría Humana (60%)"
        ></div>
      </div>
      <div className="d-flex justify-content-between text-muted mt-1" style={{ fontSize: "0.7rem" }}>
        <span>0%</span>
        <span className="fw-semibold text-dark">Umbral Auditoría: 60%</span>
        <span>100%</span>
      </div>
    </div>
  );
};

export default ConfidenceIndicator;
