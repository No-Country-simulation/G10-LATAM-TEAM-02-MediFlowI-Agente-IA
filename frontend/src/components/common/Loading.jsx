import React from "react";

const Loading = ({ message = "Cargando información..." }) => {
  return (
    <div className="d-flex flex-column align-items-center justify-content-center py-5">
      <div className="spinner-border text-primary" role="status" style={{ width: "3rem", height: "3rem" }}>
        <span className="visually-hidden">Cargando...</span>
      </div>
      <p className="mt-3 text-muted fw-medium">{message}</p>
    </div>
  );
};

export default Loading;
