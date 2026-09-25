import React from "react";
import { FaExclamationTriangle } from "react-icons/fa";

const ErrorMessage = ({
  title = "Ocurrió un error",
  message = "No fue posible comunicarse con el servicio. Por favor, reintente más tarde.",
  onRetry
}) => {
  return (
    <div className="alert alert-danger d-flex align-items-center p-3 my-3 shadow-sm rounded-3" role="alert">
      <FaExclamationTriangle size={24} className="me-3 flex-shrink-0" />
      <div className="flex-grow-1">
        <h6 className="alert-heading fw-bold mb-1">{title}</h6>
        <p className="mb-0 small">{message}</p>
      </div>
      {onRetry && (
        <button className="btn btn-outline-danger btn-sm ms-3" onClick={onRetry}>
          Reintentar
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;
