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

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = location.state?.from?.pathname || "/dashboard";

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    const trimmedEmail = email.trim();
    const trimmedPassword = password.trim();

    if (!trimmedEmail || !trimmedPassword) {
      setError("Por favor complete todos los campos.");
      return;
    }

    if (!emailRegex.test(trimmedEmail)) {
      setError("Por favor, introduzca una dirección de correo electrónico válida");
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await login(trimmedEmail, trimmedPassword);
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
    navigate("/signup");
  };

  return (
    <main className="login-page flex min-h-screen relative bg-[#f5f7fb] overflow-hidden">
      {/* Sección lateral testimonial con fondo de banner médico */}
      <TestimonialSection />

      {/* Sección interactiva de login */}
      <section
        aria-labelledby="welcome-heading"
        className="relative w-full md:w-1/2 min-h-screen flex flex-col items-center justify-center py-6 px-4 sm:px-8 md:px-10 lg:px-12 z-10 overflow-y-auto"
      >
        {/* Orbes de ambiente difuminados de fondo */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden -z-10">
          <div className="login-orb-1" />
          <div className="login-orb-2" />
          <div className="login-orb-3" />
        </div>

        <div className="w-full max-w-[380px] flex flex-col items-center my-auto">
          {/* Badge institucional superior */}
          <div className="inline-flex items-center justify-center px-3.5 py-1 mb-2 text-center rounded-full bg-slate-200/60 border border-slate-300/40">
            <p
              className="font-bold text-[10px] sm:text-[11px] tracking-wider uppercase text-slate-600"
              style={{ fontFamily: "'Montserrat', sans-serif" }}
            >
              SISTEMA AUTÓNOMO DE TRIAJE Y ENRUTAMIENTO CLÍNICO
            </p>
          </div>

          {/* Logo compacto y armonioso de MediFlow */}
          <div className="my-2 flex justify-center items-center">
            <img
              className="w-[160px] sm:w-[180px] md:w-[200px] h-auto aspect-[1.08] object-contain drop-shadow-sm select-none"
              alt="MediFlow"
              src={logo}
            />
          </div>

          {/* Formulario de autenticación */}
          <LoginForm
            email={email}
            password={password}
            onEmailChange={setEmail}
            onPasswordChange={setPassword}
            onSubmit={handleSubmit}
            onRegister={handleRegister}
            isSubmitting={isSubmitting}
            error={error}
          />
        </div>
      </section>
    </main>
  );
};

export default Login;
