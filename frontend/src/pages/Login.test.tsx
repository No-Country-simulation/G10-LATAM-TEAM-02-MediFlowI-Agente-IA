import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

const mockLogin = vi.fn()
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    login: mockLogin,
    logout: vi.fn(),
    user: null,
    token: null,
    isAuthenticated: false,
    loading: false,
  }),
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  useLocation: () => ({ state: { from: { pathname: '/dashboard' } } }),
}))

import Login from './Login'

describe('Login - Renderizado (US1)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLogin.mockResolvedValue({ success: true })
  })

  it('renderiza el título "Bienvenido"', () => {
    render(<Login />)
    const heading = screen.getByRole('heading', { level: 1 })
    expect(heading).toHaveTextContent('Bienvenido')
  })

  it('renderiza el subtítulo de bienvenida', () => {
    render(<Login />)
    expect(screen.getByText(/¿Con qué comenzaremos/i)).toBeInTheDocument()
  })

  it('renderiza el logo de MediFlow con alt correcto', () => {
    render(<Login />)
    const logo = screen.getByAltText('MediFlow')
    expect(logo).toBeInTheDocument()
  })

  it('renderiza el texto del sistema autónomo', () => {
    render(<Login />)
    expect(screen.getByText(/SISTEMA AUTÓNOMO DE TRIAJE/i)).toBeInTheDocument()
  })

  it('renderiza campo correo con etiqueta asociada', () => {
    render(<Login />)
    const correoInput = screen.getByLabelText(/CORREO/i)
    expect(correoInput).toBeInTheDocument()
    expect(correoInput).toHaveAttribute('type', 'email')
    expect(correoInput).toHaveAttribute('placeholder', 'email@example.com')
  })

  it('renderiza campo contraseña con etiqueta asociada', () => {
    render(<Login />)
    const passwordInput = screen.getByLabelText('CONTRASEÑA')
    expect(passwordInput).toBeInTheDocument()
    expect(passwordInput).toHaveAttribute('type', 'password')
  })

  it('renderiza botón "Iniciar sesión"', () => {
    render(<Login />)
    const button = screen.getByRole('button', { name: /Iniciar sesión/i })
    expect(button).toBeInTheDocument()
    expect(button).toHaveAttribute('type', 'submit')
  })

  it('el botón para iniciar sesión permanece deshabilitado si no hay texto ingresado', () => {
    render(<Login />)
    const button = screen.getByRole('button', { name: /Iniciar sesión/i })
    expect(button).toBeDisabled()
  })

  it('no tiene defaultValue en los inputs (sin credenciales hardcodeadas)', () => {
    const { container } = render(<Login />)
    const inputs = container.querySelectorAll('input')
    inputs.forEach((input) => {
      expect(input).not.toHaveAttribute('defaultValue')
      expect(input.getAttribute('value') ?? '').toBe('')
    })
  })
})

describe('Login - Interacción, Validación y submit (US2)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('actualiza el valor escrito en el input y no renderiza el nombre del campo', async () => {
    const user = userEvent.setup()
    render(<Login />)

    const correoInput = screen.getByLabelText(/CORREO/i) as HTMLInputElement
    await user.type(correoInput, 'doctor@mediflow.com')

    expect(correoInput.value).toBe('doctor@mediflow.com')
    expect(correoInput.value).not.toBe('correo')
    expect(correoInput.value).not.toBe('documentoIdentidad')
  })

  it('habilita el botón solo cuando ambos campos contienen texto', async () => {
    const user = userEvent.setup()
    render(<Login />)

    const button = screen.getByRole('button', { name: /Iniciar sesión/i })
    const correoInput = screen.getByLabelText(/CORREO/i)
    const passwordInput = screen.getByLabelText('CONTRASEÑA')

    expect(button).toBeDisabled()

    await user.type(correoInput, 'doctor@mediflow.com')
    expect(button).toBeDisabled()

    await user.type(passwordInput, 'Secret123!')
    expect(button).not.toBeDisabled()
  })

  it('muestra mensaje de error si se ingresa un correo con formato inválido', async () => {
    const user = userEvent.setup()
    render(<Login />)

    const correoInput = screen.getByLabelText(/CORREO/i)
    const passwordInput = screen.getByLabelText('CONTRASEÑA')
    const button = screen.getByRole('button', { name: /Iniciar sesión/i })

    await user.type(correoInput, 'cadena_simple_invalida')
    await user.type(passwordInput, 'Secret123!')
    await user.click(button)

    expect(screen.getByText('Por favor, introduzca una dirección de correo electrónico válida')).toBeInTheDocument()
    expect(mockLogin).not.toHaveBeenCalled()
  })

  it('muestra error general cuando el login falla en el servidor', async () => {
    mockLogin.mockResolvedValue({ success: false, message: 'Credenciales incorrectas' })
    const user = userEvent.setup()
    const { container } = render(<Login />)

    const correoInput = screen.getByLabelText(/CORREO/i)
    const passwordInput = screen.getByLabelText('CONTRASEÑA')
    const button = screen.getByRole('button', { name: /Iniciar sesión/i })

    await user.type(correoInput, 'doctor@mediflow.com')
    await user.type(passwordInput, 'testpassword')
    await user.click(button)

    await vi.waitFor(() => {
      expect(container.querySelector('[aria-live="polite"]')).toBeInTheDocument()
    })
  })

  it('navega al dashboard cuando el login es exitoso', async () => {
    mockLogin.mockResolvedValue({ success: true })
    const user = userEvent.setup()
    render(<Login />)

    const correoInput = screen.getByLabelText(/CORREO/i)
    const passwordInput = screen.getByLabelText('CONTRASEÑA')
    const button = screen.getByRole('button', { name: /Iniciar sesión/i })

    await user.type(correoInput, 'doctor@mediflow.com')
    await user.type(passwordInput, 'testpassword')
    await user.click(button)

    await vi.waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true })
    })
  })

  it('envía correo y contraseña al hook de autenticación preservando el perfil de usuario', async () => {
    const mockUserPayload = {
      id: 'usr-1234-uuid',
      documento_identidad: '12345678',
      nombres: 'María',
      apellidos: 'Gómez Pérez',
      correo: 'maria.gomez@mediflow.local',
      especialidad_medica: 'Medicina General',
      rol: 'COORDINADOR',
      estado: 'ACTIVO',
      token: 'mf_session_token_123',
    }
    mockLogin.mockResolvedValue({ success: true, user: mockUserPayload })

    const user = userEvent.setup()
    render(<Login />)

    const correoInput = screen.getByLabelText(/CORREO/i)
    const passwordInput = screen.getByLabelText('CONTRASEÑA')
    const button = screen.getByRole('button', { name: /Iniciar sesión/i })

    await user.type(correoInput, 'maria.gomez@mediflow.local')
    await user.type(passwordInput, 'ClaveSegura#2026')
    await user.click(button)

    expect(mockLogin).toHaveBeenCalledWith('maria.gomez@mediflow.local', 'ClaveSegura#2026')
    await vi.waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true })
    })
  })
})

describe('Login - Enlace de registro (US3)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLogin.mockResolvedValue({ success: true })
  })

  it('renderiza el enlace "Regístrate"', () => {
    render(<Login />)
    expect(screen.getByRole('button', { name: /Regístrate/i })).toBeInTheDocument()
  })

  it('navega a /signup al hacer click en Regístrate', async () => {
    const user = userEvent.setup()
    render(<Login />)
    const registerButton = screen.getByRole('button', { name: /Regístrate/i })
    await user.click(registerButton)
    expect(mockNavigate).toHaveBeenCalledWith('/signup')
  })
})
