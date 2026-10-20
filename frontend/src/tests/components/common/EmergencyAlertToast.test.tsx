import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import EmergencyAlertToast from '../../../components/common/EmergencyAlertToast'
import type { AlertaGuardia } from '../../../services/alertStreamService'

const mockAlerts: AlertaGuardia[] = [
  {
    id: 'alert-1',
    documento_id: 'DOC-EMERGENCIA-001',
    prioridad: 'Urgente',
    fecha: '2026-10-20T12:00:00Z',
    mensaje: 'Paciente con dolor torácico opresivo y sospecha de IAM.',
  },
]

describe('EmergencyAlertToast - Alertas de Guardia en Tiempo Real (FE-15 / Issue #72)', () => {
  it('no renderiza nada si la lista de alertas está vacía', () => {
    const { container } = render(
      <EmergencyAlertToast
        alerts={[]}
        onDismiss={vi.fn()}
        soundEnabled={true}
        onToggleSound={vi.fn()}
      />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renderiza la tarjeta de alerta con datos clínicos y botón de atención', () => {
    render(
      <MemoryRouter>
        <EmergencyAlertToast
          alerts={mockAlerts}
          onDismiss={vi.fn()}
          soundEnabled={true}
          onToggleSound={vi.fn()}
        />
      </MemoryRouter>
    )

    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.getByText('Doc: DOC-EMERGENCIA-001')).toBeInTheDocument()
    expect(screen.getByText(/dolor torácico opresivo/i)).toBeInTheDocument()
    expect(screen.getByText('Atender caso')).toBeInTheDocument()
  })

  it('invoca onDismiss al hacer click en el botón de cerrar', async () => {
    const handleDismiss = vi.fn()
    const user = userEvent.setup()

    render(
      <MemoryRouter>
        <EmergencyAlertToast
          alerts={mockAlerts}
          onDismiss={handleDismiss}
          soundEnabled={true}
          onToggleSound={vi.fn()}
        />
      </MemoryRouter>
    )

    const dismissBtn = screen.getByLabelText('Descartar alerta')
    await user.click(dismissBtn)

    expect(handleDismiss).toHaveBeenCalledWith('alert-1')
  })

  it('permite alternar el sonido de alerta', async () => {
    const handleToggleSound = vi.fn()
    const user = userEvent.setup()

    render(
      <MemoryRouter>
        <EmergencyAlertToast
          alerts={mockAlerts}
          onDismiss={vi.fn()}
          soundEnabled={true}
          onToggleSound={handleToggleSound}
        />
      </MemoryRouter>
    )

    const soundBtn = screen.getByTitle('Silenciar alertas acústicas')
    await user.click(soundBtn)

    expect(handleToggleSound).toHaveBeenCalledTimes(1)
  })
})
