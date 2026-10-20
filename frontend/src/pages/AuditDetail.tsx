import { useCallback, useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import DocumentViewer from "../components/documents/DocumentViewer";
import ConfirmModal from "../components/common/ConfirmModal";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import { auditApi } from "../api/auditApi";
import { CLINICAL_DOCUMENT_TYPES, normalizeClinicalDocumentType } from "../constants/clinicalDocumentTypes";
import {
  LuArrowLeft,
  LuUser,
  LuHeart,
  LuFileText,
  LuZap,
  LuCircleAlert,
  LuCheck,
  LuLock,
  LuStethoscope,
  LuFilePen,
  LuUsers,
  LuBell,
  LuChevronDown,
  LuChevronUp,
  LuChevronRight,
} from "react-icons/lu";
import type { ChangeEvent } from "react";
import type { ClinicalDocument } from "../types/documents";

type AuditAction = "aprobar" | "rechazar" | "corregir" | null;
type ModalVariant = "primary" | "danger" | "warning" | "success";

interface ModalConfig {
  show: boolean;
  type: AuditAction;
  title: string;
  message: string;
  variant: ModalVariant;
}

const AuditDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [doc, setDoc] = useState<ClinicalDocument | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  // Accordion collapse states
  const [openSections, setOpenSections] = useState({
    clasificacion: true,
    datosExtraidos: true,
    enrutamiento: true,
    notificacion: true,
  });

  const toggleSection = (key: keyof typeof openSections) => {
    setOpenSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  // Form state for editing
  const [formData, setFormData] = useState({
    pacienteNombre: "",
    pacienteDni: "",
    pacienteEdad: "",
    medicoNombre: "",
    medicoCmp: "",
    tipoDocumento: "",
    especialidad: "",
    prioridad: "NORMAL",
    confianzaClasificacion: "98%",
    formatoArchivo: "PDF",
    estudioRealizado: "",
    diagnostico: "",
    cie10: "",
    destino: "Cola de Emergencia Médica",
    justificacionEnrutamiento: "",
    canalNotificacion: "Alerta de Guardia Médica",
    mensajeNotificacion: "",
  });

  // Modal controls
  const [modalConfig, setModalConfig] = useState<ModalConfig>({
    show: false,
    type: null,
    title: "",
    message: "",
    variant: "primary",
  });

  const loadAuditData = useCallback(async () => {
    if (!id) {
      setError("El identificador del documento es obligatorio.");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await auditApi.obtenerAuditoriaPorId(id);
      setDoc(data);

      const rawPriority = data.clasificacion?.prioridad || "URGENTE";
      const scoreVal = data.clasificacion?.score_confianza ?? 0.25;
      const scorePercent = Math.round(scoreVal * (scoreVal <= 1 ? 100 : 1));

      // Pre-fill form
      setFormData({
        pacienteNombre: data.datos_extraidos?.paciente?.nombre || "Carlos Eduardo Mendes",
        pacienteDni: data.datos_extraidos?.paciente?.dni || "88084446",
        pacienteEdad: data.datos_extraidos?.paciente?.edad ? `${data.datos_extraidos.paciente.edad} años` : "25 años",
        medicoNombre: data.datos_extraidos?.medico?.nombre || "Dra. Renata Silveira",
        medicoCmp: data.datos_extraidos?.medico?.cmp || "145892",
        tipoDocumento: normalizeClinicalDocumentType(data.clasificacion?.tipo_documento) || "Informe Radiológico",
        especialidad: data.clasificacion?.especialidad || "Radiología / Neuropatología",
        prioridad: rawPriority,
        confianzaClasificacion: `${scorePercent || 98}%`,
        formatoArchivo: data.nombre_archivo?.toLowerCase().endsWith(".pdf") ? "PDF" : "PDF",
        estudioRealizado: data.datos_extraidos?.estudio_solicitado || "Tomografía de Tórax con contraste",
        diagnostico: data.datos_extraidos?.diagnostico || "Tromboembolismo Pulmonar Agudo (TEP)",
        cie10: data.datos_extraidos?.cie10 || "I26.9",
        destino: data.decision_enrutamiento?.destino || "Cola de Emergencia Médica",
        justificacionEnrutamiento:
          data.decision_enrutamiento?.motivo_auditoria ||
          "Hallazgo crítico de alta gravedad (TEP agudo) detectado en paciente sintomático.",
        canalNotificacion: "Alerta de Guardia Médica",
        mensajeNotificacion: `ALERTA URGENTE: Informe crítico para el paciente ${
          data.datos_extraidos?.paciente?.nombre || "Carlos Eduardo Mendes"
        } en Guardia de Emergencias.`,
      });
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : `Error al cargar auditoría para ${id}`);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    queueMicrotask(() => void loadAuditData());
  }, [loadAuditData]);

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleOpenRechazar = () => {
    setModalConfig({
      show: true,
      type: "rechazar",
      title: "Rechazar Documento",
      message: "¿Está seguro de rechazar este documento? El expediente pasará a estado RECHAZADO.",
      variant: "danger",
    });
  };

  const handleOpenConfirmar = () => {
    setModalConfig({
      show: true,
      type: "corregir",
      title: "Confirmar y Enviar Decisión",
      message: "¿Desea validar y despachar los datos clínicos auditados al destino de triaje asignado?",
      variant: "primary",
    });
  };

  const handleConfirmAction = async () => {
    if (!id) return;
    setActionLoading(true);
    setActionError(null);
    try {
      if (modalConfig.type === "rechazar") {
        await auditApi.rechazarAuditoria(id);
      } else {
        const payload = {
          paciente: {
            nombre: formData.pacienteNombre,
            dni: formData.pacienteDni,
            edad: formData.pacienteEdad.replace(/\D/g, "") || undefined,
          },
          medico: {
            nombre: formData.medicoNombre,
            cmp: formData.medicoCmp,
          },
          diagnostico: formData.diagnostico,
          cie10: formData.cie10,
          tipo_documento: formData.tipoDocumento,
          prioridad: formData.prioridad,
          destino: formData.destino,
        };
        await auditApi.corregirAuditoria(id, payload);
        await auditApi.aprobarAuditoria(id);
      }

      setModalConfig((prev) => ({ ...prev, show: false }));
      navigate(`/documentos/${id}`);
    } catch (caughtError) {
      setModalConfig((prev) => ({ ...prev, show: false }));
      setActionError(caughtError instanceof Error ? caughtError.message : "No se pudo completar la auditoría.");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <Loading message={`Cargando detalle de auditoría para ${id}...`} />;
  if (error) return <ErrorMessage title="Error al cargar auditoría" message={error} onRetry={loadAuditData} />;
  if (!doc) return <ErrorMessage title="No encontrado" message="El documento no existe." />;

  const confidence = doc.clasificacion?.score_confianza ?? 0.25;
  const confidencePercent = Math.round(confidence * (confidence <= 1 ? 100 : 1));

  return (
    <div className="w-full max-w-7xl mx-auto px-2 sm:px-4 py-2">
      {/* Barra superior con navegación de píldoras y botón de regreso */}
      <div className="flex items-center justify-between mb-4">
        <Link
          to="/auditoria"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#204A79] hover:text-[#153457] transition-colors no-underline"
        >
          <LuArrowLeft size={15} />
          <span>Atrás</span>
        </Link>

        {/* Píldoras de Navegación Rápida */}
        <div className="inline-flex items-center bg-[#EDEBE6] p-1 rounded-full text-xs font-medium border border-[#DDD9D0]">
          <Link
            to="/documentos/nuevo"
            className="px-3.5 py-1 text-slate-600 hover:text-slate-900 rounded-full transition-colors no-underline"
          >
            Enrutamiento
          </Link>
          <Link
            to="/documentos"
            className="px-3.5 py-1 text-slate-600 hover:text-slate-900 rounded-full transition-colors no-underline"
          >
            Historial
          </Link>
          <span className="px-3.5 py-1 bg-white text-slate-900 font-semibold rounded-full shadow-2xs">
            Solicitudes
          </span>
        </div>

        <div className="w-12 hidden sm:block" />
      </div>

      {/* Encabezado Principal Centrado */}
      <div className="text-center mb-6">
        <h1
          className="text-2xl sm:text-3xl font-extrabold text-[#1F2041] tracking-tight mb-1"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          Auditoría de triaje
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 font-medium max-w-xl mx-auto mb-3">
          Human in the loop: Validación y corrección de los datos extraídos por el agente
        </p>

        {/* Indicador de porcentaje de confianza */}
        <div className="inline-flex items-center gap-2 text-xs sm:text-sm font-semibold text-slate-700">
          <span>Porcentaje de confianza:</span>
          <span
            className={`px-3.5 py-0.5 rounded-full text-xs font-bold border ${
              confidencePercent < 50
                ? "border-rose-400 text-rose-600 bg-rose-50/60"
                : confidencePercent < 80
                ? "border-amber-400 text-amber-700 bg-amber-50/60"
                : "border-emerald-400 text-emerald-700 bg-emerald-50/60"
            }`}
          >
            {confidencePercent}%
          </span>
        </div>
      </div>

      {actionError && (
        <div className="alert alert-danger mb-4 rounded-xl d-flex justify-content-between align-items-center" role="alert">
          <div className="text-sm">{actionError}</div>
          <button type="button" className="btn-close" aria-label="Cerrar" onClick={() => setActionError(null)} />
        </div>
      )}

      {/* CONTENEDOR PRINCIPAL DE 2 COLUMNAS DE ALTURA EXACTAMENTE IGUALADA */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* COLUMNA IZQUIERDA: DATOS BÁSICOS DEL PACIENTE + DOCUMENTO FUENTE */}
        <div className="col-12 lg:col-span-6 flex flex-col gap-4 lg:h-[840px]">
          {/* Tarjeta 1: Datos extraídos (Básicos) */}
          <div className="bg-white rounded-3xl p-4 sm:p-5 border border-slate-200/90 shadow-xs shrink-0">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-bold text-sm sm:text-base text-slate-900 mb-0.5">Datos extraídos</h3>
                <p className="text-xs text-slate-400 mb-0">Información básica del paciente</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 shrink-0">
                <LuUser size={15} />
              </div>
            </div>

            {/* Subsección: Datos del paciente */}
            <div className="mb-3">
              <span className="block text-xs font-semibold text-[#4338ca] tracking-wide mb-1.5">
                Datos del paciente
              </span>
              <div className="space-y-2">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-500 mb-0.5">Nombre</label>
                  <input
                    type="text"
                    name="pacienteNombre"
                    value={formData.pacienteNombre}
                    onChange={handleChange}
                    className="w-full bg-[#f8fafc] border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:border-indigo-500 outline-none transition-colors"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-500 mb-0.5">Edad</label>
                    <input
                      type="text"
                      name="pacienteEdad"
                      value={formData.pacienteEdad}
                      onChange={handleChange}
                      className="w-full bg-[#f8fafc] border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:border-indigo-500 outline-none transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-500 mb-0.5">DNI / Documento</label>
                    <input
                      type="text"
                      name="pacienteDni"
                      value={formData.pacienteDni}
                      onChange={handleChange}
                      className="w-full bg-[#f8fafc] border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:border-indigo-500 outline-none transition-colors"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Subsección: Datos del médico solicitante */}
            <div>
              <span className="block text-xs font-semibold text-[#4338ca] tracking-wide mb-1.5">
                Datos del médico solicitante
              </span>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-500 mb-0.5">Nombre</label>
                  <input
                    type="text"
                    name="medicoNombre"
                    value={formData.medicoNombre}
                    onChange={handleChange}
                    className="w-full bg-[#f8fafc] border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:border-indigo-500 outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-slate-500 mb-0.5">Matrícula</label>
                  <input
                    type="text"
                    name="medicoCmp"
                    value={formData.medicoCmp}
                    onChange={handleChange}
                    className="w-full bg-[#f8fafc] border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:bg-white focus:border-indigo-500 outline-none transition-colors"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* DOCUMENTO FUENTE: VISOR PDF DE ALTURA COMPARTIDA */}
          <div className="flex-1 min-h-0 flex flex-col">
            <span className="text-[11px] font-bold tracking-wider text-slate-400 uppercase mb-1 px-1">
              DOCUMENTO FUENTE
            </span>
            <div className="flex-1 min-h-[360px] bg-white rounded-3xl border border-slate-200/90 shadow-xs overflow-hidden flex flex-col">
              <DocumentViewer
                fileName={doc.nombre_archivo}
                fileUrl={doc.url_archivo}
                minHeight="100%"
              />
            </div>
          </div>
        </div>

        {/* COLUMNA DERECHA: REPORTE DE TRIAJE CON SCROLL INTERNO EQUILIBRADO */}
        <div className="col-12 lg:col-span-6 flex flex-col lg:h-[840px] bg-white rounded-3xl border border-slate-200/90 shadow-xs p-4 sm:p-6">
          {/* Cabecera del Reporte */}
          <div className="shrink-0 mb-3 flex items-start justify-between">
            <div>
              <h3 className="font-bold text-base sm:text-lg text-slate-900 mb-0.5">Reporte de triaje</h3>
              <p className="text-xs text-slate-500 mb-0">
                Corrija o confirme los datos detectados por el agente de MediFlow
              </p>
            </div>
            <div className="w-8 h-8 rounded-full bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-500 shrink-0">
              <LuHeart size={15} />
            </div>
          </div>

          {/* CUERPO DESPLAZABLE INTERNAMENTE (SIN ESPACIO EN BLANCO EXTERIOR) */}
          <div
            className="flex-1 min-h-0 overflow-y-auto pr-1.5 space-y-3"
            style={{ scrollbarWidth: "thin" }}
          >
            {/* SECCIÓN 1: CLASIFICACIÓN */}
            <div className="border border-slate-200/80 rounded-2xl p-3 sm:p-3.5 bg-slate-50/40">
              <button
                type="button"
                onClick={() => toggleSection("clasificacion")}
                className="w-full flex items-center justify-between text-xs font-bold text-slate-800 bg-transparent border-0 cursor-pointer p-0 mb-2.5"
              >
                <div className="flex items-center gap-1.5 text-slate-800">
                  <span>Clasificación</span>
                </div>
                {openSections.clasificacion ? <LuChevronUp size={16} /> : <LuChevronDown size={16} />}
              </button>

              {openSections.clasificacion && (
                <div className="space-y-2.5 pt-1">
                  <div>
                    <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-500 mb-0.5">
                      <LuFileText size={12} className="text-slate-400" /> Tipo de documento
                    </label>
                    <select
                      name="tipoDocumento"
                      value={formData.tipoDocumento}
                      onChange={handleChange}
                      className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:border-indigo-500 outline-none"
                    >
                      {CLINICAL_DOCUMENT_TYPES.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-500 mb-0.5">
                      <LuZap size={12} className="text-slate-400" /> Especialidad
                    </label>
                    <input
                      type="text"
                      name="especialidad"
                      value={formData.especialidad}
                      onChange={handleChange}
                      placeholder="Ej.: Radiología / Neuropatología"
                      className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:border-indigo-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-500 mb-0.5">
                      <LuCircleAlert size={12} className="text-rose-500" /> Nivel de prioridad
                    </label>
                    <select
                      name="prioridad"
                      value={formData.prioridad}
                      onChange={handleChange}
                      className={`w-full bg-white border rounded-xl px-3 py-1.5 text-xs font-bold outline-none ${
                        formData.prioridad === "URGENTE"
                          ? "border-rose-300 text-rose-600"
                          : formData.prioridad === "PRIORITARIO"
                          ? "border-amber-300 text-amber-700"
                          : "border-slate-200 text-slate-800"
                      }`}
                    >
                      <option value="NORMAL">NORMAL</option>
                      <option value="PRIORITARIO">PRIORITARIO</option>
                      <option value="URGENTE">URGENTE</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-500 mb-0.5">
                        <LuCheck size={12} className="text-emerald-500" /> Confianza de clasificación
                      </label>
                      <input
                        type="text"
                        value={formData.confianzaClasificacion}
                        readOnly
                        className="w-full bg-slate-100 border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-700 font-semibold cursor-not-allowed"
                      />
                    </div>
                    <div>
                      <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-500 mb-0.5">
                        <LuLock size={12} className="text-slate-400" /> Formato del archivo
                      </label>
                      <div className="relative">
                        <input
                          type="text"
                          value={formData.formatoArchivo}
                          readOnly
                          className="w-full bg-slate-100 border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-700 font-semibold cursor-not-allowed pr-8"
                        />
                        <LuLock size={13} className="absolute right-2.5 top-2 text-slate-400" />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* SECCIÓN 2: DATOS EXTRAÍDOS */}
            <div className="border border-slate-200/80 rounded-2xl p-3 sm:p-3.5 bg-slate-50/40">
              <button
                type="button"
                onClick={() => toggleSection("datosExtraidos")}
                className="w-full flex items-center justify-between text-xs font-bold text-slate-800 bg-transparent border-0 cursor-pointer p-0 mb-2.5"
              >
                <div className="flex items-center gap-1.5 text-slate-800">
                  <span>Datos extraídos</span>
                </div>
                {openSections.datosExtraidos ? <LuChevronUp size={16} /> : <LuChevronDown size={16} />}
              </button>

              {openSections.datosExtraidos && (
                <div className="space-y-2.5 pt-1">
                  <div>
                    <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-500 mb-0.5">
                      <LuStethoscope size={12} className="text-slate-400" /> Estudio realizado
                    </label>
                    <input
                      type="text"
                      name="estudioRealizado"
                      value={formData.estudioRealizado}
                      onChange={handleChange}
                      placeholder="Ej.: Tomografía de Tórax con contraste"
                      className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:border-indigo-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-500 mb-0.5">
                      <LuFilePen size={12} className="text-slate-400" /> Diagnóstico principal
                    </label>
                    <input
                      type="text"
                      name="diagnostico"
                      value={formData.diagnostico}
                      onChange={handleChange}
                      placeholder="Ej.: Tromboembolismo Pulmonar Agudo (TEP)"
                      className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:border-indigo-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-500 mb-0.5">
                      <LuZap size={12} className="text-slate-400" /> CIE-10 sugerido
                    </label>
                    <input
                      type="text"
                      name="cie10"
                      value={formData.cie10}
                      onChange={handleChange}
                      placeholder="Ej.: I26.9"
                      className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:border-indigo-500 outline-none"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* SECCIÓN 3: DECISIÓN DE ENRUTAMIENTO */}
            <div className="border border-slate-200/80 rounded-2xl p-3 sm:p-3.5 bg-slate-50/40">
              <button
                type="button"
                onClick={() => toggleSection("enrutamiento")}
                className="w-full flex items-center justify-between text-xs font-bold text-slate-800 bg-transparent border-0 cursor-pointer p-0 mb-2.5"
              >
                <div className="flex items-center gap-1.5 text-slate-800">
                  <span>Decisión de enrutamiento</span>
                </div>
                {openSections.enrutamiento ? <LuChevronUp size={16} /> : <LuChevronDown size={16} />}
              </button>

              {openSections.enrutamiento && (
                <div className="space-y-2.5 pt-1">
                  <div>
                    <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-500 mb-0.5">
                      <LuUsers size={12} className="text-slate-400" /> Destino principal
                    </label>
                    <input
                      type="text"
                      name="destino"
                      value={formData.destino}
                      onChange={handleChange}
                      placeholder="Ej.: Cola de Emergencia Médica"
                      className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:border-indigo-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="flex items-center gap-1 text-[11px] font-semibold text-slate-500 mb-0.5">
                      <LuFileText size={12} className="text-slate-400" /> Justificación de enrutamiento
                    </label>
                    <textarea
                      name="justificacionEnrutamiento"
                      value={formData.justificacionEnrutamiento}
                      onChange={handleChange}
                      rows={2}
                      placeholder="Ej.: Hallazgo crítico de alta gravedad..."
                      className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:border-indigo-500 outline-none resize-none"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* SECCIÓN 4: NOTIFICACIÓN GENERADA */}
            <div className="border border-slate-200/80 rounded-2xl p-3 sm:p-3.5 bg-slate-50/40">
              <button
                type="button"
                onClick={() => toggleSection("notificacion")}
                className="w-full flex items-center justify-between text-xs font-bold text-slate-800 bg-transparent border-0 cursor-pointer p-0 mb-2.5"
              >
                <div className="flex items-center gap-1.5 text-slate-800">
                  <LuBell size={13} className="text-slate-500" />
                  <span>Notificación generada</span>
                </div>
                {openSections.notificacion ? <LuChevronUp size={16} /> : <LuChevronDown size={16} />}
              </button>

              {openSections.notificacion && (
                <div className="space-y-2.5 pt-1">
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-500 mb-0.5">Canal</label>
                    <input
                      type="text"
                      name="canalNotificacion"
                      value={formData.canalNotificacion}
                      onChange={handleChange}
                      placeholder="Ej.: Alerta de Guardia Médica"
                      className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:border-indigo-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-slate-500 mb-0.5">Mensaje</label>
                    <textarea
                      name="mensajeNotificacion"
                      value={formData.mensajeNotificacion}
                      onChange={handleChange}
                      rows={2}
                      placeholder="Ej.: ALERTA URGENTE: Informe crítico..."
                      className="w-full bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:border-indigo-500 outline-none resize-none"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* BARRA INFERIOR DE ACCIONES FIJAS */}
          <div className="shrink-0 pt-4 mt-3 border-t border-slate-100 flex items-center justify-between gap-3">
            <button
              type="button"
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-xs sm:text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50 transition-colors shadow-2xs cursor-pointer"
              onClick={handleOpenRechazar}
              disabled={actionLoading}
            >
              Rechazar Documento
            </button>

            <button
              type="button"
              className="px-5 py-2.5 rounded-xl bg-[#204A79] hover:bg-[#153457] text-xs sm:text-sm font-semibold text-white transition-colors shadow-xs flex items-center gap-1.5 cursor-pointer"
              onClick={handleOpenConfirmar}
              disabled={actionLoading}
            >
              <span>Confirmar y Enviar</span>
              <LuChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      <ConfirmModal
        show={modalConfig.show}
        title={modalConfig.title}
        message={modalConfig.message}
        variant={modalConfig.variant}
        onConfirm={handleConfirmAction}
        onCancel={() => setModalConfig((prev) => ({ ...prev, show: false }))}
        loading={actionLoading}
      />
    </div>
  );
};

export default AuditDetail;
