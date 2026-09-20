import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import DocumentUploader from "../components/documents/DocumentUploader";
import { documentsApi } from "../api/documentsApi";
import { FaCheckCircle, FaSpinner } from "react-icons/fa";

const PROCESSING_STEPS = [
  "Documento recibido",
  "Documento almacenado",
  "Texto extraído (OCR)",
  "Datos analizados con IA",
  "Clasificación realizada",
  "Triaje completado"
];

const NewDocument = () => {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [error, setError] = useState(null);

  const handleProcess = async (file, canalOrigen) => {
    setIsProcessing(true);
    setError(null);
    setCurrentStep(0);

    // Simulate animated stepper progression for UI demo
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < PROCESSING_STEPS.length - 1) {
          return prev + 1;
        }
        clearInterval(stepInterval);
        return prev;
      });
    }, 700);

    try {
      const result = await documentsApi.procesarDocumento(file, canalOrigen);
      
      // Wait for animation to finish step
      setTimeout(() => {
        clearInterval(stepInterval);
        setCurrentStep(PROCESSING_STEPS.length);
        
        setTimeout(() => {
          setIsProcessing(false);
          const docId = result?.documento_id || result?.id || "DOC-001";
          navigate(`/documentos/${docId}`);
        }, 800);
      }, 4200);

    } catch (err) {
      clearInterval(stepInterval);
      setIsProcessing(false);
      setError(err.message || "Ocurrió un error al procesar el documento");
    }
  };

  const handleCancel = () => {
    navigate("/dashboard");
  };

  return (
    <div className="new-document-page">
      <div className="row justify-content-center">
        <div className="col-12 col-lg-8">
          <div className="mb-4">
            <h3 className="fw-bold text-dark mb-1">Cargar Nuevo Documento Clínico</h3>
            <p className="text-muted small">Ingesta de recetas, órdenes o informes en PDF o imagen para procesamiento en tiempo real</p>
          </div>

          {error && (
            <div className="alert alert-danger alert-dismissible fade show" role="alert">
              {error}
              <button type="button" className="btn-close" onClick={() => setError(null)}></button>
            </div>
          )}

          <DocumentUploader onProcess={handleProcess} onCancel={handleCancel} isProcessing={isProcessing} />

          {/* Processing Stepper Overlay / Progress */}
          {isProcessing && (
            <div className="card shadow-sm border-primary mt-4 bg-primary bg-opacity-10">
              <div className="card-body p-4">
                <div className="d-flex align-items-center mb-3">
                  <FaSpinner className="spinner-border text-primary me-3 flex-shrink-0" style={{ width: "2rem", height: "2rem" }} />
                  <div>
                    <h5 className="fw-bold text-primary mb-0">Procesando documento...</h5>
                    <span className="text-muted small">Ejecutando OCR, análisis clínico y reglas de enrutamiento</span>
                  </div>
                </div>

                <div className="progress mb-4" style={{ height: "10px" }}>
                  <div
                    className="progress-bar progress-bar-striped progress-bar-animated bg-primary"
                    role="progressbar"
                    style={{ width: `${Math.min(100, Math.round(((currentStep + 1) / PROCESSING_STEPS.length) * 100))}%` }}
                  ></div>
                </div>

                <div className="list-group border-0">
                  {PROCESSING_STEPS.map((step, idx) => {
                    const isCompleted = idx <= currentStep;
                    const isCurrent = idx === currentStep;

                    return (
                      <div
                        key={step}
                        className={`list-group-item bg-transparent border-0 px-0 py-1.5 d-flex align-items-center ${
                          isCompleted ? "text-dark font-medium" : "text-muted opacity-50"
                        }`}
                      >
                        {isCompleted ? (
                          <FaCheckCircle className="text-success me-2 fs-5" />
                        ) : isCurrent ? (
                          <span className="spinner-border spinner-border-sm text-primary me-2" role="status"></span>
                        ) : (
                          <span className="badge rounded-circle bg-secondary me-2 px-2 py-1">{idx + 1}</span>
                        )}
                        <span>{step}</span>
                      </div>
                    );
                  })}
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
