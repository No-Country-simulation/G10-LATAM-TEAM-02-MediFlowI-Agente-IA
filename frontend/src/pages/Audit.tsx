import React, { useCallback, useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEye, faTriangleExclamation } from "@fortawesome/free-solid-svg-icons";
import Loading from "../components/common/Loading";
import EmptyState from "../components/common/EmptyState";
import ErrorMessage from "../components/common/ErrorMessage";
import { auditApi } from "../api/auditApi";
import { formatDateShort } from "../utils/formatDate";
import { getAuditConfidenceBadge } from "../utils/auditConfidence";
import { useAuth } from "../hooks/useAuth";
import { NAV_PILLS, type TriageModalTab } from "../types/triageModal.types";
import cn from "../utils/cn";
import type { ClinicalDocument } from "../types/documents";

const Audit: React.FC = () => {
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();

  const [audits, setAudits] = useState<ClinicalDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Navegación por píldoras
  const [activePill, setActivePill] = useState<TriageModalTab>("solicitudes");

  // Paginación visual
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  // Control RBAC de píldoras
  const userRole = currentUser?.rol || "OPERADOR";
  const visiblePills = NAV_PILLS.filter((pill) =>
    pill.rolesPermitidos.includes(
      userRole as "ADMINISTRADOR" | "OPERADOR" | "AUDITOR" | "SUPERVISOR"
    )
  );

  const handlePillClick = (pillId: TriageModalTab, route: string) => {
    setActivePill(pillId);
    if (pillId === "enrutamiento") {
      navigate("/documentos/nuevo");
    } else if (pillId === "historial") {
      navigate("/documentos");
    } else if (route && route !== "/auditoria") {
      navigate(route);
    }
  };

  const fetchAudits = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await auditApi.obtenerAuditorias();
      setAudits(data);
    } catch {
      setError("Error al cargar los casos de auditoría pendiente.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchAudits();
  }, [fetchAudits]);

  if (loading) return <Loading message="Cargando casos de auditoría humana..." />;
  if (error) return <ErrorMessage title="Error de Auditoría" message={error} onRetry={fetchAudits} />;

  const totalPages = Math.max(1, Math.ceil(audits.length / itemsPerPage));
  const paginatedAudits = audits.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  return (
    <div className="w-full flex flex-col items-center min-h-[calc(100vh-80px)] py-4 sm:py-6 px-4 md:px-8 gap-2 sm:gap-4 relative z-10">
      {/* ── BARRA SUPERIOR DE PÍLDORAS (RBAC) ── */}
      <nav
        aria-label="Navegación de consola"
        className={cn(
          "p-1 mb-6 sm:mb-8",
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
                isActive
                  ? "bg-slate-100/90 text-[#1f2041] shadow-2xs font-bold"
                  : "bg-transparent text-slate-500 hover:text-slate-800"
              )}
            >
              {pill.label}
            </button>
          );
        })}
      </nav>

      {/* ── TÍTULO PRINCIPAL DE LA VISTA ── */}
      <header className="flex flex-col items-center text-center max-w-3xl mb-8">
        <h1
          className="text-3xl sm:text-4xl md:text-[40px] font-bold text-[#1f2041] tracking-tight mb-2"
          style={{ fontFamily: '"Montserrat", sans-serif' }}
        >
          Solicitudes de auditoría clínica
        </h1>
      </header>

      {/* ── TARJETA BLANCA PRINCIPAL CON TABLA ── */}
      <section className="w-full max-w-6xl bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-200/70 transition-all flex flex-col gap-6">
        {!audits.length ? (
          <EmptyState
            title="No hay documentos pendientes de auditoría"
            message="Actualmente todos los documentos han sido triados automáticamente con alta confianza o ya han sido auditados."
          />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <caption className="sr-only">Documentos pendientes de auditoría clínica</caption>
                <thead>
                  <tr className="border-b border-slate-200/80">
                    <th scope="col" className="py-3.5 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      ID
                    </th>
                    <th scope="col" className="py-3.5 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Documento
                    </th>
                    <th scope="col" className="py-3.5 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Confianza
                    </th>
                    <th scope="col" className="py-3.5 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Motivo de Derivación
                    </th>
                    <th scope="col" className="py-3.5 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      Fecha
                    </th>
                    <th scope="col" className="py-3.5 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-center">
                      Visualizar
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {paginatedAudits.map((item) => {
                    const conf = getAuditConfidenceBadge(item.clasificacion?.score_confianza);
                    const motivo =
                      item.decision_enrutamiento?.motivo_auditoria ||
                      "Confianza baja o datos incompletos detectados";

                    return (
                      <tr
                        key={item.documento_id}
                        className="hover:bg-slate-50/70 transition-colors"
                      >
                        {/* 1. ID */}
                        <td className="py-4 px-4 text-sm font-bold text-[#2C5282] whitespace-nowrap">
                          {item.documento_id}
                        </td>

                        {/* 2. Documento */}
                        <td className="py-4 px-4 text-sm font-semibold text-slate-800 max-w-xs truncate" title={item.nombre_archivo}>
                          {item.nombre_archivo}
                        </td>

                        {/* 3. Confianza */}
                        <td className="py-4 px-4 whitespace-nowrap">
                          <span
                            data-testid="confidence-badge"
                            data-tier={conf.tier}
                            className={cn(
                              "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold shadow-2xs",
                              conf.badgeClass
                            )}
                            style={{ color: conf.colorVar }}
                          >
                            <span
                              className={cn("w-2 h-2 rounded-full flex-shrink-0", conf.dotClass)}
                              style={{ backgroundColor: conf.colorVar }}
                            />
                            <span>{conf.percentage}%</span>
                          </span>
                        </td>

                        {/* 4. Motivo de Derivación */}
                        <td className="py-4 px-4 text-xs text-slate-600 max-w-md">
                          <div className="flex items-center gap-1.5">
                            <FontAwesomeIcon
                              icon={faTriangleExclamation}
                              className="text-amber-500 flex-shrink-0 text-sm"
                            />
                            <span className="line-clamp-2">{motivo}</span>
                          </div>
                        </td>

                        {/* 5. Fecha */}
                        <td className="py-4 px-4 text-xs text-slate-400 whitespace-nowrap">
                          {formatDateShort(item.fecha_creacion)}
                        </td>

                        {/* 6. Acción / Visualizar */}
                        <td className="py-4 px-4 text-center whitespace-nowrap">
                          <Link
                            to={`/auditoria/${item.documento_id}`}
                            className={cn(
                              "inline-flex items-center justify-center gap-2 px-3.5 py-1.5",
                              "border border-slate-300 rounded-lg text-xs font-semibold no-underline",
                              "text-slate-700 bg-[#FFFFFF] transition-all duration-200 cursor-pointer",
                              "hover:bg-[var(--primary)] hover:border-[var(--primary)] hover:text-white group shadow-2xs"
                            )}
                          >
                            <FontAwesomeIcon
                              icon={faEye}
                              className="text-slate-600 group-hover:text-white transition-colors"
                            />
                            <span>Revisar</span>
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* ── CONTROL DE PAGINACIÓN VISUAL ── */}
            <div className="flex items-center justify-center gap-2 pt-4 border-t border-slate-100">
              {Array.from({ length: totalPages }, (_, idx) => {
                const pageNumber = idx + 1;
                const formattedNumber = String(pageNumber).padStart(2, "0");
                const isCurrent = currentPage === pageNumber;
                return (
                  <button
                    key={pageNumber}
                    type="button"
                    onClick={() => setCurrentPage(pageNumber)}
                    className={cn(
                      "text-xs font-medium px-2.5 py-1 rounded-md transition-all cursor-pointer border",
                      isCurrent
                        ? "border-slate-400 bg-slate-50 text-[#1f2041] font-bold shadow-2xs"
                        : "border-transparent text-slate-400 hover:text-slate-700"
                    )}
                  >
                    {formattedNumber}
                  </button>
                );
              })}
            </div>
          </>
        )}
      </section>
    </div>
  );
};

export default Audit;
