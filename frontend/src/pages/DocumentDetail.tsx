import { useCallback, useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import DocumentViewer from "../components/documents/DocumentViewer";
import ExtractedData from "../components/triage/ExtractedData";
import ConfidenceIndicator from "../components/triage/ConfidenceIndicator";
import PriorityBadge from "../components/triage/PriorityBadge";
import RoutingDecision from "../components/triage/RoutingDecision";
import { normalizeClinicalDocumentType } from "../constants/clinicalDocumentTypes";
import DocumentStatusBadge from "../components/documents/DocumentStatusBadge";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import PageHeader from "../components/common/PageHeader";
import { documentsApi } from "../api/documentsApi";
import { formatDate } from "../utils/formatDate";
import { FaArrowLeft, FaFileAlt, FaFileCode, FaUserCheck, FaCopy, FaCheck } from "react-icons/fa";
import type { ClinicalDocument } from '../types/documents'

const DocumentDetail = () => {
  const { id } = useParams();
  const [doc, setDoc] = useState<ClinicalDocument | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'extracted' | 'ocr'>("extracted");
  const [copied, setCopied] = useState(false);

  const fetchDocument = useCallback(async () => {
    if (!id) {
      setError('El identificador del documento es obligatorio.')
      setLoading(false)
      return
    }
    setLoading(true);
    setError(null);
    try {
      const data = await documentsApi.obtenerDocumentoPorId(id);
      setDoc(data);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : `No se pudo encontrar el documento ${id}`);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    queueMicrotask(() => void fetchDocument());
  }, [fetchDocument]);

  const handleCopyOcr = () => {
    if (doc?.texto_ocr) {
      navigator.clipboard.writeText(doc.texto_ocr);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) return <Loading message={`Cargando resultado del triaje para ${id}...`} />;
  if (error) return <ErrorMessage title="Error de Carga" message={error} onRetry={fetchDocument} />;
  if (!doc) return <ErrorMessage title="No encontrado" message="El documento solicitado no existe." />;

  const requiereAuditoria = doc.estado === "AUDITORIA" || doc.decision_enrutamiento?.requiere_auditoria;

  return (
    <div className="clinical-page document-detail-page">
      <PageHeader
        eyebrow="Resultado de triaje"
        title={doc.documento_id}
        description={`Recepción: ${formatDate(doc.fecha_creacion)}`}
        icon={<FaFileAlt />}
        actions={(
          <>
          <Link to="/documentos" className="btn btn-outline-secondary">
            <FaArrowLeft className="me-2" /> Historial
          </Link>
          <PriorityBadge priority={doc.clasificacion?.prioridad} />
          <DocumentStatusBadge estado={doc.estado} />
          {requiereAuditoria && (
            <Link to={`/auditoria/${doc.documento_id}`} className="btn btn-warning text-dark px-3">
              <FaUserCheck className="me-2" /> Revisar caso
            </Link>
          )}
          </>
        )}
      />

      {/* Main split grid layout */}
      <div className="row g-4">
        {/* Left Column: Document Original */}
        <div className="col-12 col-lg-5">
          <DocumentViewer fileName={doc.nombre_archivo} fileUrl={doc.url_archivo} />
        </div>

        {/* Right Column: Extracted Data & OCR Tabs */}
        <div className="col-12 col-lg-7">
          <div className="card border-0 shadow-sm mb-4">
            <div className="card-header bg-white border-bottom py-3 px-3">
              <div className="row align-items-center">
                <div className="col-md-7 mb-2 mb-md-0">
                  <ConfidenceIndicator score={doc.clasificacion?.score_confianza} />
                </div>
                <div className="col-md-5 text-md-end">
                  <span className="text-muted small d-block">Canal: <strong className="text-dark">{doc.canal_origen || "General"}</strong></span>
                  <span className="text-muted small">Tipo: <strong className="text-dark">{normalizeClinicalDocumentType(doc.clasificacion?.tipo_documento)}</strong></span>
                </div>
              </div>
            </div>

            <div className="card-body p-0">
              {/* Tab headers */}
              <ul className="nav nav-tabs nav-fill bg-light px-3 pt-2 border-bottom">
                <li className="nav-item">
                  <button
                    className={`nav-link fw-bold ${activeTab === "extracted" ? "active text-primary bg-white" : "text-secondary"}`}
                    onClick={() => setActiveTab("extracted")}
                  >
                    <FaFileAlt className="me-2" /> Datos extraídos
                  </button>
                </li>
                <li className="nav-item">
                  <button
                    className={`nav-link fw-bold ${activeTab === "ocr" ? "active text-primary bg-white" : "text-secondary"}`}
                    onClick={() => setActiveTab("ocr")}
                  >
                    <FaFileCode className="me-2" /> Texto detectado (OCR)
                  </button>
                </li>
              </ul>

              <div className="p-3">
                {activeTab === "extracted" ? (
                  <ExtractedData data={doc.datos_extraidos} clasificacion={doc.clasificacion} />
                ) : (
                  <div>
                    <div className="d-flex justify-content-between align-items-center mb-2 px-1">
                      <span className="text-muted small fw-semibold">Transcripción OCR cruda del motor de extracción:</span>
                      <button
                        className="btn btn-sm btn-outline-secondary py-1 px-2.5 rounded-pill"
                        onClick={handleCopyOcr}
                      >
                        {copied ? (
                          <span className="text-success fw-bold"><FaCheck className="me-1" /> Copiado</span>
                        ) : (
                          <>
                            <FaCopy className="me-1" /> Copiar Texto OCR
                          </>
                        )}
                      </button>
                    </div>
                    <div className="ocr-text-container bg-dark text-light p-3 rounded font-monospace small shadow-inner" style={{ minHeight: "360px", maxHeight: "480px", overflowY: "auto", whiteSpace: "pre-wrap" }}>
                      {doc.texto_ocr || "// No hay texto OCR disponible para este documento."}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Routing Decision Banner */}
          <RoutingDecision decision={doc.decision_enrutamiento} clasificacion={doc.clasificacion} />
        </div>
      </div>
    </div>
  );
};

export default DocumentDetail;
