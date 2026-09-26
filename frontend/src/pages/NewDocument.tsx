import { useState } from "react";
import { useNavigate } from "react-router-dom";
import DocumentUploader from "../components/documents/DocumentUploader";
import { documentsApi } from "../api/documentsApi";
import { FaSpinner } from "react-icons/fa";
import { FaFileUpload } from "react-icons/fa";
import PageHeader from "../components/common/PageHeader";

const NewDocument = () => {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleProcess = async (file: File, canalOrigen: string) => {
    setIsProcessing(true);
    setError(null);

    try {
      const result = await documentsApi.procesarDocumento(file, canalOrigen);
      navigate(`/documentos/${result.documento_id}`);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Ocurrió un error al procesar el documento");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCancel = () => {
    navigate("/dashboard");
  };

  return (
    <div className="clinical-page new-document-page">
      <PageHeader
        eyebrow="Ingesta"
        title="Cargar documento clínico"
        description="Selecciona un PDF o una imagen y define su canal de origen para iniciar el triaje."
        icon={<FaFileUpload />}
      />
      <div className="row justify-content-center">
        <div className="col-12 col-xl-9">

          {error && (
            <div className="alert alert-danger alert-dismissible fade show" role="alert">
              {error}
              <button type="button" className="btn-close" onClick={() => setError(null)}></button>
            </div>
          )}

          <DocumentUploader onProcess={handleProcess} onCancel={handleCancel} isProcessing={isProcessing} />

          {/* Processing Stepper Overlay / Progress */}
          {isProcessing && (
            <div className="clinical-surface mt-4" role="status" aria-live="polite">
              <div className="card-body p-4">
                <div className="d-flex align-items-center mb-3">
                  <FaSpinner className="spinner-border text-primary me-3 flex-shrink-0" style={{ width: "2rem", height: "2rem" }} />
                  <div>
                    <h5 className="fw-bold text-primary mb-0">Procesando documento...</h5>
                    <span className="text-muted small">Ejecutando OCR, análisis clínico y reglas de enrutamiento</span>
                  </div>
                </div>

                <div className="progress" style={{ height: "10px" }} aria-label="Procesamiento en curso">
                  <div
                    className="progress-bar progress-bar-striped progress-bar-animated bg-primary"
                    role="progressbar"
                    style={{ width: "100%" }}
                    aria-valuetext="Procesamiento en curso"
                  ></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NewDocument;
