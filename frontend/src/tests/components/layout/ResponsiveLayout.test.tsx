import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import MainLayout from '../../../components/layout/MainLayout'
import * as authHook from '../../../hooks/useAuth'

vi.mock('../../../hooks/useAuth')
vi.mock('../../../services/alertStreamService', () => ({
  subscribeToAlertsStream: vi.fn(() => vi.fn()),
  playEmergencyAlertSound: vi.fn(),
}))

describe('ResponsiveLayout & Mobile Navigation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(authHook.useAuth).mockReturnValue({
      user: {
        id: 'user-admin',
        documento_identidad: '12345678',
        nombres: 'Admin',
        apellidos: 'MediFlow',
        correo: 'admin@mediflow.local',
        rol: 'ADMINISTRADOR',
        estado: 'ACTIVO',
        token: 'mock-token',
      },
      token: 'mock-token',
      isAuthenticated: true,
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
    })
  })

  it('renders mobile menu button on compact screens', () => {
    render(
      <MemoryRouter>
        <MainLayout />
      </MemoryRouter>
    )

    const menuButton = screen.getByRole('button', { name: /Abrir menú/i })
    expect(menuButton).toBeInTheDocument()
  })

  it('opens sidebar drawer and backdrop when mobile menu button is clicked', () => {
    render(
      <MemoryRouter>
        <MainLayout />
      </MemoryRouter>
    )

    const menuButton = screen.getByRole('button', { name: /Abrir menú/i })
    fireEvent.click(menuButton)

    const backdrop = screen.getByTestId('sidebar-backdrop')
    expect(backdrop).toBeInTheDocument()

    // Clicking backdrop closes drawer
    fireEvent.click(backdrop)
    expect(screen.queryByTestId('sidebar-backdrop')).not.toBeInTheDocument()
  })
})
