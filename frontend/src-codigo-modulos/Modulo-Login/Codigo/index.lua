import { FormEvent, useState } from "react";
import image from "./image.svg";
import line from "./line.svg";
import logo1 from "./logo-1.png";

const backgroundOrbs = [
  "absolute top-[-100px] left-[200px] w-[600px] h-[600px] bg-[#ffe4ec] rounded-[300px] blur-[75px] opacity-50",
  "absolute top-[-200px] left-[600px] w-[700px] h-[700px] bg-[#e8dcff] rounded-[350px] blur-[90px] opacity-60",
  "absolute top-[100px] left-[1000px] w-[500px] h-[500px] bg-[#d6f5e3] rounded-[250px] blur-[70px] opacity-40",
];

export const MediflowLanding = (): JSX.Element => {
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitted(true);
  };

  return (
    <main className="flex flex-col h-[1080px] items-end relative bg-[#f5f7fb] border border-solid border-black overflow-hidden">
      {backgroundOrbs.map((className, index) => (
        <div key={index} aria-hidden="true" className={className} />
      ))}

      <div className="grid grid-cols-2 grid-rows-1 h-[1080px]">
        <section
          aria-label="Testimonio de cliente"
          className="relative row-[1_/_2] col-[1_/_2] w-full h-full flex flex-col items-start justify-end p-8 bg-[linear-gradient(180deg,rgba(31,32,65,0)_0%,rgba(31,32,65,0.8)_70%,rgba(31,32,65,0.98)_100%)]"
        >
          <div className="flex flex-col w-[896px] items-start gap-4 relative flex-[0_0_auto]">
            <blockquote className="relative self-stretch mt-[-1.00px] [font-family:'Quicksand-Bold',Helvetica] font-bold text-white text-2xl tracking-[0] leading-[33.6px]">
              &quot;Simplemente la plataforma que nuestro equipo médico
              necesitaba para optimizar la atención.&quot;
            </blockquote>
            <div className="flex flex-col items-start gap-0.5 relative self-stretch w-full flex-[0_0_auto]">
              <cite className="relative w-fit mt-[-1.00px] not-italic [font-family:'Montserrat-Bold',Helvetica] font-bold text-white text-base tracking-[0] leading-[normal]">
                Dr. Alejandro Torres
              </cite>
              <div className="relative w-[285px] [font-family:'Montserrat-Regular',Helvetica] font-normal text-[#ffffffb3] text-sm tracking-[0] leading-[normal]">
                Director de Operaciones Clínicas
              </div>
            </div>
          </div>
        </section>
        <section
          aria-labelledby="welcome-heading"
          className="relative row-[1_/_2] col-[2_/_3] w-full h-full flex flex-col items-center justify-center gap-10 pt-[100px] pb-10 px-20"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 relative flex-[0_0_auto]">
            <p className="relative w-fit mt-[-1.00px] [font-family:'Montserrat-Bold',Helvetica] font-bold text-dark-50 text-base tracking-[1.00px] leading-[normal]">
              SISTEMA AUTÓNOMO DE TRIAJE Y ENRUTAMIENTO CLÍNICO
            </p>
          </div>
          <img
            className="relative w-[400px] h-[369.01px] aspect-[1.08]"
            alt="MediFlow"
            src={logo1}
          />
          <form
            onSubmit={handleSubmit}
            noValidate
            className="flex flex-col max-w-[540px] w-[540px] items-start gap-6 relative flex-[0_0_auto]"
          >
            <div className="flex flex-col w-[540px] items-start gap-6 px-0.5 py-0 relative flex-[0_0_auto] rounded-3xl overflow-hidden shadow-[0px_16px_40px_#1f20410d]">
              <div className="flex flex-col items-start gap-6 relative self-stretch w-full flex-[0_0_auto]">
                <div className="flex flex-col items-center gap-2 relative self-stretch w-full flex-[0_0_auto]">
                  <h1
                    id="welcome-heading"
                    className="relative self-stretch mt-[-1.00px] [font-family:'Quicksand-Bold',Helvetica] font-bold text-[#1f2041] text-[32px] text-center tracking-[0] leading-[normal]"
                  >
                    Bienvenido
                  </h1>
                  <p className="relative self-stretch [font-family:'Montserrat-Regular',Helvetica] font-normal text-[#1f204180] text-base text-center tracking-[0] leading-[normal]">
                    ¿Con qué comenzaremos el día de hoy?
                  </p>
                </div>
                <div className="flex flex-col items-start gap-3 relative self-stretch w-full flex-[0_0_auto]">
                  {formFields.map((field) => (
                    <label
                      key={field.id}
                      htmlFor={field.id}
                      className="flex flex-col items-start gap-0.5 px-4 py-2 relative self-stretch w-full flex-[0_0_auto] bg-white rounded-lg border border-solid border-[#1f20411a] cursor-text"
                    >
                      <span className="relative w-fit mt-[-1.00px] [font-family:'Montserrat-Bold',Helvetica] font-bold text-[#1f204180] text-xs tracking-[0.06px] leading-[normal]">
                        {field.label}
                      </span>
                      <input
                        id={field.id}
                        name={field.id}
                        type={field.type}
                        defaultValue={field.defaultValue}
                        autoComplete={field.autoComplete}
                        aria-label={field.label}
                        className="relative self-stretch w-full [font-family:'Montserrat-Medium',Helvetica] font-medium text-variable-collection-dark-shade-50 text-sm tracking-[0] leading-[normal]"
                      />
                    </label>
                  ))}
                </div>
                <div className="flex flex-col items-start gap-4 relative self-stretch w-full flex-[0_0_auto]">
                  <button
                    type="submit"
                    className="flex h-[46px] items-center justify-center relative self-stretch w-full bg-[#2c528280] rounded-lg transition-colors hover:bg-[#2c5282a6] focus-visible:ring-2 focus-visible:ring-[#2c5282] focus-visible:ring-offset-2"
                  >
                    <span className="[font-family:'Montserrat-Bold',Helvetica] font-bold text-white text-sm tracking-[0] leading-[normal]">
                      Iniciar sesión
                    </span>
                  </button>
                  <div className="flex items-center gap-3 relative self-stretch w-full flex-[0_0_auto]">
                    <img
                      className="relative flex-1 grow h-px object-cover"
                      alt=""
                      aria-hidden="true"
                      src={line}
                    />
                    <span className="relative w-fit mt-[-1.00px] [font-family:'Montserrat-Bold',Helvetica] font-bold text-[#1f204180] text-sm tracking-[0] leading-[normal]">
                      OR
                    </span>
                    <img
                      className="relative flex-1 grow h-px object-cover"
                      alt=""
                      aria-hidden="true"
                      src={image}
                    />
                  </div>
                </div>
                <footer className="flex items-start justify-center gap-1 relative self-stretch w-full flex-[0_0_auto] bg-transparent">
                  <span className="relative w-fit mt-[-1.00px] [font-family:'Montserrat-Regular',Helvetica] font-normal text-[#1f204180] text-sm tracking-[0] leading-[normal]">
                    ¿No tienes una cuenta?
                  </span>
                  <button
                    type="button"
                    className="relative w-fit mt-[-1.00px] [font-family:'Montserrat-Bold',Helvetica] font-bold text-[#2c5282] text-sm tracking-[0] leading-[normal] focus-visible:underline"
                  >
                    Regístrate
                  </button>
                </footer>
                <p aria-live="polite" className="sr-only">
                  {submitted ? "Inicio de sesión enviado." : ""}
                </p>
              </div>
            </div>
          </form>
        </section>
      </div>
    </main>
  );
};
