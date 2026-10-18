# Guía de Validación Rápida: Visor Clínico de PDF con Skeleton Loader y Zoom

**Feature**: `013-clinical-pdf-viewer`
**Fecha**: 2026-10-18

Esta guía detalla los escenarios de validación ejecutables para verificar que el visor de documentos clínicos PDF e imágenes cumple al 100% con los requerimientos funcionales y criterios de aceptación.

---

## 1. Prerrequisitos de Entorno

- **Node.js**: v18+ (instalado).
- **Dependencias del Frontend**: Instaladas en `frontend/` (`npm install`).
- **Navegador**: Chrome, Edge o Firefox moderno con soporte de Fullscreen API.

---

## 2. Ejecución de Pruebas Automatizadas (Vitest)

Ejecutar la suite completa de pruebas unitarias y de integración para `DocumentViewer`:

```bash
cd frontend
npm test -- src/tests/components/documents/DocumentViewer.test.tsx
```

### Resultados Esperados
- Renderizado de Skeleton Loader mientras el PDF está en estado de carga.
- Transición fluida al estado listo cuando el documento emite `load`.
- Comportamiento de zoom in, zoom out y reset (100%) tanto para imágenes como para documentos PDF.
- Alternancia de pantalla completa (Full Screen API y fallback de ventana).
- Presencia y funcionalidad del botón de descarga directa de archivo original.
- Activación de mensaje de error no bloqueante y enlace de contingencia cuando falla la carga del documento.
- Cero regresiones en los tests existentes de WebP y DocumentUploader.

---

## 3. Verificación de Compilación y Tipado TypeScript

Asegurar que el compilador de TypeScript y Vite no arrojan errores de sintaxis o tipado:

```bash
cd frontend
npm run build
```

### Resultados Esperados
- `tsc -b`: Cero errores de tipado TypeScript (`0 errors`).
- `vite build`: Compilación exitosa de los bundles en `frontend/dist/`.

---

## 4. Escenarios de Validación Manual en Navegador

Iniciar el servidor de desarrollo del frontend:

```bash
cd frontend
npm run dev
```

### Escenario A: Carga de PDF y Visualización de Skeleton Loader
1. Navegar a la pantalla de Triaje o a la vista de Auditoría HITL con un documento PDF adjunto.
2. **Observar**: Se muestra inmediatamente el Skeleton Loader animado con Tailwind (`animate-pulse`) simulando la estructura del documento.
3. Una vez cargado el PDF, el esqueleto desaparece y se muestra el documento embebido.

### Escenario B: Interacción con la Barra de Herramientas
1. En la barra superior, presionar el botón `+` (Zoom In) dos veces: la escala del documento aumenta a 150%.
2. Presionar el botón indicador de porcentaje `150%`: la escala vuelve inmediatamente a `100%`.
3. Presionar el botón `Descargar`: el navegador inicia la descarga del archivo PDF con su nombre original.
4. Presionar el botón de pantalla completa: el visor se expande para ocupar la totalidad del monitor; presionar `Esc` o el botón de reducción para volver a la vista estándar.

### Escenario C: Resiliencia ante Fallos de Red / Enlace Inválido
1. Abrir un documento con URL no accesible o dañada.
2. Tras el tiempo de espera o evento de error, el visor muestra la tarjeta de contingencia clínica con el mensaje explicativo.
3. El enlace de descarga directa y apertura en nueva pestaña se encuentra plenamente visible y operativo.

