import React from "react";

const StatsCard = ({ title, value, icon, variant = "primary", subtitle }) => {
  return (
    <div className={`card border-0 shadow-sm rounded-3 h-100 border-start border-4 border-${variant}`}>
      <div className="card-body p-3.5 d-flex align-items-center justify-content-between">
        <div>
          <span className="text-muted fw-semibold small d-block mb-1">{title}</span>
          <h2 className="fw-bold mb-0 text-dark">{value}</h2>
          {subtitle && <span className="text-muted small mt-1 d-block">{subtitle}</span>}
        </div>
        <div className={`p-3 rounded-circle bg-${variant} bg-opacity-10 text-${variant}`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

export default StatsCard;
