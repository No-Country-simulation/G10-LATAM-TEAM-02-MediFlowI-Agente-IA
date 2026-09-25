
import type { ReactNode } from 'react'

interface StatsCardProps {
  title: string
  value: ReactNode
  icon: ReactNode
  variant?: string
  subtitle?: string
}

const StatsCard = ({ title, value, icon, variant = "primary", subtitle }: StatsCardProps) => {
  return (
    <div className="clinical-metric">
      <div className="d-flex align-items-center justify-content-between gap-3">
        <div>
          <span className="clinical-metric__label">{title}</span>
          <p className="clinical-metric__value">{value}</p>
          {subtitle && <span className="clinical-metric__subtitle">{subtitle}</span>}
        </div>
        <div className={`clinical-metric__icon bg-${variant} bg-opacity-10 text-${variant}`} aria-hidden="true">
          {icon}
        </div>
      </div>
    </div>
  );
};

export default StatsCard;
