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

  it('renderiza campo DNI con etiqueta asociada', () => {
    render(<Login />)
    const dniInput = screen.getByLabelText(/DNI/i)
    expect(dniInput).toBeInTheDocument()
    expect(dniInput).toHaveAttribute('type', 'text')
    expect(dniInput).toHaveAttribute('inputMode', 'numeric')
    expect(dniInput).toHaveAttribute('maxLength', '8')
    expect(dniInput).toHaveAttribute('autoComplete', 'username')
  })

  it('renderiza campo contraseña con etiqueta asociada', () => {
    render(<Login />)
    const passwordInput = screen.getByLabelText(/CONTRASEÑA/i)
    expect(passwordInput).toBeInTheDocument()
    expect(passwordInput).toHaveAttribute('type', 'password')
    expect(passwordInput).toHaveAttribute('autoComplete', 'current-password')
  })

  it('renderiza botón "Iniciar sesión"', () => {
    render(<Login />)
    const button = screen.getByRole('button', { name: /Iniciar sesión/i })
    expect(button).toBeInTheDocument()
    expect(button).toHaveAttribute('type', 'submit')
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

describe('Login - Validación y submit (US2)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('no envía el formulario con campos vacíos', async () => {
    mockLogin.mockResolvedValue({ success: true })
    const user = userEvent.setup()
    render(<Login />)
    const button = screen.getByRole('button', { name: /Iniciar sesión/i })
    await user.click(button)
    expect(mockNavigate).not.toHaveBeenCalled()
  })

  it('muestra error cuando el login falla', async () => {
    mockLogin.mockResolvedValue({ success: false, message: 'Credenciales incorrectas' })
    const user = userEvent.setup()
    const { container } = render(<Login />)

    const dniInput = screen.getByLabelText(/DNI/i)
    const passwordInput = screen.getByLabelText(/CONTRASEÑA/i)
    const button = screen.getByRole('button', { name: /Iniciar sesión/i })

    await user.type(dniInput, '12345678')
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

    const dniInput = screen.getByLabelText(/DNI/i)
    const passwordInput = screen.getByLabelText(/CONTRASEÑA/i)
    const button = screen.getByRole('button', { name: /Iniciar sesión/i })

    await user.type(dniInput, '12345678')
    await user.type(passwordInput, 'testpassword')
    await user.click(button)

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
