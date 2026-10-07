import type { JSX } from 'react';
import { useNavigate } from 'react-router-dom';
import { SignUpForm } from '../components/auth/SignUpForm';
import { TestimonialSection } from '../components/login/TestimonialSection';
import logo from '../assets/login/logo.png';
import '../styles/login.css';

export default function SignUp(): JSX.Element {
  const navigate = useNavigate();

  return (
    <main className="login-page flex min-h-screen relative bg-[#f5f7fb] overflow-hidden">
      {/* Sección lateral testimonial con fondo de banner médico */}
      <TestimonialSection />

      {/* Sección interactiva de registro */}
      <section
        aria-labelledby="signup-heading"
        className="relative w-full md:w-1/2 min-h-screen flex flex-col items-center justify-center py-6 px-6 sm:px-12 lg:px-16 z-10 overflow-y-auto"
      >
        {/* Orbes de ambiente difuminados de fondo */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden -z-10">
          <div className="login-orb-1" />
          <div className="login-orb-2" />
          <div className="login-orb-3" />
        </div>

        <div className="inline-flex items-center justify-center px-4 py-1 mb-1 text-center">
          <p
            className="font-bold text-xs sm:text-sm tracking-[1.2px] uppercase text-[rgba(31,32,65,0.5)]"
            style={{ fontFamily: "'Montserrat', sans-serif" }}
          >
            SISTEMA AUTÓNOMO DE TRIAJE Y ENRUTAMIENTO CLÍNICO
          </p>
        </div>

        <div className="my-1 flex justify-center items-center">
          <img
            className="w-[220px] sm:w-[260px] md:w-[300px] h-auto aspect-[1.08] object-contain drop-shadow-sm select-none"
            alt="MediFlow"
            src={logo}
          />
        </div>

        <SignUpForm onNavigateToLogin={() => navigate('/login')} />
      </section>
    </main>
  );
}
