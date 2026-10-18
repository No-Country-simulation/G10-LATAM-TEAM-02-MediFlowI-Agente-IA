import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect } from 'vitest';
import DocumentViewer from '../../../components/documents/DocumentViewer';
import DocumentUploader from '../../../components/documents/DocumentUploader';
import { BrowserRouter } from 'react-router-dom';

describe('DocumentViewer - Soporte de Imágenes WebP', () => {
  it('renderiza correctamente una imagen con extensión y URL .webp', () => {
    render(
      <DocumentViewer
        fileName="estudio_rx.webp"
        fileUrl="https://hospital.local/estudio_rx.webp"
      />
    );

    expect(screen.getByText(/estudio_rx\.webp/i)).toBeInTheDocument();
    const img = screen.getByRole('img', { name: /Vista del documento clínico/i });
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', 'https://hospital.local/estudio_rx.webp');
  });

  it('permite aplicar zoom in, zoom out y restablecer al 100% en imágenes WebP', () => {
    render(
      <DocumentViewer
        fileName="receta_medica.webp"
        fileUrl="https://hospital.local/receta_medica.webp"
      />
    );

    const img = screen.getByRole('img', { name: /Vista del documento clínico/i });
    expect(img).toHaveStyle({ transform: 'scale(1)' });
    expect(screen.getByText('100%')).toBeInTheDocument();

    const zoomInBtn = screen.getByRole('button', { name: /Acercar imagen/i });
    fireEvent.click(zoomInBtn);
    expect(img).toHaveStyle({ transform: 'scale(1.25)' });
    expect(screen.getByText('125%')).toBeInTheDocument();

    const zoomOutBtn = screen.getByRole('button', { name: /Alejar imagen/i });
    fireEvent.click(zoomOutBtn);
    expect(img).toHaveStyle({ transform: 'scale(1)' });
    expect(screen.getByText('100%')).toBeInTheDocument();

    // Reducir zoom a 75%
    fireEvent.click(zoomOutBtn);
    expect(img).toHaveStyle({ transform: 'scale(0.75)' });
    expect(screen.getByText('75%')).toBeInTheDocument();

    // Restablecer al 100%
    const resetBtn = screen.getByRole('button', { name: /Restablecer tamaño original/i });
    fireEvent.click(resetBtn);
    expect(img).toHaveStyle({ transform: 'scale(1)' });
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('muestra mensaje de alerta clínica si la imagen WebP está corrupta o falla la decodificación (onError)', () => {
    render(
      <DocumentViewer
        fileName="corrupto.webp"
        fileUrl="https://hospital.local/corrupto.webp"
      />
    );

    const img = screen.getByRole('img', { name: /Vista del documento clínico/i });
    fireEvent.error(img);

    expect(
      screen.getByText(/No fue posible decodificar o cargar la imagen clínica/i)
    ).toBeInTheDocument();
    expect(
      screen.getByRole('link', { name: /Abrir archivo original en nueva pestaña/i })
    ).toHaveAttribute('href', 'https://hospital.local/corrupto.webp');

    // La imagen rota se oculta de la vista
    expect(screen.queryByRole('img', { name: /Vista del documento clínico/i })).not.toBeInTheDocument();
  });

  it('restablece el estado de error cuando cambia fileUrl a una nueva imagen', () => {
    const { rerender } = render(
      <DocumentViewer
        fileName="imagen1.webp"
        fileUrl="https://hospital.local/imagen1.webp"
      />
    );

    const img = screen.getByRole('img', { name: /Vista del documento clínico/i });
    fireEvent.error(img);
    expect(screen.getByText(/No fue posible decodificar o cargar la imagen clínica/i)).toBeInTheDocument();

    // Se carga una nueva URL
    rerender(
      <DocumentViewer
        fileName="imagen2.webp"
        fileUrl="https://hospital.local/imagen2.webp"
      />
    );

    expect(screen.queryByText(/No fue posible decodificar o cargar la imagen clínica/i)).not.toBeInTheDocument();
    const newImg = screen.getByRole('img', { name: /Vista del documento clínico/i });
    expect(newImg).toHaveAttribute('src', 'https://hospital.local/imagen2.webp');
  });

  it('permite alternar entre tamaño normal y pantalla completa', () => {
    render(
      <DocumentViewer
        fileName="estudio.webp"
        fileUrl="https://hospital.local/estudio.webp"
      />
    );

    const expandBtn = screen.getByRole('button', { name: /Pantalla completa/i });
    fireEvent.click(expandBtn);
    expect(screen.getByRole('button', { name: /Reducir tamaño/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Reducir tamaño/i }));
    expect(screen.getByRole('button', { name: /Pantalla completa/i })).toBeInTheDocument();
  });

  it('muestra el estado vacío informando compatibilidad con formato WebP cuando no hay fileUrl', () => {
    render(<DocumentViewer fileName="analisis.webp" />);

    expect(screen.getByText(/Imagen Médica \(JPG\/PNG\/WebP\)/i)).toBeInTheDocument();
    expect(screen.getAllByText(/analisis\.webp/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('DocumentUploader - Admisión de Formato WebP', () => {
  it('valida y acepta la selección de archivos con extensión .webp y tipo image/webp', () => {
    render(
      <BrowserRouter>
        <DocumentUploader />
      </BrowserRouter>
    );

    expect(screen.getByText(/Formatos admitidos: PDF, JPG, PNG y WebP, hasta 10 MB\./i)).toBeInTheDocument();

    const file = new File(['dummy webp content'], 'tomografia.webp', { type: 'image/webp' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    expect(input.accept).toContain('.webp');
    expect(input.accept).toContain('image/webp');

    fireEvent.change(input, { target: { files: [file] } });

    expect(screen.queryByText(/El formato del archivo no está permitido/i)).not.toBeInTheDocument();
    expect(screen.getByText(/tomografia\.webp/i)).toBeInTheDocument();
  });
});

