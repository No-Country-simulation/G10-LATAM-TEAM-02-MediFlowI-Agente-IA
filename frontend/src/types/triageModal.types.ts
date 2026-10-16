export type TriageModalTab = 'enrutamiento' | 'historial' | 'solicitudes'

export interface NavPillOption {
  id: TriageModalTab
  label: string
  route: string
  rolesPermitidos: ('ADMINISTRADOR' | 'OPERADOR' | 'AUDITOR' | 'SUPERVISOR')[]
}

export const NAV_PILLS: NavPillOption[] = [
  {
    id: 'enrutamiento',
    label: 'Enrutamiento',
    route: '/triaje',
    rolesPermitidos: ['ADMINISTRADOR', 'OPERADOR', 'AUDITOR', 'SUPERVISOR'],
  },
  {
    id: 'historial',
    label: 'Historial',
    route: '/documentos',
    rolesPermitidos: ['ADMINISTRADOR', 'OPERADOR', 'AUDITOR', 'SUPERVISOR'],
  },
  {
    id: 'solicitudes',
    label: 'Solicitudes',
    route: '/auditoria',
    rolesPermitidos: ['ADMINISTRADOR'],
  },
]

export type ModalState = 'EMPTY_DROPZONE' | 'FILE_STAGED' | 'PROCESSING'

