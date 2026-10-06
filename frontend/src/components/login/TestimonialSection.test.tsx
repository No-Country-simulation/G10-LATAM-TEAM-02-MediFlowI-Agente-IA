import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TestimonialSection } from './TestimonialSection'

describe('TestimonialSection (US4)', () => {
  it('renderiza la cita del testimonio', () => {
    render(<TestimonialSection />)
    expect(screen.getByText(/Simplemente la plataforma/i)).toBeInTheDocument()
  })

  it('no renderiza autor ni cargo (omite Dr. Alejandro Torres)', () => {
    render(<TestimonialSection />)
    expect(screen.queryByText('Dr. Alejandro Torres')).not.toBeInTheDocument()
    expect(screen.queryByText('Director de Operaciones Clínicas')).not.toBeInTheDocument()
  })

  it('tiene clase hidden para ocultarse en móvil', () => {
    const { container } = render(<TestimonialSection />)
    const section = container.querySelector('section')
    expect(section).toBeTruthy()
    expect(section?.className).toContain('hidden')
  })

  it('tiene clase md:flex para mostrarse en desktop', () => {
    const { container } = render(<TestimonialSection />)
    const section = container.querySelector('section')
    expect(section?.className).toContain('md:flex')
  })

  it('tiene aria-label de testimonio', () => {
    const { container } = render(<TestimonialSection />)
    const section = container.querySelector('section')
    expect(section?.getAttribute('aria-label')).toBe('Testimonio de cliente')
  })
})
