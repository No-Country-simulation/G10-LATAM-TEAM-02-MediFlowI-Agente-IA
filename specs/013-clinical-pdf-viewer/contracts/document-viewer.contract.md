# Contrato de Interfaz de Componente: DocumentViewer

**Feature**: `013-clinical-pdf-viewer`
**Componente**: `frontend/src/components/documents/DocumentViewer.tsx`
**Estándar**: W3C WAI-ARIA 1.2 / WCAG 2.1 AA / Tailwind CSS

---

## 1. Interfaz de Propiedades (Component Props Contract)

```typescript
export interface DocumentViewerProps {
  /** Nombre del archivo o identificador clínico para títulos y metadatos */
  fileName?: string;
  /** URL accesible o blob URL del PDF o imagen */
  fileUrl?: string;
  /** Altura mínima predeterminada del visor (default: '480px') */
  minHeight?: string;
  /** Callback opcional notificador de cambios en pantalla completa */
  onFullScreenChange?: (isFullScreen: boolean) => void;
  /** Callback opcional notificador de fallos de carga */
  onError?: (error: Error) => void;
}
```

---

## 2. Contrato de Elementos del DOM y Accesibilidad (ARIA)

### Barra de Herramientas (`toolbar`)
- **Rol**: `role="toolbar"` con `aria-label="Controles de visualización del documento"`.
- **Botón Zoom Out**:
  - `role="button"`
  - `aria-label="Alejar documento"`
  - `disabled`: `zoomLevel <= 0.5`
- **Botón Reset Zoom**:
  - `role="button"`
  - `aria-label="Restablecer tamaño original (100%)"`
  - Texto visible: `100%` (o `{zoomLevel * 100}%`)
- **Botón Zoom In**:
  - `role="button"`
  - `aria-label="Acercar documento"`
  - `disabled`: `zoomLevel >= 2.5`
- **Botón Descarga Directa**:
  - Elemento: `<a>` con atributo `download` o `<button>`
  - `aria-label="Descargar archivo original"`
  - Texto visible: `Descargar` con ícono representativo.
- **Botón Pantalla Completa**:
  - `role="button"`
  - `aria-label`: `"Pantalla completa"` cuando `isExpanded === false`, `"Reducir tamaño"` cuando `isExpanded === true`.
- **Botón Abrir Pestaña Externa**:
  - Elemento: `<a>` con `target="_blank"` y `rel="noreferrer"`
  - `aria-label="Abrir en pestaña independiente"`.

### Contenedor de Carga (Skeleton Loader)
- **Atributos**: `role="status"`, `aria-live="polite"`, `aria-label="Cargando documento clínico..."`.
- **Estructura Visual**: Animación `animate-pulse` simulando un documento clínico A4 (barra superior de metadatos, bloques de prescripción/diagnóstico).

### Contenedor de Error y Contingencia
- **Atributos**: `role="alert"`, `aria-live="assertive"`.
- **Contenido**:
  - Título descriptivo: "Error al visualizar el documento PDF" o "Error de decodificación de imagen".
  - Mensaje claro con instrucción de contingencia.
  - Botón de descarga directa con `download` y botón de apertura en nueva pestaña.

---

## 3. Matriz de Comportamiento e Interacciones

| Acción de Usuario | Estado Inicial | Evento / Disparador | Estado Final / Efecto en DOM |
|---|---|---|---|
| Carga de PDF | `fileUrl` cambia | Montaje / `useEffect` | Se activa `loadingState = 'loading'`, se muestra Skeleton Loader |
| Finalización de descarga | `loadingState = 'loading'` | `onLoad` de `<object>` o `<iframe>` | `loadingState = 'ready'`, se oculta skeleton y se muestra PDF |
| Fallo en visualización | `loadingState = 'loading'` | `onError` o timeout contingencia | `loadingState = 'error'`, se muestra panel de contingencia con enlace de descarga |
| Clic en "Acercar" | `zoomLevel = 1.0` | Clic botón `+` | `zoomLevel = 1.25`, escala CSS actualizada inmediatamente |
| Clic en "Restablecer" | `zoomLevel = 1.5` | Clic botón `{zoom}%` | `zoomLevel = 1.0` |
| Clic en "Pantalla Completa" | `isFullscreen = false` | Clic botón fullscreen | `isFullscreen = true`, se invoca `requestFullscreen()` y/o clase `fixed inset-0` |
| Pulsación tecla `Esc` | `isFullscreen = true` | Evento `fullscreenchange` | `isFullscreen = false`, retorno suave al tamaño contenedor |
| Clic en "Descargar" | Cualquier estado | Clic botón descarga | Navegador inicia descarga de `fileUrl` con nombre `fileName` |

