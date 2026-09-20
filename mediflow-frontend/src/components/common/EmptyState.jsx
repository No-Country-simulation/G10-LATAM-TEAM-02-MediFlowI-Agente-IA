import React from "react";
import { FaFolderOpen } from "react-icons/fa";

const EmptyState = ({
  title = "No se encontraron registros",
  message = "No hay documentos disponibles para mostrar en este momento.",
  actionLabel,
  onAction
}) => {
  return (
    <div className="text-center py-5 px-3 my-4 bg-light rounded-3 border">
      <FaFolderOpen className="text-secondary opacity-50 mb-3" size={48} />
      <h5 className="fw-bold text-dark mb-2">{title}</h5>
      <p className="text-muted mb-4" style={{ maxWidth: "450px", margin: "0 auto" }}>
        {message}
      </p>
      {actionLabel && onAction && (
        <button className="btn btn-primary" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
