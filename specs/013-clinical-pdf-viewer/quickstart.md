# Guía de Validación Rápida: Visor Clínico de PDF con Skeleton Loader y Zoom

**Feature**: `013-clinical-pdf-viewer`  
**Referencia**: Tarea 5.2 / Issue [FE-14] #71  
**Fecha de Actualización**: 2026-10-20  

Esta guía detalla los escenarios de validación ejecutables para verificar que el visor de documentos clínicos PDF e imágenes cumple al 100% con los requerimientos funcionales y criterios de aceptación establecidos en la tarea de frontend.

---

## 1. Prerrequisitos de Entorno

- **Node.js**: v18+ (instalado).
- **Python**: v3.13 con entorno virtual en `backend/.venv`.
- **Servicios en ejecución**:
  - Backend FastAPI: `http://localhost:8000`
  - Frontend Vite: `http://localhost:5173`
- **Navegador**: Chrome, Edge o Firefox moderno con soporte de Fullscreen API.

---

## 2. Ejecución de Pruebas Automatizadas (Vitest)

Ejecutar la suite completa de pruebas unitarias y de integración para `DocumentViewer`:

```bash
cd frontend
npm test -- src/tests/components/documents/DocumentViewer.test.tsx
```

### Resultados Esperados
- Renderizado de Skeleton Loader mientras el PDF/imagen está en estado de carga.
- Transición fluida al estado listo cuando el documento emite `load`.
- Comportamiento de zoom in (+25%), zoom out (-25%) y reset (100%) tanto para imágenes como para documentos PDF.
- Alternancia de pantalla completa (Full Screen API y fallback de ventana).
- Presencia y funcionalidad del botón de descarga directa de archivo original con preservación del nombre clínico.
- Activación de mensaje de error no bloqueante y enlace de contingencia cuando falla la carga del documento.
- **14 de 14 pruebas en verde**.

---

## 3. Validación de Compilación TypeScript y Vite

Asegurar que el compilador de TypeScript y Vite no arrojan errores de sintaxis o tipado:

```bash
cd frontend
npm run build
```

### Resultados Esperados
- `tsc -b`: Cero errores de tipado TypeScript (`0 errors`).
- `vite build`: Compilación limpia en `frontend/dist/`.

---

## 4. Validación del Endpoint de Streaming Binario (Backend)

Comprobar que el endpoint REST entrega el archivo binario con cabecera `inline`:

```bash
# Para documento PDF
curl --noproxy '*' -i http://127.0.0.1:8000/api/v1/documents/DOC-2026-04E835AF/file

# Para imagen clínica
curl --noproxy '*' -i http://127.0.0.1:8000/api/v1/documents/DOC-2026-DEAEC339/file
```

### Respuestas Esperadas
- `HTTP/1.1 200 OK`
- `content-type: application/pdf` o `image/png`
- `content-disposition: inline; filename="..."`

---

## 5. Escenarios de Validación Manual en Navegador

Acceder a `http://localhost:5173`:

### Escenario A: Carga de PDF y Visualización de Skeleton Loader
1. Navegar a `/documentos/DOC-2026-04E835AF`.
2. **Observar**: Se muestra inmediatamente el Skeleton Loader animado con Tailwind (`animate-pulse`) simulando la estructura del documento.
3. Al finalizar la descarga, el esqueleto desaparece suavemente y se presenta el documento PDF interactivo.

### Escenario B: Interacción con la Barra de Herramientas
1. En la barra superior, presionar el botón `+` (Zoom In): la escala aumenta a 125% y 150%.
2. Presionar el botón indicador de porcentaje `150%`: la escala vuelve inmediatamente a `100%`.
3. Presionar el botón `Descargar`: el navegador inicia la descarga del archivo PDF con su nombre original.
4. Presionar el botón de pantalla completa: el visor se expande para ocupar la totalidad del monitor; presionar `Esc` o el botón de reducción para volver a la vista estándar.

### Escenario C: Resiliencia ante Fallos de Red / Enlace Inválido
1. Abrir un documento inexistente o con enlace dañado.
2. Tras el tiempo de espera o evento de error, el visor muestra la tarjeta de contingencia clínica con el mensaje explicativo.
3. El enlace de descarga directa y apertura en nueva pestaña se encuentra plenamente visible y operativo.
