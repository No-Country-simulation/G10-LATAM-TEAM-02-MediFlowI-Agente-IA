import { useState, useRef, useEffect, useCallback } from "react";
import {
  FaFilePdf,
  FaFileImage,
  FaExternalLinkAlt,
  FaExpand,
  FaCompress,
  FaSearchPlus,
  FaSearchMinus,
  FaExclamationTriangle,
  FaDownload
} from "react-icons/fa";
import type { DocumentViewerProps, ViewerLoadingState } from "./DocumentViewer.types";

const DocumentViewer = ({
  fileName = "",
  fileUrl,
  minHeight = "480px",
  onFullScreenChange,
  onError
}: DocumentViewerProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [loadingState, setLoadingState] = useState<ViewerLoadingState>(fileUrl ? "loading" : "idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [prevFileUrl, setPrevFileUrl] = useState<string | undefined>(fileUrl);

  const isPdf = Boolean(
    fileName.toLowerCase().endsWith(".pdf") || (fileUrl && fileUrl.toLowerCase().includes(".pdf"))
  );

  // Reiniciar estado si cambia fileUrl
  if (fileUrl !== prevFileUrl) {
    setPrevFileUrl(fileUrl);
    setLoadingState(fileUrl ? "loading" : "idle");
    setErrorMessage(null);
    setZoomLevel(1);
  }

  // Sincronizar eventos de pantalla completa nativa
  useEffect(() => {
    const handleFullscreenChange = () => {
      const active = Boolean(
        document.fullscreenElement && document.fullscreenElement === containerRef.current
      );
      setIsExpanded(active);
      onFullScreenChange?.(active);
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
    };
  }, [onFullScreenChange]);

  const toggleFullscreen = useCallback(() => {
    if (!containerRef.current) return;

    if (document.fullscreenElement) {
      document.exitFullscreen?.().catch(() => {
        setIsExpanded(false);
        onFullScreenChange?.(false);
      });
    } else if (containerRef.current.requestFullscreen) {
      containerRef.current
        .requestFullscreen()
        .then(() => {
          setIsExpanded(true);
          onFullScreenChange?.(true);
        })
        .catch(() => {
          // Fallback a pantalla completa CSS si los permisos están bloqueados
          setIsExpanded((prev) => {
            const next = !prev;
            onFullScreenChange?.(next);
            return next;
          });
        });
    } else {
      setIsExpanded((prev) => {
        const next = !prev;
        onFullScreenChange?.(next);
        return next;
      });
    }
  }, [onFullScreenChange]);

  const handleZoomIn = () => {
    setZoomLevel((prev) => Math.min(2.5, +(prev + 0.25).toFixed(2)));
  };

  const handleZoomOut = () => {
    setZoomLevel((prev) => Math.max(0.5, +(prev - 0.25).toFixed(2)));
  };

  const handleZoomReset = () => {
    setZoomLevel(1);
  };

  const handleDocumentLoad = useCallback(() => {
    setLoadingState("ready");
    setErrorMessage(null);
  }, []);

  const handleDocumentError = useCallback(() => {
    const errorMsg = isPdf
      ? "Error de visualización del documento PDF"
      : "Error de decodificación de imagen clínica";
    setLoadingState("error");
    setErrorMessage(errorMsg);
    onError?.(new Error(errorMsg));
  }, [isPdf, onError]);

  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    const el = iframeRef.current;
    if (!el) return;
    const handleError = () => {
      handleDocumentError();
    };
    const handleLoad = () => {
      handleDocumentLoad();
    };
    el.addEventListener("error", handleError);
    el.addEventListener("load", handleLoad);
    return () => {
      el.removeEventListener("error", handleError);
      el.removeEventListener("load", handleLoad);
    };
  }, [fileUrl, isPdf, handleDocumentError, handleDocumentLoad]);

  return (
    <div
      ref={containerRef}
      className={`flex flex-col bg-white border border-slate-200 transition-all duration-200 ${
        isExpanded
          ? "fixed inset-0 z-50 w-screen h-screen m-0 rounded-none shadow-2xl"
          : "w-full h-full rounded-xl shadow-sm overflow-hidden"
      }`}
      style={{ minHeight: isExpanded ? "100vh" : minHeight }}
    >
      {/* Barra de herramientas accesible */}
      <div
        role="toolbar"
        aria-label="Controles de visualización del documento"
        className="bg-slate-50 border-b border-slate-200 px-3.5 py-2.5 flex flex-wrap items-center justify-between gap-2.5 text-slate-800"
      >
        {/* Nombre y tipo de documento */}
        <span className="font-semibold text-slate-800 flex items-center text-xs sm:text-sm min-w-0">
          {isPdf ? (
            <FaFilePdf className="text-rose-600 mr-2 text-base flex-shrink-0" />
          ) : (
            <FaFileImage className="text-sky-600 mr-2 text-base flex-shrink-0" />
          )}
          <span className="text-slate-500 font-normal mr-1 hidden sm:inline">Documento Original:</span>
          <span className="text-sky-700 font-medium truncate max-w-[180px] sm:max-w-xs md:max-w-md">
            {fileName || "Archivo adjunto"}
          </span>
        </span>

        {/* Acciones interactivas */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {fileUrl && loadingState !== "error" && (
            <div className="inline-flex rounded-md shadow-sm border border-slate-300 bg-white" role="group" aria-label="Controles de zoom">
              <button
                type="button"
                className="px-2 py-1 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-l-md disabled:opacity-40 disabled:pointer-events-none transition-colors"
                onClick={handleZoomOut}
                disabled={zoomLevel <= 0.5}
                title="Alejar documento"
                aria-label="Alejar documento"
              >
                <FaSearchMinus className="text-xs" />
              </button>
              <button
                type="button"
                className="px-2 py-1 text-xs font-mono font-medium text-slate-700 hover:bg-slate-100 border-x border-slate-200 transition-colors"
                onClick={handleZoomReset}
                title="Restablecer tamaño original (100%)"
                aria-label="Restablecer tamaño original (100%)"
              >
                {Math.round(zoomLevel * 100)}%
              </button>
              <button
                type="button"
                className="px-2 py-1 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-r-md disabled:opacity-40 disabled:pointer-events-none transition-colors"
                onClick={handleZoomIn}
                disabled={zoomLevel >= 2.5}
                title="Acercar documento"
                aria-label="Acercar documento"
              >
                <FaSearchPlus className="text-xs" />
              </button>
            </div>
          )}

          {/* Botón de Descarga Directa */}
          {fileUrl && (
            <a
              href={fileUrl}
              download={fileName || "documento_clinico"}
              className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-100 hover:text-slate-900 transition-colors shadow-sm"
              title="Descargar archivo original"
              aria-label="Descargar archivo original"
            >
              <FaDownload className="text-slate-500 text-xs" />
              <span className="hidden sm:inline">Descargar</span>
            </a>
          )}

          {/* Botón de apertura en pestaña independiente */}
          {fileUrl && (
            <a
              href={fileUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-100 hover:text-slate-900 transition-colors shadow-sm"
              title="Abrir en pestaña independiente"
              aria-label="Abrir en pestaña independiente"
            >
              <FaExternalLinkAlt className="text-slate-500 text-xs" />
              <span className="hidden sm:inline">Abrir</span>
            </a>
          )}

          {/* Alternancia a Pantalla Completa */}
          <button
            type="button"
            className="inline-flex items-center justify-center p-1.5 text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-100 hover:text-slate-900 transition-colors shadow-sm"
            onClick={toggleFullscreen}
            title={isExpanded ? "Reducir tamaño" : "Pantalla completa"}
            aria-label={isExpanded ? "Reducir tamaño" : "Pantalla completa"}
          >
            {isExpanded ? <FaCompress className="text-xs" /> : <FaExpand className="text-xs" />}
          </button>
        </div>
      </div>

      {/* Área del visor / Viewport */}
      <div
        className="flex-1 w-full p-2 sm:p-4 flex flex-col items-center justify-center bg-slate-900 text-slate-100 relative overflow-auto"
        style={{ minHeight: isExpanded ? "calc(100vh - 60px)" : "460px" }}
      >
        {fileUrl ? (
          loadingState === "error" ? (
            /* Panel de Contingencia Clínica */
            <div
              role="alert"
              className="w-full max-w-lg p-6 bg-slate-800/90 border border-rose-500/40 rounded-xl text-center shadow-lg my-auto"
            >
              <FaExclamationTriangle className="text-rose-500 text-4xl mx-auto mb-3" />
              <h3 className="text-base sm:text-lg font-bold text-rose-400 mb-2">
                {errorMessage || (isPdf ? "Error de visualización del documento" : "Error de decodificación de imagen")}
              </h3>
              <p className="text-xs sm:text-sm text-slate-300 mb-5 leading-relaxed">
                {isPdf
                  ? "No fue posible renderizar el documento PDF embebido en el navegador. Puede deberse a restricciones de seguridad, red o formato del archivo."
                  : "No fue posible decodificar o cargar la imagen clínica. El archivo podría estar dañado o el formato no es compatible con el navegador."}
              </p>
              <div className="flex flex-wrap items-center justify-center gap-3">
                <a
                  href={fileUrl}
                  download={fileName || "documento_clinico"}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold text-white bg-rose-600 rounded-lg hover:bg-rose-700 transition-colors shadow"
                  aria-label="Descargar documento original"
                >
                  <FaDownload className="text-xs" /> Descargar documento original
                </a>
                <a
                  href={fileUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-300 bg-slate-700/80 border border-slate-600 rounded-lg hover:bg-slate-700 hover:text-white transition-colors"
                  aria-label="Abrir archivo original en nueva pestaña"
                >
                  <FaExternalLinkAlt className="text-xs" /> Abrir archivo original en nueva pestaña
                </a>
              </div>
            </div>
          ) : isPdf ? (
            /* Visualizador de PDF con Skeleton Loader */
            <div className="w-full h-full flex flex-col items-center justify-center relative">
              {/* Skeleton Loader animado con Tailwind mientras carga */}
              {loadingState === "loading" && (
                <div
                  role="status"
                  aria-label="Cargando documento clínico..."
                  className="w-full max-w-2xl h-full min-h-[420px] p-6 bg-slate-800/80 rounded-xl border border-slate-700/60 shadow-inner flex flex-col justify-between animate-pulse my-auto"
                >
                  <div className="space-y-4">
                    <div className="flex items-center justify-between pb-3 border-b border-slate-700/60">
                      <div className="h-5 w-44 bg-slate-700 rounded-md"></div>
                      <div className="h-4 w-24 bg-slate-700/80 rounded-full"></div>
                    </div>
                    <div className="space-y-2.5 pt-2">
                      <div className="h-4 w-full bg-slate-700/70 rounded"></div>
                      <div className="h-4 w-5/6 bg-slate-700/60 rounded"></div>
                      <div className="h-4 w-4/6 bg-slate-700/50 rounded"></div>
                    </div>
                    <div className="grid grid-cols-2 gap-3 pt-3">
                      <div className="h-16 bg-slate-700/40 rounded-lg border border-slate-700/40"></div>
                      <div className="h-16 bg-slate-700/40 rounded-lg border border-slate-700/40"></div>
                    </div>
                    <div className="space-y-2.5 pt-2">
                      <div className="h-4 w-full bg-slate-700/60 rounded"></div>
                      <div className="h-4 w-3/4 bg-slate-700/50 rounded"></div>
                    </div>
                  </div>
                  <div className="flex items-center justify-center gap-2 pt-4 text-xs font-medium text-slate-400">
                    <div className="w-2.5 h-2.5 rounded-full bg-sky-500 animate-ping"></div>
                    <span>Preparando vista del documento clínico...</span>
                  </div>
                </div>
              )}

              {/* Contenedor embebido del documento con soporte de Zoom */}
              <div
                className={`w-full h-full flex items-center justify-center transition-opacity duration-200 ${
                  loadingState === "loading" ? "opacity-0 absolute pointer-events-none" : "opacity-100"
                }`}
                style={{
                  minHeight: isExpanded ? "calc(100vh - 80px)" : "460px"
                }}
              >
                <div
                  className="w-full h-full flex items-center justify-center"
                  style={{
                    transform: `scale(${zoomLevel})`,
                    transformOrigin: "center center",
                    transition: "transform 0.15s ease-out"
                  }}
                >
                  <iframe
                    ref={iframeRef}
                    src={fileUrl}
                    title="Vista previa del documento PDF"
                    className="w-full h-full rounded border-0 shadow-md bg-white"
                    style={{ minHeight: isExpanded ? "calc(100vh - 90px)" : "460px" }}
                    onLoad={handleDocumentLoad}
                    onError={handleDocumentError}
                  />
                </div>
              </div>
            </div>
          ) : (
            /* Visualizador de Imágenes Clínicas con Zoom */
            <div
              className="w-full h-full flex items-center justify-center overflow-auto p-2"
              style={{ minHeight: isExpanded ? "calc(100vh - 80px)" : "460px" }}
            >
              <img
                src={fileUrl}
                alt="Vista del documento clínico"
                className="max-w-full max-h-[80vh] object-contain rounded shadow-md"
                onError={handleDocumentError}
                onLoad={handleDocumentLoad}
                style={{
                  transform: `scale(${zoomLevel})`,
                  transformOrigin: "center center",
                  transition: "transform 0.15s ease-out"
                }}
              />
            </div>
          )
        ) : (
          /* Estado vacío sin archivo */
          <div className="text-center p-8 max-w-sm">
            <div className="mb-4 inline-flex p-3 rounded-full bg-slate-800 text-sky-400">
              {isPdf ? (
                <FaFilePdf className="text-4xl text-rose-500" />
              ) : (
                <FaFileImage className="text-4xl text-sky-400" />
              )}
            </div>
            <h4 className="font-semibold text-slate-200 text-base mb-1">
              {fileName || "Documento Clínico"}
            </h4>
            <p className="text-xs text-slate-400 mb-4">
              Vista previa del archivo cargado en el sistema
            </p>
            <div className="p-3 bg-slate-800/80 rounded-lg border border-slate-700 text-left text-xs font-mono text-slate-300 space-y-1">
              <div className="text-sky-400 font-semibold">// VISTA PREVIA DEL DOCUMENTO</div>
              <div>Archivo: {fileName || "Sin especificar"}</div>
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
