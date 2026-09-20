import React, { useState } from "react";
import { FaFilePdf, FaFileImage, FaExternalLinkAlt, FaExpand, FaCompress } from "react-icons/fa";

const DocumentViewer = ({ fileName = "", fileUrl }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const isPdf = fileName.toLowerCase().endsWith(".pdf");

  return (
    <div className={`card border-0 shadow-sm ${isExpanded ? "position-fixed top-0 start-0 w-100 h-100 z-3 m-0 rounded-0" : "h-100"}`}>
      <div className="card-header bg-light d-flex align-items-center justify-content-between py-2.5 px-3 border-bottom">
        <span className="fw-bold text-dark d-flex align-items-center small">
          {isPdf ? <FaFilePdf className="text-danger me-2 fs-5" /> : <FaFileImage className="text-primary me-2 fs-5" />}
          Documento Original: <span className="text-primary ms-1">{fileName || "Archivo adjunto"}</span>
        </span>

        <div className="d-flex align-items-center gap-2">
          {fileUrl && (
            <a href={fileUrl} target="_blank" rel="noreferrer" className="btn btn-sm btn-outline-secondary py-1 px-2.5 text-nowrap" title="Abrir en pestaña independiente">
              <FaExternalLinkAlt className="me-1" /> Abrir
            </a>
          )}
          <button
            className="btn btn-sm btn-outline-dark py-1 px-2"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? "Reducir tamaño" : "Pantalla completa"}
          >
            {isExpanded ? <FaCompress /> : <FaExpand />}
          </button>
        </div>
      </div>

      <div
        className="card-body p-2 d-flex flex-column align-items-center justify-content-center bg-dark text-white rounded-bottom"
        style={{ minHeight: isExpanded ? "calc(100vh - 60px)" : "480px" }}
      >
        {fileUrl ? (
          isPdf ? (
            <iframe
              src={fileUrl}
              title="Vista previa del documento PDF"
              className="w-100 h-100 rounded"
              style={{ minHeight: isExpanded ? "calc(100vh - 80px)" : "480px", border: "none" }}
            />
          ) : (
            <img
              src={fileUrl}
              alt="Vista del documento clínico"
              className="img-fluid rounded shadow-sm"
              style={{ maxHeight: isExpanded ? "85vh" : "480px", objectFit: "contain" }}
            />
          )
        ) : (
          <div className="text-center p-4">
            <div className="mb-3">
              {isPdf ? <FaFilePdf size={64} className="text-danger opacity-75" /> : <FaFileImage size={64} className="text-info opacity-75" />}
            </div>
            <h6 className="fw-bold">{fileName || "Documento Clínico"}</h6>
            <p className="small text-muted mb-0">Vista previa del archivo cargado en el sistema</p>
            <div className="mt-3 p-3 bg-secondary bg-opacity-25 rounded border border-secondary text-start small font-monospace" style={{ maxWidth: "380px" }}>
              <div className="text-info">// VISTA PREVIA DEL DOCUMENTO</div>
              <div>Archivo: {fileName}</div>
              <div>Formato: {isPdf ? "Documento PDF" : "Imagen Médica (JPG/PNG)"}</div>
              <div>Estado: Almacenado de forma segura</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentViewer;
