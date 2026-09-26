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

const Dashboard = () => {
  const [stats, setStats] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = useCallback(async () => {
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
  }, []);

  useEffect(() => {
    queueMicrotask(() => void loadDashboardData());
  }, [loadDashboardData]);

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
