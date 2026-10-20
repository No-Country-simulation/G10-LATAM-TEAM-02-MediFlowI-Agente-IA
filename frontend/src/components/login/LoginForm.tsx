import { useState, type FormEvent, type JSX } from 'react'
import { LuEye, LuEyeOff } from 'react-icons/lu'

const fieldCardBase =
  'flex flex-col items-start px-3.5 py-2 rounded-xl border transition-all shadow-2xs w-full'
const fieldCardEnabled =
  'bg-white border-slate-200/90 hover:border-slate-300 focus-within:border-[#204A79] focus-within:ring-2 focus-within:ring-[#204A79]/15 cursor-text'
const fieldCardDisabled =
  'bg-slate-50 border-slate-200 opacity-70 cursor-not-allowed'
const inputBase =
  'w-full font-medium text-sm placeholder:text-slate-400 outline-none bg-transparent pt-0.5'

interface LoginFormProps {
  email?: string
  password: string
  onEmailChange?: (value: string) => void
  onPasswordChange: (value: string) => void
  onSubmit: (e: FormEvent<HTMLFormElement>) => void
  onRegister: () => void
  isSubmitting: boolean
  error: string
  // Retrocompatibilidad
  documentoIdentidad?: string
  onDocumentoChange?: (value: string) => void
}

export function LoginForm({
  email,
  password,
  onEmailChange,
  onPasswordChange,
  onSubmit,
  onRegister,
  isSubmitting,
  error,
  documentoIdentidad,
  onDocumentoChange,
}: LoginFormProps): JSX.Element {
  const [showPassword, setShowPassword] = useState(false)
  const emailValue = email ?? documentoIdentidad ?? ''

  const handleEmailChange = (value: string) => {
    if (onEmailChange) onEmailChange(value)
    if (onDocumentoChange) onDocumentoChange(value)
  }

  return (
    <form
      onSubmit={onSubmit}
      noValidate
      className="flex flex-col w-full items-center gap-3.5 mt-1"
    >
      <div className="flex flex-col items-center gap-1 w-full text-center mb-1">
        <h1
          id="welcome-heading"
          className="font-bold text-slate-900 text-2xl sm:text-[26px] tracking-tight m-0"
          style={{ fontFamily: "'Quicksand', sans-serif" }}
        >
          Bienvenido
        </h1>
        <p
          className="font-normal text-xs sm:text-sm text-slate-500 m-0"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          ¿Con qué comenzaremos el día de hoy?
        </p>
      </div>

      {error && (
        <div
          aria-live="polite"
          role="alert"
          className="w-full text-xs sm:text-sm font-medium text-red-700 px-3.5 py-2 bg-red-50 border border-red-200 rounded-xl shadow-2xs"
        >
          {error}
        </div>
      )}

      <div className="flex flex-col gap-2.5 w-full">
        {/* Campo CORREO ELECTRÓNICO */}
        <label
          htmlFor="email"
          className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : fieldCardEnabled}`}
        >
          <span
            className="font-bold text-[10px] sm:text-[11px] tracking-wider text-slate-400 uppercase"
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          >
            Correo Electrónico
          </span>
          <input
            id="email"
            name="email"
            type="text"
            autoComplete="username"
            aria-label="Correo"
            placeholder="email@example.com"
            value={emailValue}
            onChange={(e) => handleEmailChange(e.target.value)}
            disabled={isSubmitting}
            className={`${inputBase} ${isSubmitting ? 'text-slate-400 cursor-not-allowed' : 'text-slate-800'}`}
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          />
        </label>

        {/* Campo CONTRASEÑA */}
        <label
          htmlFor="password"
          className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : fieldCardEnabled}`}
        >
          <span
            className="font-bold text-[10px] sm:text-[11px] tracking-wider text-slate-400 uppercase"
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          >
            CONTRASEÑA
          </span>
          <div className="flex items-center w-full gap-2">
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              aria-label="CONTRASEÑA"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => onPasswordChange(e.target.value)}
              disabled={isSubmitting}
              className={`${inputBase} ${isSubmitting ? 'text-slate-400 cursor-not-allowed' : 'text-slate-800'}`}
              style={{ fontFamily: "'Montserrat', sans-serif" }}
            />
            <button
              type="button"
              onClick={() => setShowPassword((prev) => !prev)}
              disabled={isSubmitting}
              aria-label={showPassword ? 'Ocultar clave' : 'Mostrar clave'}
              className="bg-transparent border-0 p-1 text-slate-400 hover:text-slate-600 cursor-pointer flex items-center shrink-0"
            >
              {showPassword ? <LuEyeOff size={16} /> : <LuEye size={16} />}
            </button>
          </div>
        </label>
      </div>

      <div className="flex flex-col gap-3 w-full mt-1">
        <button
          type="submit"
          disabled={isSubmitting}
          aria-busy={isSubmitting}
          className={`flex h-[42px] items-center justify-center w-full rounded-xl transition-all duration-200 shadow-xs focus-visible:ring-2 focus-visible:ring-[#204A79] focus-visible:ring-offset-2 border-0 ${
            isSubmitting
              ? 'bg-slate-400 text-white cursor-not-allowed'
              : 'bg-[#204A79] hover:bg-[#153457] active:bg-[#0e243f] text-white cursor-pointer'
          }`}
        >
          {isSubmitting ? (
            <>
              <span
                data-testid="login-spinner"
                aria-hidden="true"
                className="inline-block h-4 w-4 rounded-full border-2 border-solid border-white/40 border-t-white animate-spin"
              />
              <span className="sr-only">Ingresando...</span>
            </>
          ) : (
            <span
              className="font-bold text-white text-sm tracking-wide"
              style={{ fontFamily: "'Montserrat', sans-serif" }}
            >
              Iniciar sesión
            </span>
          )}
        </button>
      </div>

      <div className="w-full border-t border-slate-200/80 my-1" />

      <footer className="flex items-center justify-center gap-1.5 w-full text-xs sm:text-sm text-slate-600">
        <span
          className="font-normal"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          ¿No tienes una cuenta?
        </span>
        <button
          type="button"
          onClick={onRegister}
          className="bg-transparent border-0 p-0 font-bold text-[#204A79] hover:text-[#153457] hover:underline focus-visible:underline transition-colors cursor-pointer"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          Regístrate
        </button>
      </footer>
    </form>
  )
}
