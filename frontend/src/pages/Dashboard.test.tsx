import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Dashboard from './Dashboard'
import { documentsApi } from '../api/documentsApi'

let mockUser: { rol: string; nombres: string; correo: string } | null = null

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    user: mockUser,
    isAuthenticated: !!mockUser,
    token: mockUser ? 'fake-token' : null,
    loading: false,
    login: vi.fn(),
    logout: vi.fn(),
  }),
}))

vi.mock('../api/documentsApi', () => ({
  documentsApi: {
    obtenerResumenDashboard: vi.fn(),
  },
}))

describe('Dashboard - Pantalla de Bienvenida y Cuentas Pendientes (FE-04 / Issue #56)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renderiza la pantalla de bienvenida para usuarios con rol PENDIENTE', async () => {
    mockUser = { rol: 'PENDIENTE', nombres: 'Nuevo Usuario', correo: 'nuevo@mediflow.local' }

    await render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    )

    expect(screen.getByRole('heading', { level: 1, name: /Bienvenido a/i })).toBeInTheDocument()
    expect(screen.getByAltText('MediFlow')).toBeInTheDocument()
    expect(screen.getByAltText('Equipo médico MediFlow')).toBeInTheDocument()
    expect(
      screen.getByText(/Tu solicitud de acceso ha sido enviada al administrador del sistema/i)
    ).toBeInTheDocument()

    // No debe consultar documentos protegidos
    expect(documentsApi.obtenerResumenDashboard).not.toHaveBeenCalled()
    // No debe renderizar métricas operativas
    expect(screen.queryByText('Documentos Procesados')).not.toBeInTheDocument()
  })

  it('renderiza el panel de métricas operativas para usuarios activos', async () => {
    mockUser = { rol: 'OPERADOR', nombres: 'Carlos Operador', correo: 'operador@mediflow.local' }
    vi.mocked(documentsApi.obtenerResumenDashboard).mockResolvedValue({
      procesados: 8,
      urgentes: 2,
      auditoria: 1,
      errores: 0,
      recientes: [],
    })

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    )

    expect(await screen.findByText('Panel de triaje')).toBeInTheDocument()
    expect(screen.getByText('Operación clínica')).toBeInTheDocument()
    expect(screen.getByText('Documentos Procesados')).toBeInTheDocument()
    expect(screen.getByText('Casos Urgentes')).toBeInTheDocument()
    expect(screen.getByText('Pendientes de Auditoría')).toBeInTheDocument()
    expect(screen.getByText('Errores / Rechazados')).toBeInTheDocument()

    expect(documentsApi.obtenerResumenDashboard).toHaveBeenCalledTimes(1)
  })

  it('muestra mensaje de error con botón de reintento ante fallos de carga', async () => {
    mockUser = { rol: 'ADMINISTRADOR', nombres: 'Admin', correo: 'admin@mediflow.local' }
    vi.mocked(documentsApi.obtenerResumenDashboard).mockRejectedValue(new Error('Network error'))

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    )

    expect(await screen.findByText('No se pudo cargar el resumen del dashboard.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Intentar nuevamente/i })).toBeInTheDocument()
  })
})
