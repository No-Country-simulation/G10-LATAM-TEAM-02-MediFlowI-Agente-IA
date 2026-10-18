# UI Contracts & Component Interfaces: Visor Clínico y Carga WebP

**Feature**: `012-webp-clinical-viewer`  
**Date**: 2026-10-17  
**Status**: Completed  

---

## 1. Contrato de Interfaz: `DocumentUploader`

### Ubicación
`frontend/src/components/documents/DocumentUploader.tsx`

### Firma del Componente
```tsx
export interface DocumentUploaderProps {
  onProcess?: (file: File, canalOrigen: string) => void | Promise<void>;
  onCancel?: () => void;
  isProcessing?: boolean;
}

export default function DocumentUploader(props: DocumentUploaderProps): JSX.Element;
```

### Comportamiento y Aserciones
1. **Atributo `accept`**:
   - Elemento `<input type="file">` debe tener exactamente:
     `accept=".pdf,.jpg,.jpeg,.png,.webp,application/pdf,image/jpeg,image/png,image/webp"`
2. **Validación de Archivo**:
   - Archivos con extensión `.webp` o MIME `image/webp` pasan la validación sin mostrar alerta.
   - Archivos no autorizados (ej: `.docx`, `.exe`) muestran alerta de error:
     `"El formato del archivo no está permitido. Solo se permiten PDF, JPG, PNG y WebP."`
   - Archivos > 10 MB muestran alerta:
     `"El archivo supera los 10 MB."`
3. **Texto Informativo**:
   - La cabecera informativa debe mostrar:
     `"Formatos admitidos: PDF, JPG, PNG y WebP, hasta 10 MB."`

---

## 2. Contrato de Interfaz: `DocumentViewer`

### Ubicación
`frontend/src/components/documents/DocumentViewer.tsx`

### Firma del Componente
```tsx
export interface DocumentViewerProps {
  fileName?: string;
  fileUrl?: string;
}

export default function DocumentViewer(props: DocumentViewerProps): JSX.Element;
```

### Comportamiento y Aserciones
1. **Renderizado de Imagen**:
   - Cuando `fileName` termine en `.webp` (o cualquier extensión no PDF) y `fileUrl` esté presente, debe renderizar un elemento `<img />` con:
     - `src={fileUrl}`
     - `alt="Vista del documento clínico"`
     - Manejador de evento `onError`
2. **Controles de Zoom**:
   - Botón `Acercar` / `Zoom +` (`aria-label="Acercar imagen"`): incrementa `zoomLevel` en 0.25 (hasta máximo 2.5).
   - Botón `Alejar` / `Zoom -` (`aria-label="Alejar imagen"`): disminuye `zoomLevel` en 0.25 (hasta mínimo 0.5).
   - Botón `Restablecer` (`aria-label="Restablecer tamaño original"`): restablece `zoomLevel` a 1.0.
   - Etiqueta o indicador con el porcentaje actual (ej: `100%`, `125%`).
3. **Manejo de Error de Decodificación**:
   - Ante la emisión del evento `error` en la imagen, el visor debe:
     - Ocultar la etiqueta `<img>` fallida.
     - Mostrar un contenedor de alerta médica con icono `FaExclamationTriangle`.
     - Mostrar el mensaje exacto o equivalente:
       `"No fue posible decodificar o cargar la imagen clínica. El archivo podría estar dañado o el formato no es compatible con el navegador."`
     - Proveer un botón/enlace seguro `<a>` con `href={fileUrl}` y `target="_blank"` para abrir la fuente original.
4. **Reseteo de Error**:
   - Cuando cambie la propiedad `fileUrl`, el estado de error debe reiniciarse automáticamente.

