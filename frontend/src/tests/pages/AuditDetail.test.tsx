import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import AuditDetail from '../../pages/AuditDetail'
import * as auditApiModule from '../../api/auditApi'
import type { ClinicalDocument } from '../../types/documents'

vi.mock('../../api/auditApi')

const mockAuditDoc: ClinicalDocument = {
  documento_id: 'DOC-CLIN-3526-11',
  nombre_archivo: 'DOC-CLIN-3526-11.pdf',
  fecha_creacion: '2026-10-20T10:00:00Z',
  url_archivo: '/api/v1/documents/DOC-CLIN-3526-11/file',
  estado: 'AUDITORIA',
  clasificacion: {
    tipo_documento: 'Informe Radiológico',
    prioridad: 'URGENTE',
    score_confianza: 0.25,
    especialidad: 'Radiología / Neuropatología',
  },
  datos_extraidos: {
    paciente: {
      nombre: 'Carlos Eduardo Mendes',
      dni: '88084446',
      edad: 25,
    },
    medico: {
      nombre: 'Dra. Renata Silveira',
      cmp: '145892',
    },
    estudio_solicitado: 'Tomografía de Tórax con contraste',
    diagnostico: 'Tromboembolismo Pulmonar Agudo (TEP)',
    cie10: 'I26.9',
  },
  decision_enrutamiento: {
    destino: 'Cola de Emergencia Médica',
    motivo_auditoria: 'Hallazgo crítico de alta gravedad (TEP agudo) detectado en paciente sintomático.',
  },
}

describe('AuditDetail Component (Mockup UI & Balanced Layout)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(auditApiModule.auditApi.obtenerAuditoriaPorId).mockResolvedValue(mockAuditDoc)
    vi.mocked(auditApiModule.auditApi.corregirAuditoria).mockResolvedValue(mockAuditDoc)
    vi.mocked(auditApiModule.auditApi.aprobarAuditoria).mockResolvedValue(mockAuditDoc)
    vi.mocked(auditApiModule.auditApi.rechazarAuditoria).mockResolvedValue(mockAuditDoc)
  })

  it('renders centered audit header, confidence badge, and two balanced cards', async () => {
    render(
      <MemoryRouter initialEntries={['/auditoria/DOC-CLIN-3526-11']}>
        <Routes>
          <Route path="/auditoria/:id" element={<AuditDetail />} />
        </Routes>
      </MemoryRouter>
    )

    expect(await screen.findByText('Auditoría de triaje')).toBeInTheDocument()
    expect(
      screen.getByText('Human in the loop: Validación y corrección de los datos extraídos por el agente')
    ).toBeInTheDocument()
    expect(screen.getByText('25%')).toBeInTheDocument()

    // Left card
    expect(screen.getAllByText('Datos extraídos').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('Información básica del paciente')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Carlos Eduardo Mendes')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Dra. Renata Silveira')).toBeInTheDocument()

    // Right card
    expect(screen.getByText('Reporte de triaje')).toBeInTheDocument()
    expect(screen.getByText('Corrija o confirme los datos detectados por el agente de MediFlow')).toBeInTheDocument()
    expect(screen.getByText('Clasificación')).toBeInTheDocument()
    expect(screen.getByText('Decisión de enrutamiento')).toBeInTheDocument()

    // Buttons
    expect(screen.getByRole('button', { name: /Rechazar Documento/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Confirmar y Enviar/i })).toBeInTheDocument()
  })

  it('triggers confirmation modal when clicking Confirmar y Enviar', async () => {
    render(
      <MemoryRouter initialEntries={['/auditoria/DOC-CLIN-3526-11']}>
        <Routes>
          <Route path="/auditoria/:id" element={<AuditDetail />} />
        </Routes>
      </MemoryRouter>
    )

    const confirmBtn = await screen.findByRole('button', { name: /Confirmar y Enviar/i })
    fireEvent.click(confirmBtn)

    expect(screen.getByText('Confirmar y Enviar Decisión')).toBeInTheDocument()
    expect(
      screen.getByText('¿Desea validar y despachar los datos clínicos auditados al destino de triaje asignado?')
    ).toBeInTheDocument()
  })

  it('triggers reject modal when clicking Rechazar Documento', async () => {
    render(
      <MemoryRouter initialEntries={['/auditoria/DOC-CLIN-3526-11']}>
        <Routes>
          <Route path="/auditoria/:id" element={<AuditDetail />} />
        </Routes>
      </MemoryRouter>
    )

    const rejectBtn = await screen.findByRole('button', { name: /Rechazar Documento/i })
    fireEvent.click(rejectBtn)

    expect(screen.getAllByText('Rechazar Documento').length).toBeGreaterThanOrEqual(2)
    expect(
      screen.getByText('¿Está seguro de rechazar este documento? El expediente pasará a estado RECHAZADO.')
    ).toBeInTheDocument()
  })
})
