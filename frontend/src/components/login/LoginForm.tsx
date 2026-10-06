import type { FormEvent, JSX } from 'react'

const fieldCardBase =
  'flex flex-col items-start px-4 py-2 rounded-lg border transition-all shadow-[0_2px_8px_rgba(31,32,65,0.03)]'
const fieldCardEnabled =
  'bg-white border-[rgba(31,32,65,0.12)] focus-within:border-[#2c5282] focus-within:ring-2 focus-within:ring-[#2c5282]/20 cursor-text'
const fieldCardDisabled =
  'bg-[#f1f3f7] border-[rgba(31,32,65,0.08)] opacity-80 cursor-not-allowed'
const inputBase =
  'w-full font-medium text-sm placeholder:text-[rgba(31,32,65,0.35)] outline-none bg-transparent pt-0.5'

interface LoginFormProps {
  documentoIdentidad: string
  password: string
  onDocumentoChange: (value: string) => void
  onPasswordChange: (value: string) => void
  onSubmit: (e: FormEvent<HTMLFormElement>) => void
  onRegister: () => void
  isSubmitting: boolean
  error: string
}

export function LoginForm({
  documentoIdentidad,
  password,
  onDocumentoChange,
  onPasswordChange,
  onSubmit,
  onRegister,
  isSubmitting,
  error,
}: LoginFormProps): JSX.Element {
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
        <div
          aria-live="polite"
          role="alert"
          className="w-full text-sm font-medium text-red-600 px-4 py-2 bg-red-50/90 border border-red-200 rounded-lg shadow-sm"
        >
          {error}
        </div>
      )}

      <div className="flex flex-col gap-3 w-full">
        {/* Campo DNI / CORREO */}
        <label
          htmlFor="documentoIdentidad"
          className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : fieldCardEnabled}`}
        >
          <span
            className="font-bold text-[11px] tracking-[0.06px] text-[rgba(31,32,65,0.5)] uppercase"
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          >
            Correo
          </span>
          <input
            id="documentoIdentidad"
            name="documentoIdentidad"
            type="text"
            inputMode="numeric"
            maxLength={8}
            autoComplete="username"
            aria-label="DNI"
            placeholder="email@example.com"
            value={documentoIdentidad}
            onChange={(e) => onDocumentoChange(e.target.value)}
            disabled={isSubmitting}
            className={`${inputBase} ${isSubmitting ? 'text-[rgba(31,32,65,0.45)] cursor-not-allowed' : 'text-[#1f2041]'}`}
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          />
        </label>

        {/* Campo CONTRASEÑA */}
        <label
          htmlFor="password"
          className={`${fieldCardBase} ${isSubmitting ? fieldCardDisabled : fieldCardEnabled}`}
        >
          <span
            className="font-bold text-[11px] tracking-[0.06px] text-[rgba(31,32,65,0.5)] uppercase"
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          >
            CONTRASEÑA
          </span>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            aria-label="CONTRASEÑA"
            placeholder="••••••••••••"
            value={password}
            onChange={(e) => onPasswordChange(e.target.value)}
            disabled={isSubmitting}
            className={`${inputBase} ${isSubmitting ? 'text-[rgba(31,32,65,0.45)] cursor-not-allowed' : 'text-[#1f2041]'}`}
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          />
        </label>
      </div>

      <div className="flex flex-col gap-3.5 w-full mt-1">
        <button
          type="submit"
          disabled={isSubmitting}
          aria-busy={isSubmitting}
          className={`flex h-[44px] items-center justify-center w-full rounded-lg transition-colors duration-200 shadow-sm focus-visible:ring-2 focus-visible:ring-[#2c5282] focus-visible:ring-offset-2 ${
            isSubmitting
              ? 'bg-[#94a3b8] text-white cursor-not-allowed'
              : 'bg-[#2c5282] hover:bg-[#1f3e66] active:bg-[#172e4b] text-white cursor-pointer'
          }`}
        >
          {isSubmitting ? (
            <>
              <span
                data-testid="login-spinner"
                aria-hidden="true"
                className="inline-block h-5 w-5 rounded-full border-2 border-solid border-white/40 border-t-white animate-spin"
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

      <footer className="flex items-center justify-center gap-1.5 w-full text-sm">
        <span
          className="font-normal text-[rgba(31,32,65,0.5)]"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          ¿No tienes una cuenta?
        </span>
        <button
          type="button"
          onClick={onRegister}
          className="font-bold text-[#2c5282] hover:text-[#1a365d] hover:underline focus-visible:underline transition-colors cursor-pointer"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          Regístrate
        </button>
      </footer>
    </form>
  )
}
