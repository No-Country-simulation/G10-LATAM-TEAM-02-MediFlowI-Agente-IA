import { useState, type FormEvent, type JSX } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faEyeSlash } from '@fortawesome/free-regular-svg-icons';
import { faCheck, faXmark } from '@fortawesome/free-solid-svg-icons';
import cn from "../../utils/cn";
import { signupUser } from '../../api/auth.api';
import type { User } from '../../api/auth.api';
import Button from "../common/Button";

const fieldCardBase =
  'flex flex-col items-start px-3.5 py-1.5 rounded-lg border transition-all shadow-[0_2px_8px_rgba(31,32,65,0.03)]';
const fieldCardEnabled = cn(
  "bg-white border-[#2c5282] text-[rgba(31,32,65,0.5)] cursor-text",
  'hover:border-[#2c5282] focus-within:text-[#2c5282] focus-within:border-[#2c5282] focus-within:ring-2 focus-within:ring-[#2c5282]'
);
const fieldCardDisabled = 'bg-[#e9ecef] border-[rgba(31,32,65,0.08)] opacity-80 cursor-not-allowed';
const fieldCardError = cn(
  'bg-white border-[#F72C2C] text-[#F72C2C] cursor-text',
  "hover:border-[#F72C2C]",
  "focus-within:border-[#F72C2C] focus-within:ring-2 focus-within:ring-[#F72C2C]"
);
const inputBase =
  'w-full font-medium text-xs sm:text-sm placeholder:text-[rgba(31,32,65,0.35)] outline-none bg-transparent pt-0.5';

interface SignUpFormProps {
  onSuccess?: (user: User) => void;
  onNavigateToLogin?: () => void;
}

export function SignUpForm({ onSuccess, onNavigateToLogin }: SignUpFormProps): JSX.Element {
  const [formData, setFormData] = useState({
    nombres: '',
    apellidos: '',
    documento_identidad: '',
    telefono: '',
    correo: '',
    password: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successAlert, setSuccessAlert] = useState(false);
  const [serverErrorAlert, setServerErrorAlert] = useState(false);

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.nombres.trim()) {
      newErrors.nombres = 'Por favor ingrese su nombre.';
    }
    if (!formData.apellidos.trim()) {
      newErrors.apellidos = 'Por favor ingrese sus apellidos.';
    }

    const docRegex = /^\d{8}$/;
    if (!formData.documento_identidad.trim() || !docRegex.test(formData.documento_identidad.trim())) {
      newErrors.documento_identidad = 'El número de identificación debe tener 8 dígitos.';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.correo.trim() || !emailRegex.test(formData.correo.trim())) {
      newErrors.correo = 'Por favor, introduzca una dirección de correo electrónico válida';
    }
    const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/;
    if (!passwordRegex.test(formData.password)) {
      newErrors.password =
        'La contraseña debe tener al menos 8 caracteres, 1 mayúscula, 1 número y 1 carácter especial.';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSuccessAlert(false);
    setServerErrorAlert(false);

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const user = await signupUser({
        documento_identidad: formData.documento_identidad.trim(),
        nombres: formData.nombres.trim(),
        apellidos: formData.apellidos.trim(),
        telefono: formData.telefono.trim() || undefined,
        correo: formData.correo.trim(),
        password: formData.password,
      });

      setSuccessAlert(true);
      if (onSuccess) {
        onSuccess(user);
      }
    } catch (err: any) {
      const msg = err.message || '';
      if (msg.includes('documento de identidad')) {
        setErrors((prev) => ({ ...prev, documento_identidad: msg }));
      } else if (msg.includes('correo electrónico')) {
        setErrors((prev) => ({ ...prev, correo: msg }));
      } else {
        setServerErrorAlert(true);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormFilled =
    formData.nombres.trim() !== '' &&
    formData.apellidos.trim() !== '' &&
    formData.documento_identidad.trim() !== '' &&
    formData.correo.trim() !== '' &&
    formData.password !== '' &&
    formData.confirmPassword !== '';

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="flex flex-col w-full max-w-[540px] items-center gap-3.5 mt-0.5"
    >
      <div className="flex flex-col items-center gap-1 w-full text-center">
        <h1
          id="signup-heading"
          className="font-bold text-[#1f2041] text-2xl sm:text-[28px] tracking-tight"
          style={{ fontFamily: "'Quicksand', sans-serif" }}
        >
          Crea tu cuenta
        </h1>
        <p
          className="font-normal text-xs sm:text-sm text-[rgba(31,32,65,0.5)] max-w-[440px] leading-relaxed"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          Por favor ingrese los siguientes datos para proceder con su solicitud de acceso
        </p>
      </div>

      {/* Alerta de Éxito */}
      {successAlert && (
        <div
          role="alert"
          aria-live="polite"
          className="w-full flex items-start justify-between gap-3 p-3 rounded-xl border border-[#6ee7b7] bg-[#f0fdf4] transition-all"
        >
          <div className="flex items-start gap-2.5">
            <div className="w-5 h-5 rounded-full bg-[#10b981] flex items-center justify-center shrink-0 mt-0.5">
              <FontAwesomeIcon icon={faCheck} size='2xs' color='#FFF' />
            </div>
            <div className="flex flex-col text-left">
              <h3 className="font-bold text-xs sm:text-sm text-[#065f46]" style={{ fontFamily: "'Montserrat', sans-serif" }}>
                ¡Registro exitoso!
              </h3>
              <p className="text-[11px] sm:text-xs text-[#047857] mt-0.5 leading-snug">
                Tu solicitud de acceso ha sido enviada al administrador del sistema, por favor, espera a que sea confirmada para comenzar.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setSuccessAlert(false)}
            aria-label="Cerrar notificación"
            className="flex items-center text-slate-400 hover:text-slate-600 transition-colors p-0.5 bg-transparent"
          >
            <FontAwesomeIcon icon={faXmark} size='2xs' color='var(--dark-shade-25)' />
          </button>
        </div>
      )}

      {/* Alerta de Error del Servidor */}
      {serverErrorAlert && (
        <div
          role="alert"
          aria-live="polite"
          className="w-full flex items-start justify-between gap-3 p-3 rounded-xl border border-[#F72C2C] bg-[#fef2f2] transition-all"
        >
          <div className="flex items-start gap-2.5">
            <div className="p-1 rounded-md bg-[#F72C2C] flex items-center justify-center">
              <FontAwesomeIcon icon={faXmark} color='#FFF' size='2xs' />
            </div>
            <div className="flex flex-col text-left">
              <h3 className="font-bold text-xs sm:text-sm text-[#991b1b]" style={{ fontFamily: "'Montserrat', sans-serif" }}>
                Error Interno del Servidor
              </h3>
              <p className="text-[11px] sm:text-xs text-[#b91c1c] mt-0.5 leading-snug">
                Ocurrió un error inesperado al procesar la solicitud en el servidor.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setServerErrorAlert(false)}
            aria-label="Cerrar notificación de error"
            className="flex items-center text-slate-400 hover:text-slate-600 transition-colors p-0.5 bg-transparent"
          >
            <FontAwesomeIcon icon={faXmark} size='2xs' color='var(--dark-shade-25)' />
          </button>
        </div>
      )}

      <div className="flex flex-col gap-2.5 w-full">
        {/* Fila 1: NOMBRE(S) y APELLIDOS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full">
          <div className="flex flex-col w-full">
            <label
              htmlFor="nombres"
              className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : errors.nombres ? fieldCardError : fieldCardEnabled
                }`}
            >
              <span
                className="font-bold text-[10px] sm:text-[11px] tracking-[0.06px] uppercase"
                style={{ fontFamily: "'Montserrat', sans-serif" }}
              >
                NOMBRE(S)
              </span>
              <input
                id="nombres"
                name="nombres"
                type="text"
                autoComplete="given-name"
                placeholder="Ej. María Fernanda"
                value={formData.nombres}
                onChange={(e) => handleChange('nombres', e.target.value)}
                disabled={isSubmitting}
                className={`${inputBase} ${isSubmitting ? 'text-[rgba(31,32,65,0.45)] cursor-not-allowed' : 'text-[#1f2041]'
                  }`}
                style={{ fontFamily: "'Quicksand', sans-serif" }}
              />
            </label>
            {errors.nombres && (
              <p className="text-red-500 text-xs mt-1 text-left font-normal pl-1" style={{ fontFamily: "'Quicksand', sans-serif" }}>
                {errors.nombres}
              </p>
            )}
          </div>

          <div className="flex flex-col w-full">
            <label
              htmlFor="apellidos"
              className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : errors.apellidos ? fieldCardError : fieldCardEnabled
                }`}
            >
              <span
                className="font-bold text-[10px] sm:text-[11px] tracking-[0.06px] uppercase"
                style={{ fontFamily: "'Montserrat', sans-serif" }}
              >
                APELLIDOS
              </span>
              <input
                id="apellidos"
                name="apellidos"
                type="text"
                autoComplete="family-name"
                placeholder="Ej. Castañeda Hernández"
                value={formData.apellidos}
                onChange={(e) => handleChange('apellidos', e.target.value)}
                disabled={isSubmitting}
                className={`${inputBase} ${isSubmitting ? 'text-[rgba(31,32,65,0.45)] cursor-not-allowed' : 'text-[#1f2041]'
                  }`}
                style={{ fontFamily: "'Quicksand', sans-serif" }}
              />
            </label>
            {errors.apellidos && (
              <p className="text-red-500 text-xs mt-1 text-left font-normal pl-1" style={{ fontFamily: "'Montserrat', sans-serif" }}>
                {errors.apellidos}
              </p>
            )}
          </div>
        </div>

        {/* Fila 2: NÚMERO DE IDENTIFICACIÓN y NÚMERO TELEFÓNICO */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full">
          <div className="flex flex-col w-full">
            <label
              htmlFor="documento_identidad"
              className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : errors.documento_identidad ? fieldCardError : fieldCardEnabled
                }`}
            >
              <span
                className="font-bold text-[10px] sm:text-[11px] tracking-[0.06px] uppercase"
                style={{ fontFamily: "'Montserrat', sans-serif" }}
              >
                NÚMERO DE IDENTIFICACIÓN
              </span>
              <input
                id="documento_identidad"
                name="documento_identidad"
                type="text"
                inputMode="numeric"
                maxLength={8}
                placeholder="00000000"
                value={formData.documento_identidad}
                onChange={(e) => handleChange('documento_identidad', e.target.value.replace(/\D/g, ''))}
                disabled={isSubmitting}
                className={`${inputBase} ${isSubmitting ? 'text-[rgba(31,32,65,0.45)] cursor-not-allowed' : 'text-[#1f2041]'
                  }`}
                style={{ fontFamily: "'Quicksand', sans-serif" }}
              />
            </label>
            {errors.documento_identidad && (
              <p className="text-red-500 text-xs mt-1 text-left font-normal pl-1" style={{ fontFamily: "'Montserrat', sans-serif" }}>
                {errors.documento_identidad}
              </p>
            )}
          </div>

          <div className="flex flex-col w-full">
            <label
              htmlFor="telefono"
              className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : fieldCardEnabled}`}
            >
              <span
                className="font-bold text-[10px] sm:text-[11px] tracking-[0.06px] uppercase"
                style={{ fontFamily: "'Montserrat', sans-serif" }}
              >
                NÚMERO TELEFÓNICO
              </span>
              <input
                id="telefono"
                name="telefono"
                type="tel"
                autoComplete="tel"
                placeholder="Ej. (+52) 555-152-3056"
                value={formData.telefono}
                onChange={(e) => handleChange('telefono', e.target.value)}
                disabled={isSubmitting}
                className={`${inputBase} ${isSubmitting ? 'text-[rgba(31,32,65,0.45)] cursor-not-allowed' : 'text-[#1f2041]'
                  }`}
                style={{ fontFamily: "'Quicksand', sans-serif" }}
              />
            </label>
          </div>
        </div>

        {/* Fila 3: CORREO */}
        <div className="flex flex-col w-full">
          <label
            htmlFor="correo"
            className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : errors.correo ? fieldCardError : fieldCardEnabled
              }`}
          >
            <span
              className="font-bold text-[10px] sm:text-[11px] tracking-[0.06px] uppercase"
              style={{ fontFamily: "'Montserrat', sans-serif" }}
            >
              CORREO
            </span>
            <input
              id="correo"
              name="correo"
              type="email"
              autoComplete="email"
              placeholder="email@example.com"
              value={formData.correo}
              onChange={(e) => handleChange('correo', e.target.value)}
              disabled={isSubmitting}
              className={`${inputBase} ${isSubmitting ? 'text-[rgba(31,32,65,0.45)] cursor-not-allowed' : 'text-[#1f2041]'
                }`}
              style={{ fontFamily: "'Quicksand', sans-serif" }}
            />
          </label>
          {errors.correo && (
            <p className="text-red-500 text-xs mt-1 text-left font-normal pl-1" style={{ fontFamily: "'Montserrat', sans-serif" }}>
              {errors.correo}
            </p>
          )}
        </div>

        {/* Fila 4: CONTRASEÑA */}
        <div className="flex flex-col w-full gap-1">
          <div
            className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : errors.password ? fieldCardError : fieldCardEnabled
              }`}
          >
            <div className="flex items-center w-full">
              <div className="flex flex-col w-full">
                <span
                  className="font-bold text-[10px] sm:text-[11px] tracking-[0.06px] uppercase"
                  style={{ fontFamily: "'Montserrat', sans-serif" }}
                >
                  CONTRASEÑA
                </span>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  placeholder="••••••••••••"
                  value={formData.password}
                  onChange={(e) => handleChange('password', e.target.value)}
                  disabled={isSubmitting}
                  className={`${inputBase} ${isSubmitting ? 'text-[rgba(31,32,65,0.45)] cursor-not-allowed' : 'text-[#1f2041]'
                    }`}
                  style={{ fontFamily: "'Quicksand', sans-serif" }}
                />
              </div>
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                disabled={isSubmitting}
                aria-label={showPassword ? 'Ocultar contraseña' : 'Ver contraseña'}
                className="bg-transparent flex items-center text-slate-400 hover:text-slate-600 focus:outline-none p-1 shrink-0"
              >
                {showPassword ? (
                  <FontAwesomeIcon icon={faEye} />
                ) : (
                  <FontAwesomeIcon icon={faEyeSlash} />
                )}
              </button>
            </div>
          </div>
          {errors.password && (
            <p className="text-red-500 text-xs mt-1 text-left font-normal pl-1" style={{ fontFamily: "'Montserrat', sans-serif" }}>
              {errors.password}
            </p>
          )}
        </div>

        {/* Fila 5: CONFIRMA TU CONTRASEÑA */}
        <div className="flex flex-col w-full gap-1">
          <div
            className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : errors.confirmPassword ? fieldCardError : fieldCardEnabled
              }`}
          >
            <div className="flex items-center w-full">
              <div className="flex flex-col w-full">
                <span
                  className="font-bold text-[10px] sm:text-[11px] tracking-[0.06px] uppercase"
                  style={{ fontFamily: "'Montserrat', sans-serif" }}
                >
                  CONFIRMA TU CONTRASEÑA
                </span>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  placeholder="••••••••••••"
                  value={formData.confirmPassword}
                  onChange={(e) => handleChange('confirmPassword', e.target.value)}
                  disabled={isSubmitting}
                  className={`${inputBase} ${isSubmitting ? 'text-[rgba(31,32,65,0.45)] cursor-not-allowed' : 'text-[#1f2041]'
                    }`}
                  style={{ fontFamily: "'Quicksand', sans-serif" }}
                />
              </div>
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                disabled={isSubmitting}
                aria-label={showConfirmPassword ? 'Ocultar confirmación de contraseña' : 'Ver confirmación de contraseña'}
                className="bg-transparent flex items-center text-slate-400 hover:text-slate-600 focus:outline-none p-1 shrink-0"
              >
                {showConfirmPassword ? (
                  <FontAwesomeIcon icon={faEye} />
                ) : (
                  <FontAwesomeIcon icon={faEyeSlash} />
                )}
              </button>
            </div>
          </div>
          {errors.confirmPassword && (
            <p className="text-red-500 text-xs mt-1 text-left font-normal pl-1" style={{ fontFamily: "'Montserrat', sans-serif" }}>
              {errors.confirmPassword}
            </p>
          )}
        </div>
      </div>

      <div className="flex flex-col gap-3 w-full mt-2">
        <Button
          type="submit"
          text="Enviar solicitud"
          loading={isSubmitting}
          disabled={isSubmitting || !isFormFilled}
        />

        {/* Separador OR */}
        <div className="flex items-center gap-3 w-full my-0.5">
          <div className="flex-1 h-px bg-[rgba(31,32,65,0.1)]" />
          <span
            className="font-bold text-xs text-[rgba(31,32,65,0.4)] tracking-wider"
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          >
            OR
          </span>
          <div className="flex-1 h-px bg-[rgba(31,32,65,0.1)]" />
        </div>
      </div>

      <footer className="flex items-center justify-center gap-1.5 w-full text-xs sm:text-sm">
        <span
          className="font-normal text-[rgba(31,32,65,0.5)]"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          ¿Ya tiene una cuenta?
        </span>
        <button
          type="button"
          onClick={onNavigateToLogin || (() => { window.location.href = '/login'; })}
          className="bg-transparent font-bold text-[#204a79] hover:text-[#18395d] hover:underline focus-visible:underline transition-colors cursor-pointer"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          Inicie sesión
        </button>
      </footer>
    </form>
  );
}
