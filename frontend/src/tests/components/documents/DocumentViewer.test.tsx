import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { describe, it, expect, vi } from 'vitest';
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

    const zoomInBtn = screen.getByRole('button', { name: /Acercar documento/i });
    fireEvent.click(zoomInBtn);
    expect(img).toHaveStyle({ transform: 'scale(1.25)' });
    expect(screen.getByText('125%')).toBeInTheDocument();

    const zoomOutBtn = screen.getByRole('button', { name: /Alejar documento/i });
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

  it('permite alternar entre tamaño normal y pantalla completa', async () => {
    render(
      <DocumentViewer
        fileName="estudio.webp"
        fileUrl="https://hospital.local/estudio.webp"
      />
    );

    const expandBtn = screen.getByRole('button', { name: /Pantalla completa/i });
    await act(async () => {
      fireEvent.click(expandBtn);
    });
    expect(screen.getByRole('button', { name: /Reducir tamaño/i })).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Reducir tamaño/i }));
    });
    expect(screen.getByRole('button', { name: /Pantalla completa/i })).toBeInTheDocument();
  });

  it('muestra el estado vacío informando compatibilidad con formato WebP cuando no hay fileUrl', () => {
    render(<DocumentViewer fileName="analisis.webp" />);

    expect(screen.getByText(/Imagen Médica \(JPG\/PNG\/WebP\)/i)).toBeInTheDocument();
    expect(screen.getAllByText(/analisis\.webp/i).length).toBeGreaterThanOrEqual(1);
  });
});

describe('DocumentViewer - US1: Visualización Fluida de PDFs con Skeleton Loader', () => {
  it('muestra el Skeleton Loader animado al cargar un archivo PDF', () => {
    render(
      <DocumentViewer
        fileName="expediente_clinico.pdf"
        fileUrl="https://hospital.local/expediente.pdf"
      />
    );

    const skeleton = screen.getByRole('status', { name: /Cargando documento clínico/i });
    expect(skeleton).toBeInTheDocument();
    expect(screen.getByText(/Preparando vista del documento clínico/i)).toBeInTheDocument();
  });

  it('oculta el Skeleton Loader y muestra el PDF embebido tras emitirse el evento de carga', () => {
    render(
      <DocumentViewer
        fileName="informe_triaje.pdf"
        fileUrl="https://hospital.local/informe.pdf"
      />
    );

    const iframeOrObject = screen.getByTitle(/Vista previa del documento PDF/i);
    expect(iframeOrObject).toBeInTheDocument();

    // Disparar evento load en el visor embebido
    fireEvent.load(iframeOrObject);

    // El skeleton loader debe haberse ocultado
    expect(screen.queryByRole('status', { name: /Cargando documento clínico/i })).not.toBeInTheDocument();
  });

  it('reinicia el estado de carga y muestra el Skeleton Loader al cambiar a otro documento PDF', () => {
    const { rerender } = render(
      <DocumentViewer
        fileName="doc1.pdf"
        fileUrl="https://hospital.local/doc1.pdf"
      />
    );

    const viewer = screen.getByTitle(/Vista previa del documento PDF/i);
    fireEvent.load(viewer);
    expect(screen.queryByRole('status', { name: /Cargando documento clínico/i })).not.toBeInTheDocument();

    // Rerender con nuevo documento
    rerender(
      <DocumentViewer
        fileName="doc2.pdf"
        fileUrl="https://hospital.local/doc2.pdf"
      />
    );

    expect(screen.getByRole('status', { name: /Cargando documento clínico/i })).toBeInTheDocument();
  });
});

describe('DocumentViewer - US2: Controles de Zoom y Pantalla Completa', () => {
  it('habilita controles de zoom interactivo en documentos PDF', () => {
    render(
      <DocumentViewer
        fileName="diagnostico.pdf"
        fileUrl="https://hospital.local/diagnostico.pdf"
      />
    );

    expect(screen.getByText('100%')).toBeInTheDocument();
    const zoomInBtn = screen.getByRole('button', { name: /Acercar documento/i });
    const zoomOutBtn = screen.getByRole('button', { name: /Alejar documento/i });
    const resetBtn = screen.getByRole('button', { name: /Restablecer tamaño original/i });

    // Incrementar zoom
    fireEvent.click(zoomInBtn);
    expect(screen.getByText('125%')).toBeInTheDocument();

    // Restablecer zoom
    fireEvent.click(resetBtn);
    expect(screen.getByText('100%')).toBeInTheDocument();

    // Decrementar zoom
    fireEvent.click(zoomOutBtn);
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('soporta alternancia de pantalla completa invocando la Fullscreen API', async () => {
    const onFullScreenChangeMock = vi.fn();
    render(
      <DocumentViewer
        fileName="prescripcion.pdf"
        fileUrl="https://hospital.local/prescripcion.pdf"
        onFullScreenChange={onFullScreenChangeMock}
      />
    );

    const fullscreenBtn = screen.getByRole('button', { name: /Pantalla completa/i });
    await act(async () => {
      fireEvent.click(fullscreenBtn);
    });

    expect(screen.getByRole('button', { name: /Reducir tamaño/i })).toBeInTheDocument();
  });
});

describe('DocumentViewer - US3: Descarga Directa y Manejo de Errores de Contingencia', () => {
  it('proporciona un botón de descarga directa del archivo PDF original con el nombre correspondiente', () => {
    render(
      <DocumentViewer
        fileName="estudio_tomografia.pdf"
        fileUrl="https://hospital.local/estudio_tomografia.pdf"
      />
    );

    const downloadBtn = screen.getByRole('link', { name: /Descargar archivo original/i });
    expect(downloadBtn).toBeInTheDocument();
    expect(downloadBtn).toHaveAttribute('href', 'https://hospital.local/estudio_tomografia.pdf');
    expect(downloadBtn).toHaveAttribute('download', 'estudio_tomografia.pdf');
  });

  it('muestra la tarjeta de contingencia clínica con opciones de descarga si falla el renderizado embebido', () => {
    render(
      <DocumentViewer
        fileName="fallo_render.pdf"
        fileUrl="https://hospital.local/fallo_render.pdf"
      />
    );

    const viewer = screen.getByTitle(/Vista previa del documento PDF/i);
    fireEvent.error(viewer);

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText(/Error de visualización del documento/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Descargar documento original/i })).toHaveAttribute(
      'href',
      'https://hospital.local/fallo_render.pdf'
    );
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
