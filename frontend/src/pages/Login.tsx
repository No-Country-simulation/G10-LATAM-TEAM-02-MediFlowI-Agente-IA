import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { LoginForm } from "../components/login/LoginForm";
import { TestimonialSection } from "../components/login/TestimonialSection";
import logo from "../assets/login/logo.png";
import "../styles/login.css";
import type { FormEvent, JSX } from "react";

const Login = (): JSX.Element => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [documentoIdentidad, setDocumentoIdentidad] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = location.state?.from?.pathname || "/dashboard";

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    if (!documentoIdentidad.trim() || !password.trim()) {
      setError("Por favor complete todos los campos.");
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await login(documentoIdentidad, password);
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

  const handleRegister = () => {
    navigate("/register");
  };

  return (
    <main className="login-page flex min-h-screen relative bg-[#f5f7fb] overflow-hidden">
      {/* Sección lateral testimonial con fondo de banner médico */}
      <TestimonialSection />

      {/* Sección interactiva de login */}
      <section
        aria-labelledby="welcome-heading"
        className="relative w-full md:w-1/2 min-h-screen flex flex-col items-center justify-center py-8 px-6 sm:px-12 lg:px-20 z-10"
      >
        {/* Orbes de ambiente difuminados de fondo */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden -z-10">
          <div className="login-orb-1" />
          <div className="login-orb-2" />
          <div className="login-orb-3" />
        </div>

        <div className="inline-flex items-center justify-center px-4 py-1.5 mb-1 text-center">
          <p
            className="font-bold text-xs sm:text-sm tracking-[1.2px] uppercase text-[rgba(31,32,65,0.5)]"
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          >
            SISTEMA AUTÓNOMO DE TRIAJE Y ENRUTAMIENTO CLÍNICO
          </p>
        </div>

        <div className="my-2.5 flex justify-center items-center">
          <img
            className="w-[260px] sm:w-[320px] md:w-[360px] h-auto aspect-[1.08] object-contain drop-shadow-sm select-none"
            alt="MediFlow"
            src={logo}
          />
        </div>

        <LoginForm
          documentoIdentidad={documentoIdentidad}
          password={password}
          onDocumentoChange={setDocumentoIdentidad}
          onPasswordChange={setPassword}
          onSubmit={handleSubmit}
          onRegister={handleRegister}
          isSubmitting={isSubmitting}
          error={error}
        />
      </section>
    </main>
  );
};

export default Login;
