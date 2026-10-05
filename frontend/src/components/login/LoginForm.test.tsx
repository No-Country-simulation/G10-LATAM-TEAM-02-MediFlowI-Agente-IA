import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LoginForm } from './LoginForm'

describe('LoginForm (US2)', () => {
  const defaultProps = {
    documentoIdentidad: '',
    password: '',
    onDocumentoChange: vi.fn(),
    onPasswordChange: vi.fn(),
    onSubmit: vi.fn(),
    onRegister: vi.fn(),
    isSubmitting: false,
    error: '',
  }

  it('deshabilita el botón cuando isSubmitting es true', () => {
    render(<LoginForm {...defaultProps} isSubmitting={true} />)
    const button = screen.getByRole('button', { name: /Ingresando/i })
    expect(button).toBeDisabled()
  })

  it('muestra "Iniciar sesión" cuando no está submitting', () => {
    render(<LoginForm {...defaultProps} />)
    expect(screen.getByRole('button', { name: /Iniciar sesión/i })).toBeInTheDocument()
  })

  it('muestra el mensaje de error cuando error no está vacío', () => {
    render(<LoginForm {...defaultProps} error="Credenciales incorrectas" />)
    expect(screen.getByText('Credenciales incorrectas')).toBeInTheDocument()
  })

  it('el mensaje de error tiene aria-live="polite"', () => {
    render(<LoginForm {...defaultProps} error="Error test" />)
    const errorElement = screen.getByRole('alert')
    expect(errorElement).toHaveAttribute('aria-live', 'polite')
  })

  it('no muestra error cuando error está vacío', () => {
    render(<LoginForm {...defaultProps} error="" />)
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('bloquea los campos DNI y contraseña mientras se inicia sesión', () => {
    render(<LoginForm {...defaultProps} isSubmitting={true} />)
    expect(screen.getByLabelText(/DNI/i)).toBeDisabled()
    expect(screen.getByLabelText(/CONTRASEÑA/i)).toBeDisabled()
  })

  it('mantiene los campos habilitados cuando no se está enviando', () => {
    render(<LoginForm {...defaultProps} />)
    expect(screen.getByLabelText(/DNI/i)).toBeEnabled()
    expect(screen.getByLabelText(/CONTRASEÑA/i)).toBeEnabled()
  })

  it('muestra un loader dentro del botón mientras se inicia sesión', () => {
    render(<LoginForm {...defaultProps} isSubmitting={true} />)
    const button = screen.getByRole('button', { name: /Ingresando/i })
    expect(button).toHaveAttribute('aria-busy', 'true')
    expect(screen.getByTestId('login-spinner')).toBeInTheDocument()
  })

  it('no muestra el loader cuando no se está enviando', () => {
    render(<LoginForm {...defaultProps} />)
    expect(screen.queryByTestId('login-spinner')).not.toBeInTheDocument()
  })
})
