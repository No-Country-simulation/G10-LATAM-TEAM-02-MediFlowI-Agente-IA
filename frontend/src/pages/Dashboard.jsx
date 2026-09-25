import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import StatsCard from "../components/dashboard/StatsCard";
import RecentDocuments from "../components/dashboard/RecentDocuments";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import { documentsApi } from "../api/documentsApi";
import {
  FaFileUpload,
  FaCheckCircle,
  FaExclamationTriangle,
  FaUserClock,
  FaTimesCircle,
  FaFileMedical,
  FaAmbulance,
  FaClipboardCheck
} from "react-icons/fa";

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await documentsApi.obtenerResumenDashboard();
      setStats(data);
    } catch (err) {
      setError("No se pudo cargar el resumen del dashboard.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (loading) return <Loading message="Cargando métricas del sistema MediFlow..." />;
  if (error) return <ErrorMessage title="Error al cargar Dashboard" message={error} onRetry={loadDashboardData} />;

  return (
    <div className="dashboard-page">
      {/* Page Title */}
      <div className="d-flex flex-wrap align-items-center justify-content-between mb-4">
        <div>
          <h3 className="fw-bold text-dark mb-1">Dashboard de Triaje Inteligente</h3>
          <p className="text-muted small mb-0">Resumen operativo y estado de la clasificación automática de documentos clínicos</p>
        </div>
        <Link to="/documentos/nuevo" className="btn btn-primary fw-bold px-3.5 py-2 shadow-sm">
          <FaFileUpload className="me-2" /> Nuevo Documento
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="row g-3 mb-4">
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard
            title="Documentos Procesados"
            value={stats?.procesados || 120}
            icon={<FaCheckCircle size={28} />}
            variant="success"
            subtitle="Triados exitosamente"
          />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard
            title="Casos Urgentes"
            value={stats?.urgentes || 8}
            icon={<FaExclamationTriangle size={28} />}
            variant="danger"
            subtitle="Prioridad roja asignada"
          />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard
            title="Pendientes de Auditoría"
            value={stats?.auditoria || 12}
            icon={<FaUserClock size={28} />}
            variant="warning"
            subtitle="Confianza baja / ambiguos"
          />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard
            title="Errores / Rechazados"
            value={stats?.errores || 2}
            icon={<FaTimesCircle size={28} />}
            variant="dark"
            subtitle="Ilegibles o rechazados"
          />
        </div>
      </div>

      {/* Demo Quick Flow Shortcuts */}
      <div className="card border-0 shadow-sm rounded-3 mb-4 bg-white">
        <div className="card-header bg-white py-3 border-bottom">
          <h6 className="fw-bold text-dark mb-0">Escenarios de Triaje Clínico Demostrables</h6>
        </div>
        <div className="card-body p-3">
          <div className="row g-3">
            <div className="col-12 col-md-4">
              <div className="p-3 border rounded-3 bg-light h-100 d-flex flex-column justify-content-between">
                <div>
                  <span className="badge bg-success mb-2">🟢 Flujo Estándar</span>
                  <h6 className="fw-bold mb-1 text-dark">Receta Médica Normal</h6>
                  <p className="small text-muted mb-2">Procesamiento automático de receta con 94% de confianza y destino a Farmacia.</p>
                </div>
                <Link to="/documentos/DOC-001" className="btn btn-outline-success btn-sm fw-bold mt-2">
                  <FaFileMedical className="me-1" /> Ver Caso DOC-001
                </Link>
              </div>
            </div>

            <div className="col-12 col-md-4">
              <div className="p-3 border rounded-3 bg-light h-100 d-flex flex-column justify-content-between">
                <div>
                  <span className="badge bg-danger mb-2">🔴 Flujo Urgente</span>
                  <h6 className="fw-bold mb-1 text-dark">Informe de Emergencia</h6>
                  <p className="small text-muted mb-2">Detección de prioridad URGENTE (98% confianza) derivado a Emergencia / Cardiología.</p>
                </div>
                <Link to="/documentos/DOC-002" className="btn btn-outline-danger btn-sm fw-bold mt-2">
                  <FaAmbulance className="me-1" /> Ver Caso DOC-002
                </Link>
              </div>
            </div>

            <div className="col-12 col-md-4">
              <div className="p-3 border rounded-3 bg-light h-100 d-flex flex-column justify-content-between">
                <div>
                  <span className="badge bg-warning text-dark mb-2">🟠 Caso Ambiguo</span>
                  <h6 className="fw-bold mb-1 text-dark">Orden Médica Ilegible</h6>
                  <p className="small text-muted mb-2">Confianza baja (52%) por datos ilegibles en DNI, derivado a revisión humana.</p>
                </div>
                <Link to="/auditoria/DOC-003" className="btn btn-outline-warning text-dark btn-sm fw-bold mt-2">
                  <FaClipboardCheck className="me-1" /> Auditar Caso DOC-003
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Documents Table */}
      <RecentDocuments documents={stats?.recientes || []} />
    </div>
  );
};

export default Dashboard;
