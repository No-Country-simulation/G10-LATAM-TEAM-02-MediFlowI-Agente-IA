import { useCallback, useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import DocumentViewer from "../components/documents/DocumentViewer";
import ConfirmModal from "../components/common/ConfirmModal";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import PageHeader from "../components/common/PageHeader";
import { auditApi } from "../api/auditApi";
import { CLINICAL_DOCUMENT_TYPES, normalizeClinicalDocumentType } from "../constants/clinicalDocumentTypes";
import { FaArrowLeft, FaCheck, FaTimes, FaSave, FaUserCheck } from "react-icons/fa";
import type { ChangeEvent } from 'react'
import type { ClinicalDocument } from '../types/documents'

type AuditAction = 'aprobar' | 'rechazar' | 'corregir' | null
type ModalVariant = 'primary' | 'danger' | 'warning' | 'success'
interface ModalConfig {
  show: boolean
  type: AuditAction
  title: string
  message: string
  variant: ModalVariant
}

const AuditDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [doc, setDoc] = useState<ClinicalDocument | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  // Form state for editing
  const [formData, setFormData] = useState({
    pacienteNombre: "",
    pacienteDni: "",
    pacienteEdad: "",
    medicoNombre: "",
    medicoCmp: "",
    tipoDocumento: "",
    especialidad: "",
    diagnostico: "",
    cie10: "",
    prioridad: "NORMAL",
    destino: "FARMACIA"
  });

  // Modal controls
  const [modalConfig, setModalConfig] = useState<ModalConfig>({
    show: false,
    type: null, // 'aprobar' | 'rechazar' | 'corregir'
    title: "",
    message: "",
    variant: "primary"
  });

  const loadAuditData = useCallback(async () => {
    if (!id) {
      setError('El identificador del documento es obligatorio.')
      setLoading(false)
      return
    }
    setLoading(true);
    setError(null);
    try {
      const data = await auditApi.obtenerAuditoriaPorId(id);
      setDoc(data);

      // Pre-fill form
      setFormData({
        pacienteNombre: data.datos_extraidos?.paciente?.nombre || "",
        pacienteDni: data.datos_extraidos?.paciente?.dni || "",
        pacienteEdad: data.datos_extraidos?.paciente?.edad?.toString() || "",
        medicoNombre: data.datos_extraidos?.medico?.nombre || "",
        medicoCmp: data.datos_extraidos?.medico?.cmp || "",
        tipoDocumento: normalizeClinicalDocumentType(data.clasificacion?.tipo_documento),
        especialidad: data.clasificacion?.especialidad || "Medicina General",
        diagnostico: data.datos_extraidos?.diagnostico || "",
        cie10: data.datos_extraidos?.cie10 || "",
        prioridad: data.clasificacion?.prioridad || "NORMAL",
        destino: data.decision_enrutamiento?.destino || "FARMACIA"
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

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleOpenAprobar = () => {
    setModalConfig({
      show: true,
      type: "aprobar",
      title: "Aprobar Documento",
      message: "¿Desea aprobar este documento con la información extraída actual?",
      variant: "success"
    });
  };

  const handleOpenRechazar = () => {
    setModalConfig({
      show: true,
      type: "rechazar",
      title: "Rechazar Documento",
      message: "¿Está seguro de rechazar este documento? El expediente pasará a estado RECHAZADO.",
      variant: "danger"
    });
  };

  const handleOpenCorregir = () => {
    setModalConfig({
      show: true,
      type: "corregir",
      title: "Guardar Correcciones",
      message: "¿Desea actualizar y validar los datos clínicos modificados?",
      variant: "primary"
    });
  };

  const handleConfirmAction = async () => {
    if (!id) return
    setActionLoading(true);
    setActionError(null);
    try {
      if (modalConfig.type === "aprobar") {
        await auditApi.aprobarAuditoria(id);
      } else if (modalConfig.type === "rechazar") {
        await auditApi.rechazarAuditoria(id);
      } else if (modalConfig.type === "corregir") {
        const payload = {
          paciente: {
            nombre: formData.pacienteNombre,
            dni: formData.pacienteDni,
            edad: formData.pacienteEdad
          },
          medico: {
            nombre: formData.medicoNombre,
            cmp: formData.medicoCmp
          },
          diagnostico: formData.diagnostico,
          cie10: formData.cie10,
          tipo_documento: formData.tipoDocumento,
          prioridad: formData.prioridad,
          destino: formData.destino
        };
        await auditApi.corregirAuditoria(id, payload);
      }

      setModalConfig((prev) => ({ ...prev, show: false }));
      navigate(`/documentos/${id}`);
    } catch (caughtError) {
      setModalConfig((prev) => ({ ...prev, show: false }));
      setActionError(caughtError instanceof Error ? caughtError.message : 'No se pudo completar la auditoría.');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <Loading message={`Cargando detalle de auditoría para ${id}...`} />;
  if (error) return <ErrorMessage title="Error al cargar auditoría" message={error} onRetry={loadAuditData} />;
  if (!doc) return <ErrorMessage title="No encontrado" message="El documento no existe." />;
  const confidence = doc.clasificacion?.score_confianza ?? 0

  return (
    <div className="clinical-page audit-detail-page">
      <PageHeader
        eyebrow="Revisión humana"
        title={doc.documento_id}
        description="Valida y corrige la información clínica antes de registrar una decisión."
        icon={<FaUserCheck />}
        actions={(
          <>
          <Link to="/auditoria" className="btn btn-outline-secondary">
            <FaArrowLeft className="me-2" /> Auditoría
          </Link>
          <span className="badge bg-warning text-dark px-3 py-2 fs-6">
            Confianza: {Math.round(confidence * (confidence <= 1 ? 100 : 1))}%
          </span>
          </>
        )}
      />

      {actionError && (
        <div className="alert alert-danger d-flex justify-content-between align-items-start" role="alert" aria-live="assertive">
          <div>
            <strong>No se pudo registrar la decisión.</strong>
            <div className="small mt-1">{actionError}</div>
          </div>
          <button type="button" className="btn-close" aria-label="Cerrar aviso" onClick={() => setActionError(null)} />
        </div>
      )}

      {/* Grid split */}
      <div className="row g-4">
        {/* Left Column: Original Document */}
        <div className="col-12 col-lg-5">
          <DocumentViewer fileName={doc.nombre_archivo} fileUrl={doc.url_archivo} />
        </div>

        {/* Right Column: Editable Fields */}
        <div className="col-12 col-lg-7">
          <div className="clinical-surface">
            <div className="clinical-surface__header">
              <div>
              <h2 className="clinical-surface__title">Datos extraídos</h2>
              <p className="clinical-surface__hint">Corrige o completa la información antes de aprobar.</p>
              </div>
            </div>

            <div className="card-body p-4">
              <form onSubmit={(e) => e.preventDefault()}>
                {/* Paciente Section */}
                <h6 className="fw-bold text-primary border-bottom pb-2 mb-3">Datos del Paciente</h6>
                <div className="row g-3 mb-4">
                  <div className="col-md-7">
                    <label className="form-label fw-semibold small">Nombre Completo</label>
                    <input
                      type="text"
                      className="form-control"
                      name="pacienteNombre"
                      value={formData.pacienteNombre}
                      onChange={handleChange}
                    />
                  </div>
                  <div className="col-md-5">
                    <label className="form-label fw-semibold small">DNI / Documento</label>
                    <input
                      type="text"
                      className="form-control"
                      name="pacienteDni"
                      value={formData.pacienteDni}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                {/* Médico Section */}
                <h6 className="fw-bold text-primary border-bottom pb-2 mb-3">Datos del Médico</h6>
                <div className="row g-3 mb-4">
                  <div className="col-md-7">
                    <label className="form-label fw-semibold small">Médico Tratante</label>
                    <input
                      type="text"
                      className="form-control"
                      name="medicoNombre"
                      value={formData.medicoNombre}
                      onChange={handleChange}
                    />
                  </div>
                  <div className="col-md-5">
                    <label className="form-label fw-semibold small">Colegiatura / CMP</label>
                    <input
                      type="text"
                      className="form-control"
                      name="medicoCmp"
                      value={formData.medicoCmp}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                {/* Información Clínica */}
                <h6 className="fw-bold text-primary border-bottom pb-2 mb-3">Diagnóstico y Clasificación</h6>
                <div className="row g-3 mb-4">
                  <div className="col-12">
                    <label className="form-label fw-semibold small">Tipo de Documento Clínico</label>
                    <select
                      className="form-select"
                      name="tipoDocumento"
                      value={formData.tipoDocumento}
                      onChange={handleChange}
                    >
                      {CLINICAL_DOCUMENT_TYPES.map((type) => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>
                  <div className="col-md-8">
                    <label className="form-label fw-semibold small">Diagnóstico Presuntivo</label>
                    <input
                      type="text"
                      className="form-control"
                      name="diagnostico"
                      value={formData.diagnostico}
                      onChange={handleChange}
                    />
                  </div>
                  <div className="col-md-4">
                    <label className="form-label fw-semibold small">Código CIE-10</label>
                    <input
                      type="text"
                      className="form-control"
                      name="cie10"
                      value={formData.cie10}
                      onChange={handleChange}
                    />
                  </div>
                  <div className="col-md-6">
                    <label className="form-label fw-semibold small">Prioridad del Triaje</label>
                    <select
                      className="form-select"
                      name="prioridad"
                      value={formData.prioridad}
                      onChange={handleChange}
                    >
                      <option value="NORMAL">NORMAL</option>
                      <option value="PRIORITARIO">PRIORITARIO</option>
                      <option value="URGENTE">URGENTE</option>
                    </select>
                  </div>
                  <div className="col-md-6">
                    <label className="form-label fw-semibold small">Destino de Enrutamiento</label>
                    <input
                      type="text"
                      className="form-control"
                      name="destino"
                      value={formData.destino}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                {/* Action Buttons Bar */}
                <div className="d-flex flex-wrap justify-content-between align-items-center pt-3 border-top gap-2">
                  <button
                    type="button"
                    className="btn btn-outline-danger fw-bold px-3"
                    onClick={handleOpenRechazar}
                    disabled={actionLoading}
                  >
                    <FaTimes className="me-1" /> RECHAZAR
                  </button>

                  <div className="d-flex gap-2">
                    <button
                      type="button"
                      className="btn btn-primary fw-bold px-3"
                      onClick={handleOpenCorregir}
                      disabled={actionLoading}
                    >
                      <FaSave className="me-1" /> GUARDAR CORRECCIÓN
                    </button>

                    <button
                      type="button"
                      className="btn btn-success fw-bold px-4"
                      onClick={handleOpenAprobar}
                      disabled={actionLoading}
                    >
                      <FaCheck className="me-1" /> APROBAR
                    </button>
                  </div>
                </div>
              </form>
            </div>
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
