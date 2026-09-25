import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { FaStethoscope, FaUser, FaLock, FaSignInAlt, FaInfoCircle } from "react-icons/fa";

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [username, setUsername] = useState("12345678");
  const [password, setPassword] = useState("admin");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = location.state?.from?.pathname || "/dashboard";

  const handleSubmit = async (e) => {
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
    } catch (err) {
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

          <div className="alert alert-info py-2 px-3 small rounded-3 mb-4 d-flex align-items-center">
            <FaInfoCircle className="me-2 flex-shrink-0 fs-5" />
            <div>
              <strong>Credenciales de acceso:</strong>
              <div className="font-monospace">DNI: <strong>12345678</strong> | Clave: <strong>admin</strong></div>
            </div>
          </div>

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
