import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import StorageSettingsView from '../../pages/StorageSettingsView'
import * as triageApi from '../../api/triage.api'
import * as authHook from '../../hooks/useAuth'

vi.mock('../../api/triage.api')
vi.mock('../../hooks/useAuth')

describe('StorageSettingsView Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders restricted access message if user is not ADMINISTRADOR', () => {
    vi.mocked(authHook.useAuth).mockReturnValue({
      user: { id: 2, email: 'medico@mediflow.local', rol: 'MEDICO', nombre_completo: 'Dr. House', estado: 'ACTIVO' } as any,
      token: 'mock-token',
      isAuthenticated: true,
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
    })

    render(<StorageSettingsView />)

    expect(screen.getByText(/Acceso Restringido \(RBAC\)/i)).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: /Configuración de Almacenamiento/i })).not.toBeInTheDocument()
  })

  it('renders storage configuration for ADMINISTRADOR and loads settings', async () => {
    vi.mocked(authHook.useAuth).mockReturnValue({
      user: { id: 1, email: 'admin@mediflow.local', rol: 'ADMINISTRADOR', nombre_completo: 'Admin', estado: 'ACTIVO' } as any,
      token: 'mock-token',
      isAuthenticated: true,
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
    })

    vi.mocked(triageApi.obtenerConfiguracion).mockResolvedValue({
      storage_mode: 'LOCAL',
      oci_configured: false,
    } as any)

    render(<StorageSettingsView />)

    expect(screen.getByText('Configuración de Almacenamiento')).toBeInTheDocument()
    expect(screen.getByText('Almacenamiento Local')).toBeInTheDocument()
    expect(screen.getByText('OCI Object Storage')).toBeInTheDocument()

    await waitFor(() => {
      expect(triageApi.obtenerConfiguracion).toHaveBeenCalledTimes(1)
    })
  })

  it('allows selecting OCI mode and saving preference', async () => {
    vi.mocked(authHook.useAuth).mockReturnValue({
      user: { id: 1, email: 'admin@mediflow.local', rol: 'ADMINISTRADOR', nombre_completo: 'Admin', estado: 'ACTIVO' } as any,
      token: 'mock-token',
      isAuthenticated: true,
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
    })

    vi.mocked(triageApi.obtenerConfiguracion).mockResolvedValue({
      storage_mode: 'LOCAL',
      oci_configured: false,
    } as any)

    vi.mocked(triageApi.actualizarConfiguracion).mockResolvedValue({
      storage_mode: 'OCI',
      oci_configured: false,
    } as any)

    render(<StorageSettingsView />)

    await waitFor(() => {
      expect(screen.getByText('Almacenamiento Local')).toBeInTheDocument()
    })

    // Click on OCI card
    const ociCard = screen.getByText('OCI Object Storage')
    fireEvent.click(ociCard)

    // Save button
    const saveButton = screen.getByRole('button', { name: /Guardar Preferencia en Base de Datos/i })
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(triageApi.actualizarConfiguracion).toHaveBeenCalledWith('OCI')
      expect(screen.getByText(/Preferencia guardada: Almacenamiento OCI actualizado en PostgreSQL/i)).toBeInTheDocument()
    })
  })
})
