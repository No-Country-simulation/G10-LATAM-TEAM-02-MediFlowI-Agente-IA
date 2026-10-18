# Data Model: Soporte Integral para Carga y Visualización de Imágenes WebP

**Feature**: `012-webp-clinical-viewer`  
**Date**: 2026-10-17  
**Status**: Completed  

---

## 1. Entidades de Frontend y Props de Componentes

### 1.1 `DocumentViewerProps`
Interfaz que define las propiedades recibidas por el componente visualizador clínico.

```typescript
interface DocumentViewerProps {
  /** Nombre del archivo clínico (ej: "estudio_rx.webp", "receta.pdf") */
  fileName?: string;
  /** URL accesible o blob local para la renderización del archivo */
  fileUrl?: string;
}
```

### 1.2 `DocumentViewerState`
Estados locales administrados dentro de `DocumentViewer.tsx`.

| Propiedad | Tipo | Valor Inicial | Descripción |
|---|---|---|---|
| `isExpanded` | `boolean` | `false` | Indica si el visor está en modo pantalla completa / modal ampliado. |
| `zoomLevel` | `number` | `1` (100%) | Nivel de zoom aplicado a imágenes clínicas (rango: 0.5x a 2.5x en pasos de 0.25). |
| `imageError` | `boolean` | `false` | Indica si ocurrió un error en la carga o decodificación del archivo de imagen. |

### 1.3 `DocumentUploaderProps`
Interfaz del componente de carga de archivos clínicos.

```typescript
interface DocumentUploaderProps {
  /** Callback invocado cuando el archivo ha sido validado y se inicia el procesamiento */
  onProcess?: (file: File, canalOrigen: string) => void | Promise<void>;
  /** Callback invocado al cancelar la selección o volver a la vista previa */
  onCancel?: () => void;
  /** Indica si hay un proceso de carga/triaje en curso */
  isProcessing?: boolean;
}
```

### 1.4 Reglas de Validación de Formato en `DocumentUploader`

| Regla | Parámetro | Detalle |
|---|---|---|
| **MIME Types Permitidos** | `ALLOWED_TYPES` | `["application/pdf", "image/jpeg", "image/jpg", "image/png", "image/webp"]` |
| **Extensiones Válidas** | Regex | `/\.(pdf\|jpg\|jpeg\|png\|webp)$/i` |
| **Tamaño Máximo** | `MAX_SIZE_BYTES` | `10 * 1024 * 1024` (10 MB) |
| **Atributo Accept** | HTML Input | `.pdf,.jpg,.jpeg,.png,.webp,application/pdf,image/jpeg,image/png,image/webp` |

---

## 2. Transiciones de Estado en `DocumentViewer`

```text
[Inicio]
   │
   ├── (fileUrl no provisto) ─────────► [Estado Vacío: Mockup / Info de Documento Clínico]
   │
   └── (fileUrl provisto)
         │
         ├── isPdf == true ───────────► [Renderizado en <iframe>]
         │
         └── isPdf == false (Imagen)
               │
               ├── (Carga exitosa) ───► [Renderizado en <img> con Zoom y Adaptación]
               │                           │
               │                           ├── Zoom In  (+25%, max 250%)
               │                           ├── Zoom Out (-25%, min 50%)
               │                           ├── Zoom Reset (100%)
               │                           └── Expandir / Reducir (Fullscreen)
               │
               └── (Fallo onError) ───► [Estado de Alerta de Error Clínico]
                                           └── Acción: "Abrir en nueva pestaña"
```

