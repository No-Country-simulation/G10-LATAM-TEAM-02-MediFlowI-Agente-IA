import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'

const mockNavigate = vi.fn()
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}))

let mockCurrentUser: {
  id: string
  nombres: string
  apellidos: string
  rol: 'ADMINISTRADOR' | 'OPERADOR' | 'AUDITOR' | 'SUPERVISOR'
  documento_identidad: string
} | null = {
  id: 'usr-1',
  nombres: 'Lucas',
  apellidos: 'Ramírez',
  rol: 'ADMINISTRADOR',
  documento_identidad: '12345678',
}

vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    user: mockCurrentUser,
    logout: vi.fn(),
  }),
}))

vi.mock('../api/documentsApi', () => ({
  documentsApi: {
    procesarDocumento: vi.fn().mockResolvedValue({
      documento_id: 'DOC-2026-ABCD',
    }),
  },
}))

import NewDocument from './NewDocument'
import { documentsApi } from '../api/documentsApi'

describe('NewDocument - Rediseño del Modal y Píldoras RBAC', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockCurrentUser = {
      id: 'usr-1',
      nombres: 'Lucas',
      apellidos: 'Ramírez',
      rol: 'ADMINISTRADOR',
      documento_identidad: '12345678',
    }
  })

  describe('US1: Navegación por Píldoras RBAC y Cabecera', () => {
    it('un ADMINISTRADOR visualiza las 3 opciones de píldora (Enrutamiento, Historial, Solicitudes)', () => {
      render(<NewDocument />)

      expect(screen.getByRole('button', { name: /enrutamiento/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /historial/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /solicitudes/i })).toBeInTheDocument()
    })

    it('un rol no administrador (OPERADOR) visualiza únicamente Enrutamiento e Historial', () => {
      mockCurrentUser = {
        id: 'usr-2',
        nombres: 'Carlos',
        apellidos: 'Gómez',
        rol: 'OPERADOR',
        documento_identidad: '87654321',
      }
      render(<NewDocument />)

      expect(screen.getByRole('button', { name: /enrutamiento/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /historial/i })).toBeInTheDocument()
      expect(screen.queryByRole('button', { name: /solicitudes/i })).not.toBeInTheDocument()
    })

    it('la píldora Historial redirige a /documentos y Solicitudes a /auditoria', () => {
      render(<NewDocument />)

      const btnHistorial = screen.getByRole('button', { name: /historial/i })
      fireEvent.click(btnHistorial)
      expect(mockNavigate).toHaveBeenCalledWith('/documentos')

      const btnSolicitudes = screen.getByRole('button', { name: /solicitudes/i })
      fireEvent.click(btnSolicitudes)
      expect(mockNavigate).toHaveBeenCalledWith('/auditoria')
    })

    it('renderiza el saludo centrado con el nombre del usuario y la dropzone inicial', () => {
      render(<NewDocument />)

      expect(screen.getByText(/buen día dr\. lucas/i)).toBeInTheDocument()
      expect(screen.getByText(/ejecutar nuevo análisis/i)).toBeInTheDocument()
      expect(screen.getByText(/arrastre y suelte el archivo fuente para subirlo/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /seleccionar archivos/i })).toBeInTheDocument()
      expect(screen.getByLabelText(/canal de origen/i)).toBeInTheDocument()
    })
  })

  describe('US2: Estado de Archivo Seleccionado y Acciones', () => {
    it('muestra el archivo seleccionado con su tamaño y botones Cancelar / Continuar', () => {
      render(<NewDocument />)

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
      expect(fileInput).toBeInTheDocument()

      const file = new File(['dummy-content'], 'test_informe_clinico.pdf', {
        type: 'application/pdf',
      })
      fireEvent.change(fileInput, { target: { files: [file] } })

      expect(screen.getByText('test_informe_clinico.pdf')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /cancelar/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /continuar/i })).toBeInTheDocument()
    })

    it('al hacer clic en Cancelar se descarta el archivo y regresa al dropzone', () => {
      render(<NewDocument />)

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['dummy-content'], 'test_informe_clinico.pdf', {
        type: 'application/pdf',
      })
      fireEvent.change(fileInput, { target: { files: [file] } })

      const btnCancelar = screen.getByRole('button', { name: /cancelar/i })
      fireEvent.click(btnCancelar)

      expect(screen.queryByText('test_informe_clinico.pdf')).not.toBeInTheDocument()
      expect(screen.getByText(/arrastre y suelte el archivo fuente para subirlo/i)).toBeInTheDocument()
    })
  })

  describe('US3: Procesamiento y Loader', () => {
    it('al enviar el archivo llama a documentsApi.procesarDocumento y activa estado de carga', async () => {
      render(<NewDocument />)

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
      const file = new File(['dummy-content'], 'test_tomografia.pdf', {
        type: 'application/pdf',
      })
      fireEvent.change(fileInput, { target: { files: [file] } })

      const btnContinuar = screen.getByRole('button', { name: /continuar/i })
      fireEvent.click(btnContinuar)

      await waitFor(() => {
        expect(documentsApi.procesarDocumento).toHaveBeenCalledWith(file, 'Consulta_Externa')
        expect(mockNavigate).toHaveBeenCalledWith('/documentos/DOC-2026-ABCD')
      })
    })
  })
})

