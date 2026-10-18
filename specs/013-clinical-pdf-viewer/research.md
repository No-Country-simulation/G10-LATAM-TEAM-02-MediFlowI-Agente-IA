# Investigación Técnica: Visor Interactivo y Robusto de Documentos PDF Clínicos

**Feature**: `013-clinical-pdf-viewer`
**Fecha**: 2026-10-18
**Autor**: MediFlow Core Architecture Team

## Resumen de Investigación

Esta fase de investigación aborda las decisiones arquitectónicas clave para implementar un visor clínico de documentos PDF e imágenes que sea robusto, interactivo, accesible y conforme a la Constitución de MediFlow (Tailwind CSS, diseño hospitalario y cero regresiones).

---

## Decisiones Técnicas

### 1. Elemento Embebido de PDF y Detección del Estado de Carga (Skeleton Loader)

- **Decisión**: Utilizar un elemento `<object data={fileUrl} type="application/pdf">` (con fallback de `<iframe>`) encapsulado en un contenedor de estado reactivo (`loading`, `ready`, `error`).
- **Racional**:
  - El elemento `<object>` es el estándar web semántico para documentos externos embebidos y permite anidar contenido de contingencia directamente en el DOM en caso de que el plugin del navegador no pueda renderizar el PDF.
  - Dispara el evento `onLoad` cuando los metadatos y la primera página del documento se encuentran renderizados en el viewport.
  - Mientras el estado es `loading`, se renderiza un Skeleton Loader animado con Tailwind CSS (`animate-pulse`) estructurado como un documento clínico (encabezado de expediente, líneas de texto simuladas y bloques de contenido).
  - Se añade un temporizador de seguridad de contingencia (ej. 8 segundos): si el navegador no emite `onLoad` o bloquea el renderizador embebido, el estado pasa a modo contingencia ofreciendo descarga directa sin dejar la pantalla en espera infinita.
- **Alternativas Evaluadas**:
  - *PDF.js (Mozilla canvas renderer)*: Muy potente pero añade dependencias pesadas de empaquetado (>1.5MB de bundle y worker externo), innecesario para visualización directa de expedientes de triaje donde el visor nativo del navegador ofrece aceleración de hardware.
  - *Solo `<iframe>` sin detección de carga*: Comportamiento inconsistente entre navegadores para capturar fallos de decodificación o restricciones CORS de visualización.

### 2. Implementación de Pantalla Completa (Full Screen API + Fallback)

- **Decisión**: Implementar un patrón híbrido con la API nativa de pantalla completa (`Element.requestFullscreen()` / `document.exitFullscreen()`) coordinada con un fallback CSS de ventana completa (`fixed inset-0 z-50`).
- **Racional**:
  - En estaciones de trabajo médicas y computadores clínicos de escritorio, `requestFullscreen()` aprovecha el 100% de la superficie física del monitor (1080p / 4K), aislando distracciones del navegador.
  - Escuchar el evento nativo `fullscreenchange` en `document` para sincronizar el estado reactivo `isFullscreen` cuando el usuario presiona la tecla `Escape` o sale mediante la interfaz del navegador.
  - En navegadores donde los permisos de pantalla completa estén restringidos por políticas de seguridad o iframe contenedor, se activa el fallback CSS para expandir el componente en toda el área visible de la ventana sin generar errores en consola.
- **Alternativas Evaluadas**:
  - *Únicamente clases CSS `fixed`*: No oculta la barra de pestañas ni la barra del sistema operativo en estaciones médicas donde se requiere máxima inmersión visual.
  - *Librerías externas de Fullscreen (screenfull.js)*: Innecesaria sobrecarga de dependencias; la API estándar de W3C es ampliamente soportada en todos los navegadores modernos (Chrome, Firefox, Edge, Safari 16.4+).

### 3. Barra de Herramientas y Controles de Zoom para PDF e Imágenes

- **Decisión**: Proporcionar una barra de herramientas unificada superior con botones accesibles (`aria-label`, tooltips) para:
  1. Zoom Out (decrementos de 25%, mínimo 50%).
  2. Reset Zoom (botón indicador que muestra el porcentaje actual `100%` y restablece a escala base).
  3. Zoom In (incrementos de 25%, máximo 250%).
  4. Descarga directa del archivo original.
  5. Alternancia de Pantalla Completa.
- **Racional**:
  - Para imágenes (JPG, PNG, WebP), la transformación CSS `transform: scale(zoomLevel)` sobre el contenedor con `transformOrigin: 'top center'` o `'center center'` permite inspección inmediata sin pixelado prematuro.
  - Para PDFs embebidos, envolver el elemento `<object>`/`<iframe>` en un viewport con `overflow: auto` y aplicar la escala calculada garantiza ampliación uniforme del documento sin romper el flujo de lectura.
- **Alternativas Evaluadas**:
  - *Zoom exclusivo del visor nativo del navegador*: No ofrece controles unificados en la interfaz hospitalaria y depende de atajos de teclado (`Ctrl + +/-`) que el personal clínico puede desconocer en tablets.

### 4. Resiliencia ante Errores y Descarga Directa de Contingencia

- **Decisión**: Panel de contingencia no intrusivo con alerta semántica hospitalaria, botón de descarga directa forzada y apertura en pestaña independiente.
- **Racional**:
  - La continuidad asistencial es un pilar innegociable en MediFlow. Si el archivo está corrupto o el navegador bloquea el renderizado embebido, el médico no debe quedar bloqueado.
  - Proporcionar botón con etiqueta clara y atributo `download` para salvar el archivo en disco, y un botón secundario para abrir en pestaña nueva con `target="_blank"` y `rel="noreferrer"`.
- **Alternativas Evaluadas**:
  - *Error genérico de página*: Provoca pérdida del contexto de la pantalla de triaje o auditoría médica.

### 5. Estándar de Estilos y Responsive Design (Tailwind CSS)

- **Decisión**: Migrar completamente las clases CSS de `DocumentViewer.tsx` a **Tailwind CSS**, eliminando las clases residuales de Bootstrap (`card`, `btn`, `d-flex`, etc.), garantizando compatibilidad responsive para tablets (768px) y escritorios.
- **Racional**:
  - Da estricto cumplimiento a la Constitución de MediFlow v1.2.0 (Frontend: Tailwind CSS obligatorio y responsividad en todo el frontend).
  - Permite control fino de transiciones suaves, estados `hover`, `focus-visible`, `disabled` y diseño ergonómico para uso clínico continuo.

