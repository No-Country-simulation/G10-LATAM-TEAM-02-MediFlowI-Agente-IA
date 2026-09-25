import React from "react";

const DocumentStatusBadge = ({ estado = "PROCESADO" }) => {
  const norm = (estado || "").toUpperCase();

  let badgeClass = "bg-secondary";
  let label = norm;

  switch (norm) {
    case "RECIBIDO":
      badgeClass = "bg-secondary";
      label = "Recibido";
      break;
    case "PROCESANDO":
      badgeClass = "bg-info text-dark";
      label = "Procesando";
      break;
    case "PROCESADO":
      badgeClass = "bg-success";
      label = "Procesado";
      break;
    case "AUDITORIA":
    case "AUDITORÍA":
      badgeClass = "bg-warning text-dark";
      label = "Auditoría";
      break;
    case "RECHAZADO":
      badgeClass = "bg-danger";
      label = "Rechazado";
      break;
    case "ERROR":
      badgeClass = "bg-dark";
      label = "Error";
      break;
    default:
      badgeClass = "bg-secondary";
      label = estado;
  }

  return <span className={`badge ${badgeClass} px-2.5 py-1.5 fw-semibold rounded-pill`}>{label}</span>;
};

export default DocumentStatusBadge;
