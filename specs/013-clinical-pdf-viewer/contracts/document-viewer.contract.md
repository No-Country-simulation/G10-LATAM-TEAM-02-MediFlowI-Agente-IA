# Contrato de Interfaz y Streaming: DocumentViewer y API de Archivos

**Feature**: `013-clinical-pdf-viewer` (`dev-wilmer-gulcochia`)  
**Referencia de Plan**: Tarea 5.2 / Issue [FE-14] #71  
**Componente**: `frontend/src/components/documents/DocumentViewer.tsx`  
**Endpoint Backend**: `backend/app/api/v1/documents.py` (`GET /api/v1/documents/{documento_id}/file`)  
**Estándar**: W3C WAI-ARIA 1.2 / WCAG 2.1 AA / Tailwind CSS  

---

## 1. Contrato de Streaming Binario de Backend

### Endpoint: `GET /api/v1/documents/{documento_id}/file`
Retorna el archivo binario físico original (PDF, PNG, JPG, WebP) persistido en almacenamiento local u OCI para su consumo embebido en el visor o descarga directa.

#### Parámetros
| Parámetro | Tipo | Ubicación | Descripción |
|---|---|---|---|
| `documento_id` | `string` | Path | Identificador canónico del documento (ej. `DOC-2026-04E835AF`) |
| `token` | `string` (opcional) | Query | Token de autenticación para visores embebidos |
| `Authorization` | `string` (opcional) | Header | Cabecera `Bearer <JWT>` estándar |

#### Respuestas HTTP
- **`200 OK`**:
  - `Content-Type`: `application/pdf` (para PDFs) o `image/png`, `image/jpeg`, `image/webp` (para imágenes).
  - `Content-Disposition`: `inline; filename="<nombre_original_del_archivo>"`
  - `Cache-Control`: `public, max-age=3600`
  - Body: Flujo de bytes crudos (`FileResponse` o `bytes`).
- **`404 Not Found`**:
  ```json
  {
    "detail": {
      "error": "ARCHIVO_NO_ENCONTRADO",
      "mensaje": "El archivo original para 'DOC-2026-...' no está disponible."
    }
  }
  ```

---

## 2. Contrato de Adaptador Frontend (`documentsApi.ts`)

En la proyección del documento hacia la interfaz clínica:

```typescript
export interface ClinicalDocument {
  id: string;
  documento_id: string;
  nombre_archivo: string;
  url_archivo?: string; // Proyectado como `/api/v1/documents/${documento_id}/file`
  // ... resto de propiedades clínicas
}
```

---

## 3. Interfaz de Propiedades del Componente (`DocumentViewerProps`)

```typescript
export interface DocumentViewerProps {
  /** Nombre del archivo o identificador clínico para títulos y descargas */
  fileName?: string;
  /** URL accesible de streaming o blob URL del PDF o imagen */
  fileUrl?: string;
  /** Altura mínima predeterminada del visor (default: '480px' o '520px') */
  minHeight?: string;
  /** Callback opcional notificador de cambios en pantalla completa */
  onFullScreenChange?: (isFullScreen: boolean) => void;
  /** Callback opcional notificador de fallos de carga */
  onError?: (error: Error) => void;
}
```

---

## 4. Contrato de Elementos del DOM y Accesibilidad (ARIA)

### Arquitectura de Barra de Herramientas (`role="toolbar"`)
La barra de herramientas implementa un diseño responsivo adaptable para paneles laterales estrechos (`col-lg-5` ~400px) y pantallas completas:
- **Nivel 1 (Metadatos y Título Completo)**:
  - Ocupa el 100% del ancho superior (`w-full` en modo normal, flex-1 en pantalla completa).
  - Ícono visual del tipo de documento (`FaFilePdf` o `FaFileImage`).
  - Nombre completo del archivo clínico con tipografía `text-xs sm:text-sm font-semibold` y tooltip `title={fileName}`.
  - Badge semántico en píldora (`PDF` en rojo clínico o `IMAGEN` en azul médico).
- **Nivel 2 (Controles y Acciones)**:
  - **Grupo de Zoom**: Botones de incremento `[+]` y decremento `[-]` como **cuadrados exactos** (`w-7 h-7 sm:w-8 sm:h-8`), e indicador de porcentaje reactivo como **rectángulo horizontal central** (`h-7 sm:h-8 px-2.5 min-w-[54px] font-mono font-semibold`).
  - **Grupo de Acciones (Alineado a la derecha)**: Botones con padding ergonómico para descarga directa, apertura externa y pantalla completa.
- **Transición a Pantalla Completa**:
  - En pantalla completa (`isExpanded === true`), la barra colapsa suavemente a una única fila horizontal amplia (`flex-row items-center justify-between gap-4`).

### Detalle de Accesibilidad en Controles
- **Rol de Contenedor**: `role="toolbar"` con `aria-label="Controles de visualización del documento"`.
- **Botón Zoom Out**:
  - `role="button"`, `aria-label="Alejar documento"`, `disabled`: `zoomLevel <= 0.5`, geometría cuadrada.
- **Botón Reset Zoom**:
  - `role="button"`, `aria-label="Restablecer tamaño original (100%)"`, texto: `{zoomLevel * 100}%`, geometría rectangular horizontal.
- **Botón Zoom In**:
  - `role="button"`, `aria-label="Acercar documento"`, `disabled`: `zoomLevel >= 2.5`, geometría cuadrada.
- **Botón Descarga Directa**:
  - Elemento: `<a>` con atributo `download` y `href={fileUrl}`.
  - `aria-label="Descargar archivo original"`.
  - Icono `FaDownload` con texto visible `Descargar`.
- **Botón Pantalla Completa**:
  - `role="button"`, geometría cuadrada.
  - `aria-label`: `"Pantalla completa"` (si `isFullscreen === false`) o `"Reducir tamaño"` (si `isFullscreen === true`).
  - Icono `FaExpand` / `FaCompress`.
- **Botón Abrir Pestaña Externa**:
  - Elemento: `<a>` con `target="_blank"` y `rel="noreferrer"`.
  - `aria-label="Abrir en pestaña independiente"`, icono `FaExternalLinkAlt`, texto visible `Abrir`.

### Contenedor de Carga (Skeleton Loader)
- **Atributos**: `role="status"`, `aria-live="polite"`, `aria-label="Cargando documento clínico..."`.
- **Estructura Visual**: Animación `animate-pulse` con Tailwind CSS estructurada en bloques de cabecera y líneas que simulan un expediente o receta médica A4.

### Contenedor de Error y Contingencia
- **Atributos**: `role="alert"`, `aria-live="assertive"`.
- **Estructura**:
  - Encabezado `<h3>` conciso y desacoplado (ej. `"Error de visualización del documento PDF"` o `"Error de decodificación de imagen clínica"`).
  - Párrafo descriptivo `<p>` con instrucciones de contingencia.
  - Botón de descarga directa con `download` y botón de apertura en nueva pestaña.

---

## 5. Matriz de Comportamiento e Interacciones

| Acción de Usuario | Estado Inicial | Evento / Disparador | Estado Final / Efecto en DOM |
|---|---|---|---|
| Carga de documento | `fileUrl` cambia | Montaje / `useEffect` | Se activa `loadingState = 'loading'`, se muestra Skeleton Loader |
| Descarga exitosa | `loadingState = 'loading'` | `onLoad` de `<object>` o `<img>` | `loadingState = 'ready'`, se oculta skeleton y se muestra documento |
| Fallo en visualización | `loadingState = 'loading'` | `onError` o timeout contingencia | `loadingState = 'error'`, se muestra panel de contingencia con enlaces de rescate |
| Clic en "Acercar" | `zoomLevel = 1.0` | Clic botón `+` | `zoomLevel = 1.25`, escala CSS actualizada inmediatamente |
| Clic en "Restablecer" | `zoomLevel = 1.5` | Clic botón `{zoom}%` | `zoomLevel = 1.0` |
| Clic en "Pantalla Completa" | `isFullscreen = false` | Clic botón fullscreen | `isFullscreen = true`, se invoca `requestFullscreen()` y clase `fixed inset-0` |
| Pulsación tecla `Esc` | `isFullscreen = true` | Evento `fullscreenchange` | `isFullscreen = false`, retorno suave al contenedor habitual |
| Clic en "Descargar" | Cualquier estado | Clic botón descarga | Navegador inicia descarga de `fileUrl` con nombre `fileName` |
