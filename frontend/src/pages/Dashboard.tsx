import { useCallback, useState, useEffect } from "react";
import { Link } from "react-router-dom";
import StatsCard from "../components/dashboard/StatsCard";
import RecentDocuments from "../components/dashboard/RecentDocuments";
import Loading from "../components/common/Loading";
import ErrorMessage from "../components/common/ErrorMessage";
import PageHeader from "../components/common/PageHeader";
import { documentsApi, type DashboardSummary } from "../api/documentsApi";
import {
  FaFileUpload,
  FaCheckCircle,
  FaExclamationTriangle,
  FaUserClock,
  FaTimesCircle,
  FaChartLine
} from "react-icons/fa";

import { useAuth } from "../hooks/useAuth";
import logo from "../assets/login/logo.png";
import welcomeTeamImg from "../assets/welcome_team.jpg";

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = useCallback(async () => {
    if (user?.rol === 'PENDIENTE') {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await documentsApi.obtenerResumenDashboard();
      setStats(data);
    } catch {
      setError("No se pudo cargar el resumen del dashboard.");
    } finally {
      setLoading(false);
    }
  }, [user?.rol]);

  useEffect(() => {
    queueMicrotask(() => void loadDashboardData());
  }, [loadDashboardData]);

  if (user?.rol === "PENDIENTE") {
    return (
      <div
        className="clinical-page d-flex flex-column align-items-center justify-content-center text-center py-5 px-3"
        style={{ minHeight: "calc(100vh - 120px)" }}
      >
        <div style={{ maxWidth: "680px" }} className="d-flex flex-column align-items-center">
          <h1
            className="fw-bold display-5 mb-2"
            style={{ fontFamily: "'Quicksand', sans-serif", color: "#1f2041" }}
          >
            Bienvenido a
          </h1>
          <div className="my-2">
            <img
              src={logo}
              alt="MediFlow"
              className="img-fluid select-none"
              style={{ maxWidth: "240px", height: "auto" }}
            />
          </div>
          <div className="my-4 shadow-sm" style={{ maxWidth: "420px", overflow: "hidden", borderRadius: "24px" }}>
            <img
              src={welcomeTeamImg}
              alt="Equipo médico MediFlow"
              className="img-fluid select-none"
              style={{ borderRadius: "24px" }}
            />
          </div>
          <p
            className="fw-medium fs-5 mt-2"
            style={{ fontFamily: "'Montserrat', sans-serif", color: "#314b6e", maxWidth: "560px" }}
          >
            Tu solicitud de acceso ha sido enviada al administrador del sistema, por favor, espera a que sea confirmada para comenzar.
          </p>
        </div>
      </div>
    );
  }

  if (loading) return <Loading message="Cargando métricas del sistema MediFlow..." />;
  if (error) return <ErrorMessage title="Error al cargar Dashboard" message={error} onRetry={loadDashboardData} />;

  return (
    <div className="clinical-page dashboard-page">
      <PageHeader
        eyebrow="Operación clínica"
        title="Panel de triaje"
        description="Seguimiento de documentos procesados, casos urgentes y revisiones humanas pendientes."
        icon={<FaChartLine />}
        actions={(
          <Link to="/documentos/nuevo" className="btn btn-primary px-3">
            <FaFileUpload className="me-2" /> Cargar documento
          </Link>
        )}
      />

      {/* KPI Cards */}
      <div className="row g-3 mb-4">
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard
            title="Documentos Procesados"
            value={stats?.procesados ?? 0}
            icon={<FaCheckCircle size={28} />}
            variant="success"
            subtitle="Triados exitosamente"
          />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard
            title="Casos Urgentes"
            value={stats?.urgentes ?? 0}
            icon={<FaExclamationTriangle size={28} />}
            variant="danger"
            subtitle="Prioridad roja asignada"
          />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard
            title="Pendientes de Auditoría"
            value={stats?.auditoria ?? 0}
            icon={<FaUserClock size={28} />}
            variant="warning"
            subtitle="Confianza baja / ambiguos"
          />
        </div>
        <div className="col-12 col-sm-6 col-xl-3">
          <StatsCard
            title="Errores / Rechazados"
            value={stats?.errores ?? 0}
            icon={<FaTimesCircle size={28} />}
            variant="dark"
            subtitle="Ilegibles o rechazados"
          />
        </div>
      </div>

      <RecentDocuments documents={stats?.recientes || []} />
    </div>
  );
};

export default Dashboard;
