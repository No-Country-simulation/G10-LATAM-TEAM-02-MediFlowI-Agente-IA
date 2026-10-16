import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import type { ClinicalDocument } from '../types/documents'

const mockNavigate = vi.fn()
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  Link: ({ to, children, className }: { to: string; children: React.ReactNode; className?: string }) => (
    <a href={to} className={className} data-testid={`link-${to}`}>
      {children}
    </a>
  ),
}))

let mockCurrentUser: {
  id: string
  nombres: string
  apellidos: string
  rol: 'ADMINISTRADOR' | 'OPERADOR' | 'AUDITOR' | 'SUPERVISOR'
} | null = {
  id: 'usr-1',
  nombres: 'Valeria',
  apellidos: 'Corvo',
  rol: 'ADMINISTRADOR',
}

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    user: mockCurrentUser,
    logout: vi.fn(),
  }),
}))

const mockAuditDocuments: ClinicalDocument[] = [
  {
    documento_id: 'DOC-001',
    nombre_archivo: 'informe_radiologico_01.pdf',
    fecha_creacion: '2026-05-27T10:00:00Z',
    clasificacion: {
      tipo_documento: 'Radiologia',
      score_confianza: 0.15, // < 25% (Rojo)
    },
    decision_enrutamiento: {
      motivo_auditoria: 'Inconsistencia en descripción clínica',
    },
  },
  {
    documento_id: 'DOC-002',
    nombre_archivo: 'receta_neumonologia_02.pdf',
    fecha_creacion: '2026-05-19T11:00:00Z',
    clasificacion: {
      tipo_documento: 'Neumonologia',
      score_confianza: 0.35, // 25% - 50% (Naranja)
    },
    decision_enrutamiento: {
      motivo_auditoria: 'Falta firma del médico tratante',
    },
  },
  {
    documento_id: 'DOC-003',
    nombre_archivo: 'epicrisis_urgencias_03.pdf',
    fecha_creacion: '2026-03-04T12:00:00Z',
    clasificacion: {
      tipo_documento: 'Urgencias',
      score_confianza: 0.65, // 50% - 75% (Amarillo)
    },
    decision_enrutamiento: {
      motivo_auditoria: 'Diagnóstico CIE-10 dudoso',
    },
  },
  {
    documento_id: 'DOC-004',
    nombre_archivo: 'laboratorio_sangre_04.pdf',
    fecha_creacion: '2026-07-27T14:00:00Z',
    clasificacion: {
      tipo_documento: 'Laboratorio',
      score_confianza: 0.88, // > 75% (Verde)
    },
    decision_enrutamiento: {
      motivo_auditoria: 'Verificación aleatoria de protocolo',
    },
  },
]

vi.mock('../api/auditApi', () => ({
  auditApi: {
    obtenerAuditorias: vi.fn().mockImplementation(() => Promise.resolve(mockAuditDocuments)),
  },
}))

import Audit from './Audit'
import { auditApi } from '../api/auditApi'

describe('Audit - Rediseño Visual de Auditoría Clínica', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockCurrentUser = {
      id: 'usr-1',
      nombres: 'Valeria',
      apellidos: 'Corvo',
      rol: 'ADMINISTRADOR',
    }
  })

  describe('US1: Cabecera, Píldoras RBAC y Tarjeta Principal', () => {
    it('renderiza el título exacto "Solicitudes de auditoría clínica"', async () => {
      render(<Audit />)

      await waitFor(() => {
        expect(
          screen.getByRole('heading', { level: 1, name: /solicitudes de auditoría clínica/i })
        ).toBeInTheDocument()
      }, { timeout: 10000 })
    }, 15000)

    it('renderiza la barra superior de píldoras con "Solicitudes" activa', async () => {
      render(<Audit />)

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /enrutamiento/i })).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /historial/i })).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /solicitudes/i })).toBeInTheDocument()
      })
    })

    it('OMITE completamente el menú dropdown de filtros', async () => {
      render(<Audit />)

      await waitFor(() => {
        expect(screen.queryByRole('combobox')).not.toBeInTheDocument()
        expect(screen.queryByText(/urgencias médicas/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('US2: Conservación Integral de Columnas y Campos Clínicos', () => {
    it('conserva exactamente las 6 columnas en el encabezado de la tabla', async () => {
      render(<Audit />)

      await waitFor(() => {
        expect(screen.getByText('ID')).toBeInTheDocument()
        expect(screen.getByText('Documento')).toBeInTheDocument()
        expect(screen.getByText('Confianza')).toBeInTheDocument()
        expect(screen.getByText('Motivo de Derivación')).toBeInTheDocument()
        expect(screen.getByText('Fecha')).toBeInTheDocument()
        expect(screen.getByText(/visualizar|acción/i)).toBeInTheDocument()
      })
    })

    it('renderiza los datos de los documentos sin pérdida de información', async () => {
      render(<Audit />)

      await waitFor(() => {
        expect(screen.getByText('DOC-001')).toBeInTheDocument()
        expect(screen.getByText('informe_radiologico_01.pdf')).toBeInTheDocument()
        expect(screen.getByText('Inconsistencia en descripción clínica')).toBeInTheDocument()
      })
    })
  })

  describe('US3: Badges de Confianza con Regla Cuádruple de Colores', () => {
    it('aplica los 4 colores de confianza según el score (<25% rojo, 25-50% naranja, 50-75% amarillo, >75% verde)', async () => {
      render(<Audit />)

      await waitFor(() => {
        // 15% -> Rojo
        expect(screen.getByText('15%')).toBeInTheDocument()
        const badge15 = screen.getByText('15%').closest('[data-testid="confidence-badge"]')
        expect(badge15).toHaveAttribute('data-tier', 'CRITICAL')

        // 35% -> Naranja
        expect(screen.getByText('35%')).toBeInTheDocument()
        const badge35 = screen.getByText('35%').closest('[data-testid="confidence-badge"]')
        expect(badge35).toHaveAttribute('data-tier', 'LOW')

        // 65% -> Amarillo
        expect(screen.getByText('65%')).toBeInTheDocument()
        const badge65 = screen.getByText('65%').closest('[data-testid="confidence-badge"]')
        expect(badge65).toHaveAttribute('data-tier', 'MEDIUM')

        // 88% -> Verde
        expect(screen.getByText('88%')).toBeInTheDocument()
        const badge88 = screen.getByText('88%').closest('[data-testid="confidence-badge"]')
        expect(badge88).toHaveAttribute('data-tier', 'HIGH')
      })
    })
  })

  describe('US4: Botón de Revisión Outline con Icono de Ojo FontAwesome y Hover Azul', () => {
    it('muestra botón outline con icono de ojo FontAwesome y enlace a /auditoria/:id', async () => {
      render(<Audit />)

      await waitFor(() => {
        const linkDoc1 = screen.getByTestId('link-/auditoria/DOC-001')
        expect(linkDoc1).toBeInTheDocument()
        expect(linkDoc1).toHaveAttribute('href', '/auditoria/DOC-001')

        // Verificar que contiene icono de ojo
        const eyeIcon = linkDoc1.querySelector('svg[data-icon="eye"]')
        expect(eyeIcon).toBeInTheDocument()

        // Verificar que tiene clases outline y hover azul var(--primary)
        expect(linkDoc1.className).toContain('hover:bg-[var(--primary)]')
      })
    })
  })

  describe('US5: Paginación Visual y Estados de Carga/Vacío', () => {
    it('muestra el control de paginación numerada', async () => {
      render(<Audit />)

      await waitFor(() => {
        expect(screen.getByText('01')).toBeInTheDocument()
      })
    })

    it('muestra estado vacío cuando no hay documentos', async () => {
      vi.mocked(auditApi.obtenerAuditorias).mockResolvedValueOnce([])
      render(<Audit />)

      await waitFor(() => {
        expect(screen.getByText(/no hay documentos pendientes de auditoría/i)).toBeInTheDocument()
      })
    })
  })
})

