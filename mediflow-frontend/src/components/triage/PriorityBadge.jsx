import React from "react";

const PriorityBadge = ({ priority = "NORMAL" }) => {
  const normPriority = (priority || "").toUpperCase();

  if (normPriority === "URGENTE") {
    return (
      <span className="badge bg-danger text-white px-3 py-2 fs-6 rounded-pill d-inline-flex align-items-center">
        <span className="me-1">🔴</span> URGENTE
      </span>
    );
  }

  if (normPriority === "PRIORITARIO") {
    return (
      <span className="badge bg-warning text-dark px-3 py-2 fs-6 rounded-pill d-inline-flex align-items-center">
        <span className="me-1">🟠</span> PRIORITARIO
      </span>
    );
  }

  return (
    <span className="badge bg-success text-white px-3 py-2 fs-6 rounded-pill d-inline-flex align-items-center">
      <span className="me-1">🟢</span> NORMAL
    </span>
  );
};

export default PriorityBadge;
