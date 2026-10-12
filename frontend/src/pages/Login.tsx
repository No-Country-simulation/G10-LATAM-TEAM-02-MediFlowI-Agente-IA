import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import type { FormEvent, JSX } from "react";
import { useAuth } from "../hooks/useAuth";
import { LoginForm } from "../components/login/LoginForm";
import { TestimonialSection } from "../components/login/TestimonialSection";
import logo from "../assets/login/logo.png";
import "../styles/login.css";

const Login = (): JSX.Element => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = location.state?.from?.pathname || "/dashboard";

  const handleChange = (field: string, value: string) => {
    if (field === "email") {
      setEmail(value);
    } else if (field === "password") {
      setPassword(value);
    }

    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }));
    }
    if (error) {
      setError("");
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!email.trim()) {
      newErrors.email = "Por favor ingrese su correo electrónico.";
    } else if (!emailRegex.test(email.trim())) {
      newErrors.email = "Por favor, introduzca una dirección de correo electrónico válida";
    }

    if (!password.trim()) {
      newErrors.password = "Por favor ingrese su contraseña.";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await login(email.trim(), password);
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
          email={email}
          password={password}
          onChange={handleChange}
          onSubmit={handleSubmit}
          onRegister={handleRegister}
          isSubmitting={isSubmitting}
          error={error}
          errors={errors}
        />
      </section>
    </main>
  );
};

export default Login;
