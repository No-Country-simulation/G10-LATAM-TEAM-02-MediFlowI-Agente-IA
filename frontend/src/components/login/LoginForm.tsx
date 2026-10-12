import type { FormEvent, JSX } from 'react';
import { Input, Button, Alert } from '../common';
import FooterDivider from './FooterDivider';

interface LoginFormProps {
  email?: string;
  password: string;
  onChange?: (name: string, value: string) => void;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
  onRegister: () => void;
  isSubmitting: boolean;
  error?: string;
  errors?: Record<string, string>;
}

export function LoginForm({
  email,
  password,
  onChange,
  onSubmit,
  onRegister,
  isSubmitting,
  error,
  errors = {},
}: LoginFormProps): JSX.Element {
  const emailValue = email ?? '';

  const handleInputChange = (name: string, value: string) => {
    if (onChange) {
      onChange(name, value);
    }
  };

  const isFormFilled = emailValue.trim() !== '' && password.trim() !== '';

  return (
    <form
      onSubmit={onSubmit}
      noValidate
      className="flex flex-col w-full max-w-[420px] items-center gap-4 mt-1"
    >
      <div className="flex flex-col items-center gap-1.5 w-full text-center">
        <h1
          id="welcome-heading"
          className="font-bold text-[#1f2041] text-3xl sm:text-[32px] tracking-tight"
          style={{ fontFamily: "'Quicksand', sans-serif" }}
        >
          Bienvenido
        </h1>
        <p
          className="font-normal text-sm sm:text-base text-[rgba(31,32,65,0.5)]"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          ¿Con qué comenzaremos el día de hoy?
        </p>
      </div>

      {error && (
        <Alert
          type="error"
          title="Error de inicio de sesión"
          message={error}
        />
      )}

      <div className="flex flex-col gap-3 w-full">
        {/* Campo CORREO ELECTRÓNICO */}
        <label
          htmlFor="documentoIdentidad"
          className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : fieldCardEnabled}`}
        >
          <span
            className="font-bold text-[11px] tracking-[0.06px] text-[rgba(31,32,65,0.5)] uppercase"
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          >
            Correo Electrónico
          </span>
          <input
            id="documentoIdentidad"
            name="documentoIdentidad"
            type="text"
            autoComplete="username"
            aria-label="Correo"
            placeholder="email@example.com"
            value={documentoIdentidad}
            onChange={(e) => onDocumentoChange(e.target.value)}
            disabled={isSubmitting}
            className={`${inputBase} ${isSubmitting ? 'text-[rgba(31,32,65,0.45)] cursor-not-allowed' : 'text-[#1f2041]'}`}
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          />
        </label>

        {/* Campo CONTRASEÑA */}
        <Input
          type="password"
          name="password"
          value={password}
          onChange={handleInputChange}
          placeholder="••••••••••••"
          label="CONTRASEÑA"
          error={errors.password}
          disabled={isSubmitting}
        />
      </div>

      <div className="flex flex-col gap-3.5 w-full mt-1">
        <Button
          type="submit"
          text="Iniciar sesión"
          loading={isSubmitting}
          disabled={isSubmitting || !isFormFilled}
        />

        {/* Separador OR */}
        <FooterDivider
          lightText="¿No tienes una cuenta?"
          boldText="Regístrate"
          onNavigate={onRegister}
        />
      </div>
    </form>
  );
}
