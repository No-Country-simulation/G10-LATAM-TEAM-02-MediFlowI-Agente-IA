import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { FaCloudUploadAlt, FaFilePdf, FaFileImage, FaTimes, FaCheckCircle, FaExclamationTriangle } from "react-icons/fa";

const ALLOWED_TYPES = ["application/pdf", "image/jpeg", "image/jpg", "image/png"];
const MAX_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB

const CHANNELS = [
  "Emergencia",
  "Consulta Externa",
  "Hospitalización",
  "Laboratorio",
  "Administrativo",
  "Otro"
];

const DocumentUploader = ({ onProcess, onCancel, isProcessing }) => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [canalOrigen, setCanalOrigen] = useState("Consulta Externa");
  const [errorMessage, setErrorMessage] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);

  const fileInputRef = useRef(null);

  const validateAndSetFile = (selectedFile) => {
    setErrorMessage("");

    if (!selectedFile) {
      setErrorMessage("Debe seleccionar un documento.");
      return false;
    }

    if (!ALLOWED_TYPES.includes(selectedFile.type) && !selectedFile.name.match(/\.(pdf|jpg|jpeg|png)$/i)) {
      setErrorMessage("El formato del archivo no está permitido. Solo se permiten PDF, JPG y PNG.");
      return false;
    }

    if (selectedFile.size > MAX_SIZE_BYTES) {
      setErrorMessage("El archivo supera los 10 MB.");
      return false;
    }

    setFile(selectedFile);
    return true;
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleClearFile = () => {
    setFile(null);
    setErrorMessage("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleCancelClick = () => {
    handleClearFile();
    if (onCancel) {
      onCancel();
    } else {
      navigate("/dashboard");
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) {
      setErrorMessage("Debe seleccionar un documento.");
      return;
    }
    if (onProcess) {
      onProcess(file, canalOrigen);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024 * 1024) {
      return `${Math.round(bytes / 1024)} KB`;
    }
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const isPdf = file?.name.toLowerCase().endsWith(".pdf");

  return (
    <div className="card shadow-sm border-0 rounded-4">
      <div className="card-header bg-white py-3 border-bottom px-4">
        <h5 className="mb-0 fw-bold text-dark">Carga de documento clínico</h5>
        <span className="text-muted small">Suba una receta, orden o informe clínico en PDF o imagen para triaje automático</span>
      </div>

      <div className="card-body p-4">
        {errorMessage && (
          <div className="alert alert-danger d-flex align-items-center alert-dismissible fade show rounded-3 mb-4" role="alert">
            <FaExclamationTriangle className="me-2 flex-shrink-0 fs-5" />
            <div>{errorMessage}</div>
            <button type="button" className="btn-close" onClick={() => setErrorMessage("")}></button>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Dropzone */}
          <div
            className={`border border-2 border-dashed rounded-4 p-4 text-center mb-4 transition-all ${
              isDragOver
                ? "border-primary bg-primary bg-opacity-10 scale-102"
                : file
                ? "border-success bg-success bg-opacity-10"
                : "border-secondary border-opacity-25 bg-light hover-bg-light"
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            style={{ cursor: "pointer", minHeight: "230px", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}
            onClick={() => !file && fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
              className="d-none"
              disabled={isProcessing}
            />

            {!file ? (
              <>
                <div className="p-3 bg-white rounded-circle shadow-sm mb-3">
                  <FaCloudUploadAlt size={48} className="text-primary" />
                </div>
                <h5 className="fw-bold text-dark mb-1">Arrastre el documento aquí</h5>
                <p className="text-muted small mb-3">Formatos permitidos: <strong>PDF / JPG / PNG</strong> (Hasta 10 MB)</p>
                <button
                  type="button"
                  className="btn btn-outline-primary btn-sm px-4 fw-bold rounded-pill shadow-sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    fileInputRef.current?.click();
                  }}
                  disabled={isProcessing}
                >
                  Seleccionar archivo
                </button>
              </>
            ) : (
              <div className="w-100 p-3 bg-white rounded-3 shadow-sm border d-flex align-items-center justify-content-between">
                <div className="d-flex align-items-center text-start">
                  <div className="p-2 bg-light rounded me-3">
                    {isPdf ? <FaFilePdf size={36} className="text-danger" /> : <FaFileImage size={36} className="text-primary" />}
                  </div>
                  <div>
                    <h6 className="fw-bold mb-0 text-dark d-flex align-items-center">
                      {file.name}
                      <FaCheckCircle className="text-success ms-2 fs-6" title="Archivo válido" />
                    </h6>
                    <span className="text-muted small">Tamaño: {formatFileSize(file.size)} | Tipo: {file.type || "Documento"}</span>
                  </div>
                </div>
                <button
                  type="button"
                  className="btn btn-outline-danger btn-sm rounded-circle p-2 ms-2"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleClearFile();
                  }}
                  disabled={isProcessing}
                  title="Quitar archivo"
                >
                  <FaTimes size={14} />
                </button>
              </div>
            )}
          </div>

          {/* Channel selector */}
          <div className="mb-4">
            <label className="form-label fw-bold text-dark mb-1 small text-uppercase letter-spacing-1">Canal de origen</label>
            <select
              className="form-select form-select-lg fs-6 rounded-3"
              value={canalOrigen}
              onChange={(e) => setCanalOrigen(e.target.value)}
              disabled={isProcessing}
            >
              {CHANNELS.map((ch) => (
                <option key={ch} value={ch}>
                  {ch}
                </option>
              ))}
            </select>
          </div>

          {/* Action buttons */}
          <div className="d-flex justify-content-end gap-2 border-top pt-3">
            <button
              type="button"
              className="btn btn-light border px-4 rounded-pill fw-semibold"
              onClick={handleCancelClick}
              disabled={isProcessing}
            >
              CANCELAR
            </button>
            <button
              type="submit"
              className="btn btn-primary px-4 fw-bold rounded-pill shadow-sm"
              disabled={isProcessing || !file}
            >
              {isProcessing ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  PROCESANDO...
                </>
              ) : (
                "PROCESAR"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DocumentUploader;
