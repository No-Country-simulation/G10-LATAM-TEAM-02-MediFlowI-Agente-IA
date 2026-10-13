import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import cn from "../utils/cn"
import {
  faFolder,
  faPaperclip,
  faCircleNotch,
  faTrashAlt,
  faRobot,
} from "@fortawesome/free-solid-svg-icons";
import { documentsApi } from "../api/documentsApi";
import { useAuth } from "../hooks/useAuth";
import { formatFileSize } from "../utils/fileFormatting";
import { NAV_PILLS, type TriageModalTab } from "../types/triageModal.types";

const NewDocument = () => {
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Estados de navegación y modal
  const [activePill, setActivePill] = useState<TriageModalTab>("enrutamiento");
  const [canalOrigen, setCanalOrigen] = useState("Consulta_Externa");
  const [fileToUpload, setFileToUpload] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Control de roles para píldoras superiores
  const userRole = currentUser?.rol || "OPERADOR";
  const visiblePills = NAV_PILLS.filter((pill) =>
    pill.rolesPermitidos.includes(
      userRole as "ADMINISTRADOR" | "OPERADOR" | "AUDITOR" | "SUPERVISOR"
    )
  );

  const handlePillClick = (pillId: TriageModalTab, route: string) => {
    setActivePill(pillId);
    if (pillId === "historial") {
      navigate("/documentos");
    } else if (pillId === "solicitudes") {
      navigate("/auditoria");
    } else if (route && route !== "/documentos/nuevo") {
      navigate(route);
    }
  };

  // Manejo de archivo
  const handleBrowseFiles = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (file) {
      setFileToUpload(file);
      setError(null);
    }
  };

  const handleCancelFile = () => {
    setFileToUpload(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0] || null;
    if (file) {
      setFileToUpload(file);
      setError(null);
    }
  };

  // Enviar a procesar
  const handleProcess = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fileToUpload) return;

    setIsProcessing(true);
    setError(null);

    try {
      const result = await documentsApi.procesarDocumento(fileToUpload, canalOrigen);
      navigate(`/documentos/${result.documento_id}`);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Ocurrió un error al procesar el documento"
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const userGreetingName = currentUser?.nombres ? `${currentUser.nombres}` : ", bienvenido a MediFlow";

  return (
    <div className="w-full flex flex-col items-center justify-center min-h-[calc(100vh-80px)] py-4 sm:py-6 gap-2 md:gap-4 relative z-10">
      {/* ── BARRA SUPERIOR DE PÍLDORAS (RBAC) ── */}
      <nav
        aria-label="Navegación de consola"
        className={cn(
          "p-1 mb-8",
          "inline-flex items-center",
          "bg-white/90 backdrop-blur-md border border-slate-200/80 rounded-full shadow-xs"
        )}
      >
        {visiblePills.map((pill) => {
          const isActive = activePill === pill.id;
          return (
            <button
              key={pill.id}
              type="button"
              onClick={() => handlePillClick(pill.id, pill.route)}
              className={cn(
                "text-xs sm:text-sm font-semibold",
                "px-4 sm:px-6 py-1.5 rounded-full transition-all cursor-pointer border-0",
                `${isActive ? "bg-slate-100/90 text-[#1f2041] shadow-2xs" : "bg-transparent text-slate-500 hover:text-slate-800"}`
              )}
            >
              {pill.label}
            </button>
          );
        })}
      </nav>

      {/* ── ENCABEZADO CENTRADO CON SALUDO ── */}
      <header className="flex flex-col items-center text-center max-w-2xl px-4 mb-8 gap-2 md:gap-4">
        <h1
          className="text-3xl sm:text-4xl md:text-[42px] font-bold text-[#1f2041] tracking-tight mb-3"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          Buen día {userGreetingName}
        </h1>
        <p
          className="text-xs sm:text-sm text-slate-500 max-w-xl leading-relaxed"
          style={{ fontFamily: "'Quicksand', sans-serif" }}
        >
          Bienvenido/a al panel de control. Para comenzar el análisis del documento, arrastre y suelte el
          archivo en el área indicada o presione el botón para examinar sus archivos.
        </p>
      </header>

      {/* ── BARRA SUPERIOR DEL MOTOR IA Y AJUSTES ── */}
      <div className="w-full max-w-2xl px-2 flex items-center justify-between mb-2.5">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#6FCF97]/30 text-[#15803D] font-bold text-xs tracking-wide border border-[#6FCF97]/40 shadow-2xs">
          <FontAwesomeIcon icon={faRobot} className="text-xs text-[#15803D]" />
          <span>GEMINI 1.5 Flash</span>
        </div>
      </div>

      {/* ── MODAL / TARJETA CENTRAL DE CARGA ── */}
      <section className="w-full max-w-2xl bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-200/70 transition-all flex flex-col gap-5">
        {/* Encabezado del modal */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div className="flex flex-col">
            <h2
              className="text-lg sm:text-xl font-bold text-[#1f2041]"
              style={{ fontFamily: "'Montserrat', sans-serif" }}
            >
              Ejecutar nuevo análisis
            </h2>
            <span className="text-xs text-slate-400 mt-0.5">
              Formatos soportados: PDF, PNG, JPG, JPEG, JSON (Máx. 10 MB)
            </span>
          </div>

          {/* Selector de Canal de Origen (Preservado) */}
          <div className="flex items-start flex-col gap-2 self-start sm:self-auto">
            <label htmlFor="canal-origen" className="text-xs font-semibold text-slate-500 whitespace-nowrap">
              Canal de Origen:
            </label>
            <select
              id="canal-origen"
              value={canalOrigen}
              onChange={(e) => setCanalOrigen(e.target.value)}
              disabled={isProcessing}
              className="text-xs font-medium text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-[#2C5282] cursor-pointer"
            >
              <option value="Consulta_Externa">Consulta_Externa</option>
              <option value="Guardia_Emergencias">Guardia_Emergencias</option>
              <option value="Admision">Admision</option>
              <option value="Laboratorio">Laboratorio</option>
            </select>
          </div>
        </div>

        {/* Input file nativo oculto */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.json"
          onChange={handleFileChange}
          className="hidden"
          disabled={isProcessing}
        />

        <form onSubmit={handleProcess} className="flex flex-col gap-4">
          {/* ESTADO 1: DROPZONE VACÍA (Sin archivo cargado) */}
          {!fileToUpload && (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-2xl p-8 sm:p-10 flex flex-col items-center justify-center text-center transition-all bg-slate-50/40 ${isDragging
                ? "border-emerald-400 bg-emerald-50/20 ring-2 ring-emerald-200"
                : "border-slate-200/90 hover:border-slate-300"
                }`}
            >
              {/* Contenedor del ícono de carpeta con halo suave */}
              <div
                className={cn(
                  "p-2 rounded-md bg-gradient-to-b from-white to-slate-100 border border-slate-200/60",
                  "shadow-xs flex items-center justify-center text-slate-600 mb-3.5"
                )}
              >
                <FontAwesomeIcon icon={faFolder} className="text-lg text-slate-500" />
              </div>

              <p className="text-xs sm:text-sm font-semibold text-slate-700 mb-1">
                Arrastre y suelte el archivo fuente para subirlo
              </p>
              <p className="text-xs text-slate-400 mb-5">
                o,{" "}
                <button
                  type="button"
                  onClick={handleBrowseFiles}
                  className="text-[#3B82F6] hover:underline font-medium cursor-pointer border-0 bg-transparent p-0"
                >
                  haga click para buscar
                </button>{" "}
                (10 MB max)
              </p>

              <button
                type="button"
                onClick={handleBrowseFiles}
                className="bg-[#2C5282] hover:bg-[#1E3A5F] text-white px-6 py-2.5 rounded-xl font-medium text-xs sm:text-sm transition-all shadow-xs cursor-pointer border-0"
              >
                Seleccionar archivos
              </button>
            </div>
          )}

          {/* ESTADO 2 Y 3: ARCHIVO CARGADO O PROCESANDO */}
          {fileToUpload && (
            <div className="flex flex-col gap-4">
              {/* Barra horizontal redondeada */}
              <div className="w-full bg-slate-100/90 rounded-2xl px-4 sm:px-5 py-3.5 flex items-center justify-between gap-3 border border-slate-200/60 transition-all">
                <div className="flex items-center gap-3 min-w-0">
                  <FontAwesomeIcon icon={faPaperclip} className="text-slate-400 text-sm shrink-0" />
                  <span
                    className="text-xs sm:text-sm font-medium text-slate-700 truncate"
                    title={fileToUpload.name}
                  >
                    {fileToUpload.name}
                  </span>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  {/* Durante procesamiento: Porcentaje y spinner */}
                  {isProcessing && (
                    <div className="flex items-center gap-2">
                      <FontAwesomeIcon
                        icon={faCircleNotch}
                        className="text-[#10B981] animate-spin text-xs"
                      />
                    </div>
                  )}

                  <span className="text-xs text-slate-500 font-medium">
                    {formatFileSize(fileToUpload.size)}
                  </span>

                  {!isProcessing && (
                    <button
                      type="button"
                      onClick={handleCancelFile}
                      aria-label="Descartar archivo"
                      className="text-slate-400 hover:text-red-500 p-1 transition-colors cursor-pointer border-0 bg-transparent"
                    >
                      <FontAwesomeIcon icon={faTrashAlt} className="text-xs" />
                    </button>
                  )}
                </div>
              </div>

              {/* Botones de acción inferiores alineados a la derecha */}
              <div className="flex items-center justify-end gap-3 pt-1">
                <button
                  type="button"
                  onClick={handleCancelFile}
                  disabled={isProcessing}
                  className={`px-5 py-2 rounded-xl text-xs sm:text-sm font-medium border border-slate-300 bg-white transition-all cursor-pointer ${isProcessing
                    ? "opacity-50 cursor-not-allowed text-slate-400"
                    : "text-slate-700 hover:bg-slate-50"
                    }`}
                >
                  Cancelar
                </button>

                <button
                  type="submit"
                  disabled={isProcessing}
                  className={`px-6 py-2 rounded-xl text-xs sm:text-sm font-medium text-white transition-all shadow-xs cursor-pointer border-0 flex items-center gap-2 ${isProcessing
                    ? "bg-[#2C5282]/80 opacity-70 cursor-not-allowed"
                    : "bg-[#2C5282] hover:bg-[#1E3A5F]"
                    }`}
                >
                  {isProcessing ? (
                    <>
                      <FontAwesomeIcon icon={faCircleNotch} className="animate-spin text-xs" />
                      <span>Analizando...</span>
                    </>
                  ) : (
                    <span>Continuar</span>
                  )}
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 text-red-700 border border-red-200 rounded-xl text-xs">
              {error}
            </div>
          )}
        </form>
      </section>
    </div>
  );
};

export default NewDocument;
