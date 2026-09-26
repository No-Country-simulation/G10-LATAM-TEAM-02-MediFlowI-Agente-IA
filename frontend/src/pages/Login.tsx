import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { FaStethoscope, FaUser, FaLock, FaSignInAlt } from "react-icons/fa";
import type { FormEvent } from 'react'

const DEVELOPMENT_ADMIN_CREDENTIALS = {
  documentoIdentidad: '12345678',
  password: 'MediFlow#Admin2026',
} as const

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = location.state?.from?.pathname || "/dashboard";

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const result = await login(username, password);
      if (result.success) {
        navigate(from, { replace: true });
      } else {
        setError(result.message || "Credenciales incorrectas.");
      }
    } catch {
      setError("Error al procesar el inicio de sesión.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light p-3">
      <div className="card border-0 shadow-lg rounded-4 overflow-hidden" style={{ maxWidth: "450px", width: "100%" }}>
        {/* Header */}
        <div className="bg-primary text-white text-center p-4">
          <div className="d-inline-flex p-3 bg-white bg-opacity-20 rounded-circle mb-3">
            <FaStethoscope size={42} className="text-white" />
          </div>
          <h3 className="fw-bold mb-1">MediFlow</h3>
          <p className="text-light opacity-75 small mb-0">Sistema de Triaje Inteligente de Documentos Clínicos</p>
        </div>

        {/* Body */}
        <div className="card-body p-4 p-md-5">
          <h5 className="fw-bold text-dark text-center mb-4">Iniciar Sesión</h5>

          {error && (
            <div className="alert alert-danger py-2 px-3 small rounded-3 mb-3" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label className="form-label fw-semibold text-muted small">DNI</label>
              <div className="input-group">
                <span className="input-group-text bg-light border-end-0 text-muted">
                  <FaUser />
                </span>
                <input
                  type="text"
                  className="form-control border-start-0 ps-0"
                  placeholder="Ingrese su DNI"
                  inputMode="numeric"
                  autoComplete="username"
                  maxLength={8}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="mb-4">
              <label className="form-label fw-semibold text-muted small">Contraseña</label>
              <div className="input-group">
                <span className="input-group-text bg-light border-end-0 text-muted">
                  <FaLock />
                </span>
                <input
                  type="password"
                  autoComplete="current-password"
                  className="form-control border-start-0 ps-0"
                  placeholder="Ingrese su contraseña"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary w-100 py-2.5 fw-bold shadow-sm rounded-3 d-flex align-items-center justify-content-center"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Ingresando...
                </>
              ) : (
                <>
                  <FaSignInAlt className="me-2" /> INGRESAR
                </>
              )}
            </button>
          </form>

          {import.meta.env.DEV && (
            <aside className="alert alert-info border-0 rounded-3 mt-4 mb-0" role="note">
              <p className="fw-semibold mb-2">Acceso inicial de desarrollo</p>
              <dl className="row small mb-3">
                <dt className="col-4">DNI</dt>
                <dd className="col-8 mb-1">
                  <code>{DEVELOPMENT_ADMIN_CREDENTIALS.documentoIdentidad}</code>
                </dd>
                <dt className="col-4">Contraseña</dt>
                <dd className="col-8 mb-0">
                  <code>{DEVELOPMENT_ADMIN_CREDENTIALS.password}</code>
                </dd>
              </dl>
              <button
                type="button"
                className="btn btn-sm btn-outline-primary w-100"
                onClick={() => {
                  setUsername(DEVELOPMENT_ADMIN_CREDENTIALS.documentoIdentidad)
                  setPassword(DEVELOPMENT_ADMIN_CREDENTIALS.password)
                  setError('')
                }}
              >
                Completar credenciales
              </button>
            </aside>
          )}
        </div>

        {/* Footer */}
        <div className="card-footer bg-light text-center py-3 border-0 text-muted small">
          MediFlow © 2026 - Hackathon IA
        </div>
      </div>
    </div>
  );
};

export default Login;
