export type ConfidenceTierKey = 'CRITICAL' | 'LOW' | 'MEDIUM' | 'HIGH'

export interface AuditConfidenceInfo {
  percentage: number
  tier: ConfidenceTierKey
  label: string
  badgeClass: string
  dotClass: string
  colorVar: string
  hexColor: string
}

export interface AuditPaginationState {
  currentPage: number
  itemsPerPage: number
  totalPages: number
  totalItems: number
}

