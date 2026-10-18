import { useState } from "react";
import {
  FaFilePdf,
  FaFileImage,
  FaExternalLinkAlt,
  FaExpand,
  FaCompress,
  FaSearchPlus,
  FaSearchMinus,
  FaExclamationTriangle
} from "react-icons/fa";

interface DocumentViewerProps {
  fileName?: string;
  fileUrl?: string;
}

const DocumentViewer = ({ fileName = "", fileUrl }: DocumentViewerProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [imageError, setImageError] = useState(false);
  const [prevFileUrl, setPrevFileUrl] = useState(fileUrl);

  if (fileUrl !== prevFileUrl) {
    setPrevFileUrl(fileUrl);
    setImageError(false);
    setZoomLevel(1);
  }

  const isPdf = fileName.toLowerCase().endsWith(".pdf");

  const handleZoomIn = () => {
    setZoomLevel((prev) => Math.min(2.5, +(prev + 0.25).toFixed(2)));
  };

  const handleZoomOut = () => {
    setZoomLevel((prev) => Math.max(0.5, +(prev - 0.25).toFixed(2)));
  };

  const handleZoomReset = () => {
    setZoomLevel(1);
  };

  return (
    <div className={`card border-0 shadow-sm ${isExpanded ? "position-fixed top-0 start-0 w-100 h-100 z-3 m-0 rounded-0" : "h-100"}`}>
      <div className="card-header bg-light d-flex align-items-center justify-content-between py-2.5 px-3 border-bottom">
        <span className="fw-bold text-dark d-flex align-items-center small">
          {isPdf ? <FaFilePdf className="text-danger me-2 fs-5" /> : <FaFileImage className="text-primary me-2 fs-5" />}
          Documento Original: <span className="text-primary ms-1">{fileName || "Archivo adjunto"}</span>
        </span>

        <div className="d-flex align-items-center gap-2">
          {!isPdf && fileUrl && !imageError && (
            <div className="btn-group btn-group-sm" role="group" aria-label="Controles de zoom">
              <button
                type="button"
                className="btn btn-sm btn-outline-secondary py-1 px-2"
                onClick={handleZoomOut}
                disabled={zoomLevel <= 0.5}
                title="Alejar imagen"
                aria-label="Alejar imagen"
              >
                <FaSearchMinus />
              </button>
              <button
                type="button"
                className="btn btn-sm btn-outline-secondary py-1 px-2 font-monospace small"
                onClick={handleZoomReset}
                title="Restablecer tamaño original (100%)"
                aria-label="Restablecer tamaño original"
              >
                {Math.round(zoomLevel * 100)}%
              </button>
              <button
                type="button"
                className="btn btn-sm btn-outline-secondary py-1 px-2"
                onClick={handleZoomIn}
                disabled={zoomLevel >= 2.5}
                title="Acercar imagen"
                aria-label="Acercar imagen"
              >
                <FaSearchPlus />
              </button>
            </div>
          )}

          {fileUrl && (
            <a href={fileUrl} target="_blank" rel="noreferrer" className="btn btn-sm btn-outline-secondary py-1 px-2.5 text-nowrap" title="Abrir en pestaña independiente">
              <FaExternalLinkAlt className="me-1" /> Abrir
            </a>
          )}
          <button
            className="btn btn-sm btn-outline-dark py-1 px-2"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? "Reducir tamaño" : "Pantalla completa"}
            aria-label={isExpanded ? "Reducir tamaño" : "Pantalla completa"}
          >
            {isExpanded ? <FaCompress /> : <FaExpand />}
          </button>
        </div>
      </div>

      <div
        className="card-body p-2 d-flex flex-column align-items-center justify-content-center bg-dark text-white rounded-bottom overflow-auto position-relative"
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
          ) : imageError ? (
            <div className="text-center p-4 bg-danger bg-opacity-10 border border-danger rounded-3 m-3" style={{ maxWidth: "480px" }} role="alert">
              <FaExclamationTriangle size={48} className="text-danger mb-3" />
              <h6 className="fw-bold text-danger mb-2">Error de decodificación de imagen</h6>
              <p className="small text-light mb-3">
                No fue posible decodificar o cargar la imagen clínica. El archivo podría estar dañado o el formato no es compatible con el navegador.
              </p>
              <a
                href={fileUrl}
                target="_blank"
                rel="noreferrer"
                className="btn btn-sm btn-outline-danger"
              >
                <FaExternalLinkAlt className="me-1" /> Abrir archivo original en nueva pestaña
              </a>
            </div>
          ) : (
            <div
              className="d-flex align-items-center justify-content-center w-100 h-100 overflow-auto p-2"
              style={{ minHeight: isExpanded ? "calc(100vh - 80px)" : "460px" }}
            >
              <img
                src={fileUrl}
                alt="Vista del documento clínico"
                className="img-fluid rounded shadow-sm"
                onError={() => setImageError(true)}
                style={{
                  maxHeight: isExpanded ? "85vh" : "480px",
                  objectFit: "contain",
                  transform: `scale(${zoomLevel})`,
                  transformOrigin: "center center",
                  transition: "transform 0.15s ease-out"
                }}
              />
            </div>
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
              <div>Formato: {isPdf ? "Documento PDF" : "Imagen Médica (JPG/PNG/WebP)"}</div>
              <div>Estado: Almacenado de forma segura</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentViewer;
