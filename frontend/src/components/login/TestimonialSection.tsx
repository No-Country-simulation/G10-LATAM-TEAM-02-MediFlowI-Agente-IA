import type { JSX } from 'react'
import banner from '../../assets/login/banner.jpg'

export function TestimonialSection(): JSX.Element {
  return (
    <section
      aria-label="Testimonio de cliente"
      className="hidden md:flex relative w-1/2 min-h-screen bg-cover bg-center bg-no-repeat flex-col items-start justify-end p-8 md:p-12 lg:p-16 z-10"
      style={{
        backgroundImage: `linear-gradient(180deg, rgba(31,32,65,0) 0%, rgba(31,32,65,0.7) 65%, rgba(31,32,65,0.96) 100%), url(${banner})`,
      }}
    >
      <div className="flex flex-col w-full max-w-[560px] items-start gap-4 relative z-10">
        <blockquote
          className="relative self-stretch font-bold text-white text-xl lg:text-2xl leading-[1.4]"
          style={{ fontFamily: "'Quicksand', sans-serif" }}
        >
          &ldquo;Simplemente la plataforma que nuestro equipo médico necesitaba para optimizar la atención.&rdquo;
        </blockquote>
      </div>
    </section>
  )
}
