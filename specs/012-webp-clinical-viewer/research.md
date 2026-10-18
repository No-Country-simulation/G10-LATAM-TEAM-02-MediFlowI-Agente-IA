# Research & Technical Decisions: Soporte Integral de Imágenes WebP en Visor Clínico

**Feature**: `012-webp-clinical-viewer`  
**Date**: 2026-10-17  
**Status**: Completed  

---

## 1. Soporte de Formatos y Validación en `DocumentUploader.tsx`

### Contexto
El componente `DocumentUploader.tsx` actualmente valida los archivos cargados mediante dos mecanismos:
1. Una lista de tipos MIME permitidos: `const ALLOWED_TYPES = ["application/pdf", "image/jpeg", "image/jpg", "image/png"];`
2. Una expresión regular de extensión de archivo: `selectedFile.name.match(/\.(pdf|jpg|jpeg|png)$/i)`
3. El atributo nativo `accept` en el `<input type="file">`: `accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"`

### Decisión
- Agregar `"image/webp"` a `ALLOWED_TYPES`.
- Actualizar la expresión regular a `/\.(pdf|jpg|jpeg|png|webp)$/i`.
- Añadir `.webp,image/webp` al atributo `accept`.
- Actualizar el texto descriptivo de la cabecera: `"Formatos admitidos: PDF, JPG, PNG y WebP, hasta 10 MB."`.

### Justificación
- La especificación de W3C e IANA designa `image/webp` como el MIME type estándar para archivos WebP.
- Mantener la sincronización entre el atributo HTML `accept`, la validación de MIME type y la comprobación de extensión por regex previene inconsistencias tanto al arrastrar archivos (drag & drop) como al seleccionarlos mediante el explorador del sistema operativo.

### Alternativas Evaluadas
- *Validar únicamente por extensión de archivo*: Descartado porque no protege adecuadamente contra archivos con extensiones cambiadas y rompe la consistencia existente con `ALLOWED_TYPES`.
- *Validación mediante lectura de magic bytes en cliente*: Descartado por añadir complejidad innecesaria para el uploader en cliente; la verificación binaria se complementa con el manejador `onError` en el visor.

---

## 2. Renderizado, Detección y Adaptación en `DocumentViewer.tsx`

### Contexto
Actualmente, `DocumentViewer.tsx` evalúa:
```typescript
const isPdf = fileName.toLowerCase().endsWith(".pdf");
```
Si no es PDF, asume que es una imagen y renderiza una etiqueta `<img>`:
```tsx
<img
  src={fileUrl}
  alt="Vista del documento clínico"
  className="img-fluid rounded shadow-sm"
  style={{ maxHeight: isExpanded ? "85vh" : "480px", objectFit: "contain" }}
/>
```
Sin embargo:
- No cuenta con controles de zoom ni ajuste dinámico de escala más allá del botón de pantalla completa.
- No dispone de manejador `onError` para imágenes corruptas o no decodificables.
- Si no hay `fileUrl`, el mensaje de ejemplo indica "Formato: Imagen Médica (JPG/PNG)".

### Decisión
- **Detección de formato**: `isPdf` se mantiene como bifurcador principal para documentos interactivos en PDF (iframe). Para imágenes (JPG, PNG, WebP), se utiliza la etiqueta `<img>`.
- **Adaptación y Zoom**:
  - Implementar botones ergonómicos de zoom en la barra de herramientas del visor: `Zoom +` (+25%), `Zoom -` (-25%) y `Reset` (100%), permitiendo un rango entre 50% y 250%.
  - El contenedor de la imagen mantendrá `overflow: auto` para permitir paneo/scroll natural cuando el zoom sea superior al 100%, con `objectFit: contain` y `transition: transform 0.15s ease-out`.
  - Cuando se active el modo de pantalla completa (`isExpanded`), la altura máxima se ajusta dinámicamente (`calc(100vh - 120px)`), garantizando responsividad en cualquier resolución.
- **Manejo de Errores (`onError`)**:
  - Incorporar el estado local `imageError: boolean` (inicializado en `false`).
  - Escuchar `onError={() => setImageError(true)}` en el elemento `<img>`.
  - Si `imageError` es `true`, renderizar un estado de alerta clínica con diseño profesional, icono de advertencia, mensaje explicativo ("No fue posible decodificar o cargar la imagen clínica. El archivo podría estar dañado o el formato no es compatible con el navegador.") y un botón de acción para "Abrir archivo original en nueva pestaña" mediante `fileUrl`.
  - Restablecer `imageError` a `false` automáticamente si cambia la prop `fileUrl`.

### Justificación
- Los profesionales médicos requieren ampliar recetas manuscritas o placas radiográficas comprimidas en WebP para confirmar diagnósticos o dosis sin perder legibilidad.
- Un fallo silencioso de decodificación o una imagen rota daña la experiencia clínica; un estado visual explícito con enlace de apertura externa ofrece una vía de escape segura.

### Alternativas Evaluadas
- *Uso de biblioteca externa para zoom (ej. react-zoom-pan-pinch)*: Descartado para evitar agregar dependencias pesadas que compliquen el bundle. La combinación de estado de escala local + estilos Tailwind / CSS inline proporciona máxima estabilidad y cero dependencias adicionales.
- *Uso del tag `<picture>` con fallback a `<img src="original.jpg">`*: Descartado porque la URL provista por el backend apunta a un recurso único (`.webp` o similar), no a múltiples fuentes pregeneradas.

---

## 3. Estrategia de Pruebas Unitarias (`vitest` + `@testing-library/react`)

### Contexto
Se requiere crear pruebas unitarias en `frontend/src/tests/components/documents/DocumentViewer.test.tsx` (y comprobar `DocumentUploader`).

### Decisión
Diseñar la suite de pruebas unitarias cubriendo:
1. **Renderizado de imagen WebP**: Renderizar `DocumentViewer` con `fileName="receta.webp"` y `fileUrl="https://example.com/receta.webp"`, validando que se renderiza el elemento `<img>` con el `src` y `alt` correctos.
2. **Controles de Zoom y Adaptación**: Probar interacción con los botones de zoom (aumento de escala, reducción, reset) y verificar que la escala aplicada al elemento `<img>` se actualiza.
3. **Manejo de Error de Decodificación**: Disparar el evento `fireEvent.error(img)` y corroborar que se oculta la imagen y se muestra el componente de alerta clínica con el mensaje descriptivo y el botón de enlace externo.
4. **Reseteo del estado de error**: Verificar que al cambiar `fileUrl` se reinicia el estado de error.
5. **Modo expandido / pantalla completa**: Probar el botón de alternancia de tamaño (`isExpanded`).
6. **Estado vacío (sin `fileUrl`)**: Verificar que se muestra la información de documento clínico indicando soporte para WebP.

### Justificación
- Cumple estrictamente con la Regla de Oro y la Constitución de MediFlow (cobertura unitaria y TDD).
- Simula fielmente los eventos del navegador sin requerir decodificación binaria real en JSDOM.

