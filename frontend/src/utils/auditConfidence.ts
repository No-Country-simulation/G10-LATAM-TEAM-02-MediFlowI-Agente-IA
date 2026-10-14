import type { AuditConfidenceInfo } from "../types/auditView.types";

/**
 * Calcula el rango y formato de confianza clínica para la bandeja de auditoría:
 * - Menor al 25%: Rojo (var(--error) / #F72C2C)
 * - Entre 25% y 50%: Anaranjado (var(--orange) / #F59E0B)
 * - Entre 50% y 75%: Amarillo (var(--warning) / #EAB308)
 * - Superior al 75%: Verde (var(--green) / #10B981)
 */
export function getAuditConfidenceBadge(score?: number | string | null): AuditConfidenceInfo {
  const numericScore = Number(score);

  if (score === null || score === undefined || Number.isNaN(numericScore)) {
    return {
      percentage: 0,
      tier: "CRITICAL",
      label: "< 25%",
      badgeClass: "bg-red-50 text-[#F72C2C]",
      dotClass: "bg-[#F72C2C]",
      colorVar: "var(--error)",
      hexColor: "#F72C2C",
    };
  }

  const percentage = Math.round(numericScore > 0 && numericScore <= 1 ? numericScore * 100 : numericScore);

  if (percentage < 25) {
    return {
      percentage,
      tier: "CRITICAL",
      label: "< 25%",
      badgeClass: "bg-red-50 text-[#F72C2C]",
      dotClass: "bg-[#F72C2C]",
      colorVar: "var(--error)",
      hexColor: "#F72C2C",
    };
  }

  if (percentage <= 50) {
    return {
      percentage,
      tier: "LOW",
      label: "25% - 50%",
      badgeClass: "bg-amber-50 text-[#F59E0B]",
      dotClass: "bg-[#F59E0B]",
      colorVar: "var(--orange)",
      hexColor: "#F59E0B",
    };
  }

  if (percentage <= 75) {
    return {
      percentage,
      tier: "MEDIUM",
      label: "50% - 75%",
      badgeClass: "bg-yellow-50 text-yellow-700",
      dotClass: "bg-[#EAB308]",
      colorVar: "var(--warning)",
      hexColor: "#EAB308",
    };
  }

  return {
    percentage,
    tier: "HIGH",
    label: "> 75%",
    badgeClass: "bg-emerald-50 text-[#10B981]",
    dotClass: "bg-[#10B981]",
    colorVar: "var(--green)",
    hexColor: "#10B981",
  };
}
