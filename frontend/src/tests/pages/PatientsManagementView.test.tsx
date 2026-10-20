import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import PatientsManagementView from '../../pages/PatientsManagementView'
import * as patientsApi from '../../api/patients.api'
import * as authHook from '../../hooks/useAuth'

vi.mock('../../api/patients.api')
vi.mock('../../hooks/useAuth')

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

const mockPatients: patientsApi.Paciente[] = [
  {
    id: 'pac-01',
    tipo_documento: 'DNI',
    numero_documento: '12345678',
    historia_clinica: 'HC-001',
    nombres: 'Carlos',
    apellidos: 'Santana',
    nombre_completo: 'Carlos Santana',
    fecha_nacimiento: '1980-05-10',
    sexo: 'M',
    telefono: '999888777',
    correo: 'carlos@example.com',
  },
  {
    id: 'pac-02',
    tipo_documento: 'CE',
    numero_documento: '98765432',
    historia_clinica: '',
    nombres: 'Maria',
    apellidos: 'Gomez',
    nombre_completo: 'Maria Gomez',
    fecha_nacimiento: '1992-08-20',
    sexo: 'F',
    telefono: '',
    correo: 'maria@example.com',
  },
]

describe('PatientsManagementView Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(authHook.useAuth).mockReturnValue({
      user: { id: 1, email: 'admin@mediflow.local', rol: 'ADMINISTRADOR', nombre_completo: 'Admin', estado: 'ACTIVO' } as any,
      token: 'mock-token',
      isAuthenticated: true,
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
    })
    vi.mocked(patientsApi.fetchPatients).mockResolvedValue({
      items: mockPatients,
      total: 2,
    } as any)
  })

  it('renders patient list with KPI cards and table', async () => {
    render(
      <MemoryRouter>
        <PatientsManagementView />
      </MemoryRouter>
    )

    expect(screen.getByText('Módulo de Pacientes')).toBeInTheDocument()
    expect(screen.getByText('Total Pacientes')).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText('12345678')).toBeInTheDocument()
      expect(screen.getByText('Carlos Santana')).toBeInTheDocument()
      expect(screen.getByText('HC-001')).toBeInTheDocument()
      expect(screen.getByText('Maria Gomez')).toBeInTheDocument()
    })
  })

  it('filters patients when search input is typed', async () => {
    render(
      <MemoryRouter>
        <PatientsManagementView />
      </MemoryRouter>
    )

    const searchInput = screen.getByPlaceholderText(/Buscar paciente por DNI/i)
    fireEvent.change(searchInput, { target: { value: 'Carlos' } })

    await waitFor(() => {
      expect(patientsApi.fetchPatients).toHaveBeenCalledWith('Carlos', 'mock-token')
    })
  })

  it('opens registration modal and registers a new patient', async () => {
    vi.mocked(patientsApi.createPatient).mockResolvedValue({
      message: 'Paciente registrado exitosamente.',
      data: { id: 'pac-03' } as any,
    } as any)

    render(
      <MemoryRouter>
        <PatientsManagementView />
      </MemoryRouter>
    )

    const registerBtn = screen.getByRole('button', { name: /Registrar Paciente/i })
    fireEvent.click(registerBtn)

    expect(screen.getByText(/RF-06 — Registrar Nuevo Paciente/i)).toBeInTheDocument()

    fireEvent.change(screen.getByPlaceholderText('Ej. 45678912'), { target: { value: '55667788' } })
    fireEvent.change(screen.getByPlaceholderText('Ej. Juan Carlos'), { target: { value: 'Roberto' } })
    fireEvent.change(screen.getByPlaceholderText('Ej. Pérez Ramos'), { target: { value: 'Perez' } })

    const submitBtn = screen.getByRole('button', { name: /Guardar Paciente/i })
    fireEvent.click(submitBtn)

    await waitFor(() => {
      expect(patientsApi.createPatient).toHaveBeenCalledWith(
        expect.objectContaining({
          numero_documento: '55667788',
          nombres: 'Roberto',
          apellidos: 'Perez',
        }),
        'mock-token'
      )
    })
  })

  it('navigates to document ingest with selected patient when Ingestar is clicked', async () => {
    render(
      <MemoryRouter>
        <PatientsManagementView />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Carlos Santana')).toBeInTheDocument()
    })

    const ingestButtons = screen.getAllByRole('button', { name: /Ingestar/i })
    fireEvent.click(ingestButtons[0])

    expect(mockNavigate).toHaveBeenCalledWith('/documentos/nuevo', {
      state: { paciente: mockPatients[0] },
    })
  })
})
