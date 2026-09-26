import { FaUser, FaUserMd, FaFileMedical, FaStethoscope, FaPills } from "react-icons/fa";
import type { ClinicalDocument } from "../../types/documents";
import { normalizeClinicalDocumentType } from "../../constants/clinicalDocumentTypes";

const sanitize = (value: unknown) => {
  if (value === null || value === undefined || value === "" || String(value).toLowerCase() === "nan") {
    return "No identificado";
  }
  return String(value);
};

interface ExtractedDataProps {
  data?: NonNullable<ClinicalDocument['datos_extraidos']>
  clasificacion?: NonNullable<ClinicalDocument['clasificacion']>
}

const ExtractedData = ({ data = {}, clasificacion = {} }: ExtractedDataProps) => {
  const paciente = data.paciente || {};
  const medico = data.medico || {};
  const medicamentos = Array.isArray(data.medicamentos) ? data.medicamentos : [];

  return (
    <div className="extracted-data-container">
      <div className="row g-3">
        {/* Paciente */}
        <div className="col-md-6">
          <div className="card h-100 border-0 bg-light shadow-sm">
            <div className="card-body">
              <h6 className="card-title text-primary fw-bold d-flex align-items-center mb-3">
                <FaUser className="me-2" /> Paciente
              </h6>
              <ul className="list-unstyled mb-0">
                <li className="mb-2">
                  <span className="text-muted small d-block">Nombre:</span>
                  <span className="fw-semibold text-dark">{sanitize(paciente.nombre)}</span>
                </li>
                <li className="mb-2">
                  <span className="text-muted small d-block">DNI / Identificación:</span>
                  <span className="fw-semibold text-dark">{sanitize(paciente.dni)}</span>
                </li>
                <li>
                  <span className="text-muted small d-block">Edad:</span>
                  <span className="fw-semibold text-dark">
                    {paciente.edad !== null && paciente.edad !== undefined ? `${paciente.edad} años` : "No identificado"}
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Médico */}
        <div className="col-md-6">
          <div className="card h-100 border-0 bg-light shadow-sm">
            <div className="card-body">
              <h6 className="card-title text-primary fw-bold d-flex align-items-center mb-3">
                <FaUserMd className="me-2" /> Médico Tratante
              </h6>
              <ul className="list-unstyled mb-0">
                <li className="mb-2">
                  <span className="text-muted small d-block">Nombre:</span>
                  <span className="fw-semibold text-dark">{sanitize(medico.nombre)}</span>
                </li>
                <li>
                  <span className="text-muted small d-block">Colegiatura / CMP:</span>
                  <span className="fw-semibold text-dark">{sanitize(medico.cmp)}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Clasificación del Documento */}
        <div className="col-md-6">
          <div className="card h-100 border-0 bg-light shadow-sm">
            <div className="card-body">
              <h6 className="card-title text-primary fw-bold d-flex align-items-center mb-3">
                <FaFileMedical className="me-2" /> Documento
              </h6>
              <ul className="list-unstyled mb-0">
                <li className="mb-2">
                  <span className="text-muted small d-block">Tipo de Documento:</span>
                  <span className="badge bg-primary text-white fs-7">{normalizeClinicalDocumentType(clasificacion.tipo_documento)}</span>
                </li>
                <li>
                  <span className="text-muted small d-block">Especialidad:</span>
                  <span className="fw-semibold text-dark">{sanitize(clasificacion.especialidad)}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Información Clínica */}
        <div className="col-md-6">
          <div className="card h-100 border-0 bg-light shadow-sm">
            <div className="card-body">
              <h6 className="card-title text-primary fw-bold d-flex align-items-center mb-3">
                <FaStethoscope className="me-2" /> Información Clínica
              </h6>
              <ul className="list-unstyled mb-0">
                <li className="mb-2">
                  <span className="text-muted small d-block">Diagnóstico:</span>
                  <span className="fw-bold text-dark">{sanitize(data.diagnostico)}</span>
                </li>
                <li className="mb-2">
                  <span className="text-muted small d-block">Código CIE-10:</span>
                  <span className="badge bg-secondary">{sanitize(data.cie10)}</span>
                </li>
                <li>
                  <span className="text-muted small d-block">Estudio Solicitado:</span>
                  <span className="fw-semibold text-dark">{sanitize(data.estudio_solicitado)}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Medicamentos Prescritos */}
        <div className="col-12">
          <div className="card border-0 bg-light shadow-sm">
            <div className="card-body">
              <h6 className="card-title text-primary fw-bold d-flex align-items-center mb-3">
                <FaPills className="me-2" /> Medicamentos Prescritos
              </h6>
              {medicamentos.length === 0 ? (
                <p className="text-muted mb-0 small fst-italic">No identificado / No aplica</p>
              ) : (
                <div className="table-responsive">
                  <table className="table table-sm table-hover bg-white rounded mb-0 align-middle">
                    <thead className="table-light">
                      <tr>
                        <th>Medicamento</th>
                        <th>Dosis</th>
                        <th>Frecuencia</th>
                      </tr>
                    </thead>
                    <tbody>
                      {medicamentos.map((med, idx) => (
                        <tr key={idx}>
                          <td className="fw-semibold">{sanitize(med.nombre)}</td>
                          <td>{sanitize(med.dosis)}</td>
                          <td>{sanitize(med.frecuencia)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExtractedData;
