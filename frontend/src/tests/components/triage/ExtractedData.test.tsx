import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect } from 'vitest';
import ExtractedData from '../../../components/triage/ExtractedData';

describe('ExtractedData - Visualización de Medicamentos Prescritos (US1)', () => {
  it('renderiza la tabla de medicamentos con sus columnas cuando existen prescripciones', () => {
    const mockData = {
      diagnostico: 'Infección respiratoria aguda',
      cie10: 'J06.9',
      paciente: {
        nombre: 'Carlos Mendoza',
        dni: '45892134',
        edad: 42,
      },
      medico: {
        nombre: 'Dra. Elena Ramos',
        cmp: 'CMP-44582',
      },
      medicamentos: [
        {
          nombre: 'Amoxicilina + Ácido Clavulánico',
          dosis: '875/125 mg',
          frecuencia: 'Cada 8 horas por 7 días',
          via_administracion: 'Oral',
        },
        {
          medicamento: 'Ibuprofeno',
          dosis: '400 mg',
          frecuencia: 'Cada 8 horas si hay dolor',
          via_administracion: 'Oral',
        },
      ],
    };

    render(
      <ExtractedData
        data={mockData}
        clasificacion={{ tipo_documento: 'RECETA_MEDICA', especialidad: 'Medicina General' }}
      />
    );

    // Encabezado de sección
    expect(screen.getByText(/Medicamentos Prescritos/i)).toBeInTheDocument();

    // Columnas de la tabla
    expect(screen.getByRole('columnheader', { name: /Medicamento/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /Dosis/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /Frecuencia/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /Vía/i })).toBeInTheDocument();

    // Filas de fármacos y dosis
    expect(screen.getByText('Amoxicilina + Ácido Clavulánico')).toBeInTheDocument();
    expect(screen.getByText('875/125 mg')).toBeInTheDocument();
    expect(screen.getByText('Cada 8 horas por 7 días')).toBeInTheDocument();

    expect(screen.getByText('Ibuprofeno')).toBeInTheDocument();
    expect(screen.getByText('400 mg')).toBeInTheDocument();

    // Badges de vía de administración
    const viaBadges = screen.getAllByText('Oral');
    expect(viaBadges.length).toBe(2);
  });

  it('muestra estado neutro cuando la vía de administración no está especificada', () => {
    const mockData = {
      medicamentos: [
        {
          medicamento: 'Paracetamol',
          dosis: '500 mg',
          frecuencia: 'Cada 6 horas',
        },
      ],
    };

    render(<ExtractedData data={mockData} />);

    expect(screen.getByText('Paracetamol')).toBeInTheDocument();
    expect(screen.getByText('500 mg')).toBeInTheDocument();
    expect(screen.getByText('No especificada')).toBeInTheDocument();
  });

  it('muestra mensaje defensivo "No identificado / No aplica" cuando no hay medicamentos', () => {
    const mockData = {
      diagnostico: 'Control de rutina',
      medicamentos: [],
    };

    render(<ExtractedData data={mockData} />);

    expect(screen.getByText(/No identificado \/ No aplica/i)).toBeInTheDocument();
    expect(screen.queryByRole('columnheader', { name: /Medicamento/i })).not.toBeInTheDocument();
  });

  it('maneja datos sanitizados contra inyecciones XSS en nombres y dosis', () => {
    const mockData = {
      medicamentos: [
        {
          nombre: '<script>alert("xss")</script>Ketorolaco',
          dosis: '10 mg',
          frecuencia: 'C/8h',
          via_administracion: 'Sublingual',
        },
      ],
    };

    render(<ExtractedData data={mockData} />);

    // El contenido malicioso no debe interpretarse como HTML
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.getByText(/Ketorolaco/i)).toBeInTheDocument();
    expect(screen.getByText('Sublingual')).toBeInTheDocument();
  });
});
