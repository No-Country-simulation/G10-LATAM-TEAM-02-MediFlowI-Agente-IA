import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { SignUpForm } from '../../../components/auth/SignUpForm';
import { signupUser } from '../../../api/auth.api';

// Mock the API
vi.mock('../../../api/auth.api', () => ({
  signupUser: vi.fn(),
}));

describe('SignUpForm', () => {
  const mockSignupUser = vi.mocked(signupUser);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders all expected fields according to the clinical design mockup including identification number', () => {
    render(<SignUpForm />);

    expect(screen.getByRole('heading', { name: /Crea tu cuenta/i })).toBeInTheDocument();
    expect(screen.getByText(/Por favor ingrese los siguientes datos/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ej\. María Fernanda/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ej\. Castañeda Hernández/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/00000000/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ej\. \(\+52\) 555-152-3056/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/email@example\.com/i)).toBeInTheDocument();
    expect(screen.getAllByPlaceholderText(/••••••••••••/i)).toHaveLength(2);
    expect(screen.getByRole('button', { name: /Enviar solicitud/i })).toBeInTheDocument();
  });

  it('submits successfully with valid data and renders success alert', async () => {
    const onSuccess = vi.fn();
    mockSignupUser.mockResolvedValueOnce({
      id: '1',
      documento_identidad: '12345678',
      nombres: 'Alex Jordan',
      apellidos: 'Castañeda',
      telefono: '(+52) 555-152-3056',
      correo: 'alex.jordan@gmail.com',
      rol: 'OPERADOR',
      estado: 'INACTIVO',
    });

    render(<SignUpForm onSuccess={onSuccess} />);

    fireEvent.change(screen.getByPlaceholderText(/Ej\. María Fernanda/i), { target: { value: 'Alex Jordan' } });
    fireEvent.change(screen.getByPlaceholderText(/Ej\. Castañeda Hernández/i), { target: { value: 'Castañeda' } });
    fireEvent.change(screen.getByPlaceholderText(/00000000/i), { target: { value: '12345678' } });
    fireEvent.change(screen.getByPlaceholderText(/Ej\. \(\+52\) 555-152-3056/i), { target: { value: '(+52) 555-152-3056' } });
    fireEvent.change(screen.getByPlaceholderText(/email@example\.com/i), { target: { value: 'alex.jordan@gmail.com' } });
    
    const passwordInputs = screen.getAllByPlaceholderText(/••••••••••••/i);
    fireEvent.change(passwordInputs[0], { target: { value: '#Password123' } });
    fireEvent.change(passwordInputs[1], { target: { value: '#Password123' } });

    const submitBtn = screen.getByRole('button', { name: /Enviar solicitud/i });
    expect(submitBtn).not.toBeDisabled();
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(mockSignupUser).toHaveBeenCalledWith({
        documento_identidad: '12345678',
        nombres: 'Alex Jordan',
        apellidos: 'Castañeda',
        telefono: '(+52) 555-152-3056',
        correo: 'alex.jordan@gmail.com',
        password: '#Password123',
      });
      expect(onSuccess).toHaveBeenCalled();
      expect(screen.getByText(/¡Registro exitoso!/i)).toBeInTheDocument();
      expect(screen.getByText(/Tu solicitud de acceso ha sido enviada al administrador del sistema/i)).toBeInTheDocument();
    });
  });

  it('displays validation error for invalid identification document', async () => {
    render(<SignUpForm />);

    fireEvent.change(screen.getByPlaceholderText(/Ej\. María Fernanda/i), { target: { value: 'Alex' } });
    fireEvent.change(screen.getByPlaceholderText(/Ej\. Castañeda Hernández/i), { target: { value: 'Castañeda' } });
    fireEvent.change(screen.getByPlaceholderText(/00000000/i), { target: { value: '12345' } });
    fireEvent.change(screen.getByPlaceholderText(/email@example\.com/i), { target: { value: 'alex@test.com' } });

    const passwordInputs = screen.getAllByPlaceholderText(/••••••••••••/i);
    fireEvent.change(passwordInputs[0], { target: { value: '#Password123' } });
    fireEvent.change(passwordInputs[1], { target: { value: '#Password123' } });

    fireEvent.click(screen.getByRole('button', { name: /Enviar solicitud/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/El número de identificación debe tener 8 dígitos/i)
      ).toBeInTheDocument();
      expect(mockSignupUser).not.toHaveBeenCalled();
    });
  });

  it('displays validation error for invalid email', async () => {
    render(<SignUpForm />);

    fireEvent.change(screen.getByPlaceholderText(/Ej\. María Fernanda/i), { target: { value: 'Alex' } });
    fireEvent.change(screen.getByPlaceholderText(/Ej\. Castañeda Hernández/i), { target: { value: 'Castañeda' } });
    fireEvent.change(screen.getByPlaceholderText(/00000000/i), { target: { value: '12345678' } });
    fireEvent.change(screen.getByPlaceholderText(/email@example\.com/i), { target: { value: 'invalid-email' } });

    const passwordInputs = screen.getAllByPlaceholderText(/••••••••••••/i);
    fireEvent.change(passwordInputs[0], { target: { value: '#Password123' } });
    fireEvent.change(passwordInputs[1], { target: { value: '#Password123' } });

    fireEvent.click(screen.getByRole('button', { name: /Enviar solicitud/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/Por favor, introduzca una dirección de correo electrónico válida/i)
      ).toBeInTheDocument();
      expect(mockSignupUser).not.toHaveBeenCalled();
    });
  });

  it('displays validation error for mismatched passwords', async () => {
    render(<SignUpForm />);

    fireEvent.change(screen.getByPlaceholderText(/Ej\. María Fernanda/i), { target: { value: 'Alex' } });
    fireEvent.change(screen.getByPlaceholderText(/Ej\. Castañeda Hernández/i), { target: { value: 'Castañeda' } });
    fireEvent.change(screen.getByPlaceholderText(/00000000/i), { target: { value: '12345678' } });
    fireEvent.change(screen.getByPlaceholderText(/email@example\.com/i), { target: { value: 'alex@test.com' } });

    const passwordInputs = screen.getAllByPlaceholderText(/••••••••••••/i);
    fireEvent.change(passwordInputs[0], { target: { value: '#Password123' } });
    fireEvent.change(passwordInputs[1], { target: { value: '#Different456' } });

    fireEvent.click(screen.getByRole('button', { name: /Enviar solicitud/i }));

    await waitFor(() => {
      expect(screen.getByText(/Las contraseñas no coinciden/i)).toBeInTheDocument();
      expect(mockSignupUser).not.toHaveBeenCalled();
    });
  });

  it('displays error message when duplicate email error is returned from API', async () => {
    mockSignupUser.mockRejectedValueOnce(new Error('El correo electrónico ya se encuentra registrado.'));

    render(<SignUpForm />);

    fireEvent.change(screen.getByPlaceholderText(/Ej\. María Fernanda/i), { target: { value: 'Alex' } });
    fireEvent.change(screen.getByPlaceholderText(/Ej\. Castañeda Hernández/i), { target: { value: 'Castañeda' } });
    fireEvent.change(screen.getByPlaceholderText(/00000000/i), { target: { value: '12345678' } });
    fireEvent.change(screen.getByPlaceholderText(/email@example\.com/i), { target: { value: 'alex.jordan@gmail.com' } });

    const passwordInputs = screen.getAllByPlaceholderText(/••••••••••••/i);
    fireEvent.change(passwordInputs[0], { target: { value: '#Password123' } });
    fireEvent.change(passwordInputs[1], { target: { value: '#Password123' } });

    fireEvent.click(screen.getByRole('button', { name: /Enviar solicitud/i }));

    await waitFor(() => {
      expect(screen.getByText(/El correo electrónico ya se encuentra registrado/i)).toBeInTheDocument();
    });
  });

  it('displays error message when duplicate identification document error is returned from API', async () => {
    mockSignupUser.mockRejectedValueOnce(new Error('El documento de identidad ya se encuentra registrado.'));

    render(<SignUpForm />);

    fireEvent.change(screen.getByPlaceholderText(/Ej\. María Fernanda/i), { target: { value: 'Alex' } });
    fireEvent.change(screen.getByPlaceholderText(/Ej\. Castañeda Hernández/i), { target: { value: 'Castañeda' } });
    fireEvent.change(screen.getByPlaceholderText(/00000000/i), { target: { value: '12345678' } });
    fireEvent.change(screen.getByPlaceholderText(/email@example\.com/i), { target: { value: 'alex.jordan@gmail.com' } });

    const passwordInputs = screen.getAllByPlaceholderText(/••••••••••••/i);
    fireEvent.change(passwordInputs[0], { target: { value: '#Password123' } });
    fireEvent.change(passwordInputs[1], { target: { value: '#Password123' } });

    fireEvent.click(screen.getByRole('button', { name: /Enviar solicitud/i }));

    await waitFor(() => {
      expect(screen.getByText(/El documento de identidad ya se encuentra registrado/i)).toBeInTheDocument();
    });
  });

  it('displays server error alert on unexpected server failure', async () => {
    mockSignupUser.mockRejectedValueOnce(new Error('Internal server error'));

    render(<SignUpForm />);

    fireEvent.change(screen.getByPlaceholderText(/Ej\. María Fernanda/i), { target: { value: 'Alex' } });
    fireEvent.change(screen.getByPlaceholderText(/Ej\. Castañeda Hernández/i), { target: { value: 'Castañeda' } });
    fireEvent.change(screen.getByPlaceholderText(/00000000/i), { target: { value: '12345678' } });
    fireEvent.change(screen.getByPlaceholderText(/email@example\.com/i), { target: { value: 'alex.jordan@gmail.com' } });

    const passwordInputs = screen.getAllByPlaceholderText(/••••••••••••/i);
    fireEvent.change(passwordInputs[0], { target: { value: '#Password123' } });
    fireEvent.change(passwordInputs[1], { target: { value: '#Password123' } });

    fireEvent.click(screen.getByRole('button', { name: /Enviar solicitud/i }));

    await waitFor(() => {
      expect(screen.getByText(/Error Interno del Servidor/i)).toBeInTheDocument();
      expect(
        screen.getByText(/Ocurrió un error inesperado al procesar la solicitud en el servidor/i)
      ).toBeInTheDocument();
    });
  });

  it('toggles password visibility when eye button is clicked', () => {
    render(<SignUpForm />);

    const passwordInput = screen.getAllByPlaceholderText(/••••••••••••/i)[0];
    const toggleButton = screen.getByLabelText(/Ver contraseña/i);

    expect(passwordInput).toHaveAttribute('type', 'password');

    fireEvent.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'text');

    const hideButton = screen.getByLabelText(/Ocultar contraseña/i);
    fireEvent.click(hideButton);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });
});
