import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import UsersManagementView from './UsersManagementView'
import * as authApi from '../api/auth.api'

const mockUsers: authApi.User[] = [
  {
    id: 'user-1',
    documento_identidad: '12345678',
    nombres: 'Ana',
    apellidos: 'Administradora',
    correo: 'admin@mediflow.local',
    rol: 'ADMINISTRADOR',
    estado: 'ACTIVO',
    especialidad_medica: 'Medicina General',
  },
  {
    id: 'user-2',
    documento_identidad: '87654321',
    nombres: 'Pedro',
    apellidos: 'Pendiente',
    correo: 'pedro@mediflow.local',
    rol: 'PENDIENTE',
    estado: 'ACTIVO',
    especialidad_medica: 'Pediatría',
  },
  {
    id: 'user-3',
    documento_identidad: '11223344',
    nombres: 'Laura',
    apellidos: 'Operadora',
    correo: 'laura@mediflow.local',
    rol: 'OPERADOR',
    estado: 'INACTIVO',
  },
]

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    user: { id: 'user-1', rol: 'ADMINISTRADOR', nombres: 'Ana', apellidos: 'Administradora' },
    token: 'admin-test-token',
    isAuthenticated: true,
  }),
}))

vi.mock('../api/auth.api', async () => {
  const actual = await vi.importActual('../api/auth.api')
  return {
    ...actual,
    fetchUsers: vi.fn(),
    updateUserDetails: vi.fn(),
    createNewUser: vi.fn(),
  }
})

describe('UsersManagementView - Solicitudes de Acceso y Aprobación (FE-10 / Issue #62)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(authApi.fetchUsers).mockResolvedValue(mockUsers)
  })

  it('renderiza la lista de usuarios y solicitudes recibidas', async () => {
    render(
      <MemoryRouter initialEntries={['/usuarios']}>
        <UsersManagementView />
      </MemoryRouter>
    )

    expect(await screen.findByText('Solicitudes de acceso')).toBeInTheDocument()
    expect(screen.getByText('Ana Administradora')).toBeInTheDocument()
    expect(screen.getByText('Pedro Pendiente')).toBeInTheDocument()
    expect(screen.getByText('Laura Operadora')).toBeInTheDocument()
  })

  it('activa automáticamente el filtro PENDIENTE cuando se navega a /solicitudes', async () => {
    render(
      <MemoryRouter initialEntries={['/solicitudes']}>
        <UsersManagementView />
      </MemoryRouter>
    )

    expect(await screen.findByText('Pedro Pendiente')).toBeInTheDocument()
    // En la vista de solicitudes sólo debe aparecer el pendiente inicialmente
    expect(screen.queryByText('Ana Administradora')).not.toBeInTheDocument()
    expect(screen.queryByText('Laura Operadora')).not.toBeInTheDocument()
  })

  it('permite buscar usuarios por nombre o correo', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter initialEntries={['/usuarios']}>
        <UsersManagementView />
      </MemoryRouter>
    )

    await screen.findByText('Ana Administradora')
    const searchInput = screen.getByPlaceholderText(/Buscar por nombre, correo o DNI/i)

    await user.type(searchInput, 'pedro')

    expect(screen.getByText('Pedro Pendiente')).toBeInTheDocument()
    expect(screen.queryByText('Ana Administradora')).not.toBeInTheDocument()
  })

  it('permite autorizar o cambiar el rol de un usuario mediante select', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.updateUserDetails).mockResolvedValue({
      ...mockUsers[1],
      rol: 'OPERADOR',
    })

    render(
      <MemoryRouter initialEntries={['/usuarios']}>
        <UsersManagementView />
      </MemoryRouter>
    )

    await screen.findByText('Pedro Pendiente')
    // El segundo select en la fila de Pedro es su rol
    const pedroRow = screen.getByText('Pedro Pendiente').closest('tr')!
    const roleSelect = pedroRow.querySelectorAll('select')[0]

    await user.selectOptions(roleSelect, 'OPERADOR')

    expect(authApi.updateUserDetails).toHaveBeenCalledWith(
      'admin-test-token',
      'user-2',
      { rol: 'OPERADOR' }
    )
  })

  it('permite alternar el permiso/estado de un usuario con el switch', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.updateUserDetails).mockResolvedValue({
      ...mockUsers[0],
      estado: 'INACTIVO',
    })

    render(
      <MemoryRouter initialEntries={['/usuarios']}>
        <UsersManagementView />
      </MemoryRouter>
    )

    await screen.findByText('Ana Administradora')
    const switches = screen.getAllByRole('switch')
    // El switch del primer usuario
    await user.click(switches[0])

    expect(authApi.updateUserDetails).toHaveBeenCalledWith(
      'admin-test-token',
      'user-1',
      { estado: 'INACTIVO' }
    )
  })
})
