# Implementation Plan: Visor Interactivo y Robusto de Documentos PDF Clínicos con Skeleton Loader y Zoom

**Branch**: `dev-wilmer-gulcochia` | **Fecha de Actualización**: 2026-10-20 | **Spec**: [spec.md](./spec.md)  
**Referencia de Plan de Trabajo**: Tarea 5.2 (`plan de trabajo/PLAN_DE_TRABAJO_FRONTEND_REACT.md`)  
**Issue de GitHub**: [FE-14] #71 (Visor Interactivo de PDFs: Skeleton Loader, Pantalla Completa y Descarga)  

---

## Summary

Modernizar y robustecer la experiencia de visualización clínica de documentos PDF e imágenes en MediFlow mediante una solución end-to-end compuesta por:
1. **Endpoint de Streaming Binario en Backend (`GET /api/v1/documents/{id}/file`)**: Emisión de archivos físicos (PDF/imágenes) desde almacenamiento `LOCAL` u `OCI` con cabeceras `Content-Disposition: inline`.
2. **Normalización en Adaptador de Datos Frontend (`documentsApi.ts`)**: Proyección consistente de `url_archivo` hacia las fichas clínicas de triaje y auditoría.
3. **Visor Clínico Interactivo (`DocumentViewer.tsx`)**: Skeleton loader fluido con Tailwind CSS, controles de zoom interactivo (50% a 250% con reset a 100%), alternancia a pantalla completa mediante la Full Screen API nativa (con fallback CSS), botón de descarga directa de archivo original y panel de contingencia accesible ante fallos.

---

## Technical Context

**Language/Version**: Python 3.13 / TypeScript 6.0.2 / React 19.2.8 (Node.js 18+)  
**Primary Dependencies**: FastAPI, React 19, `react-icons` (FontAwesome), Tailwind CSS 3.4.19  
**Storage**: `backend/storage/recibidos/<documento_id>/original.<ext>` (modo `LOCAL`) / OCI Object Storage (modo `OCI`)  
**Testing**:
- Frontend: Vitest 5.0.2, `@testing-library/react` 16.3.3, `@testing-library/jest-dom` 7.0.1 (14 tests unitarios en verde)
- Backend: Pytest 9.1.1 con suite de API de documentos  
**Target Platform**: Navegadores modernos de escritorio clínico y tabletas médicas (Chrome, Edge, Firefox, Safari)  
**Performance Goals**: Despliegue de Skeleton Loader en <100ms tras recibir `fileUrl`, respuesta a interacciones de zoom en <150ms, transiciones fluidas a 60 fps sin parpadeos  
**Constraints**:
- Cumplimiento de la Constitución v1.2.0: 100% Tailwind CSS (reemplazo de clases Bootstrap en el visor), responsividad obligatoria (768px a 4K)
- Cero regresiones en la suite completa de pruebas del frontend (98 tests en verde)
- Accesibilidad WAI-ARIA (roles `toolbar`, `status`, `alert`, `aria-label` en todos los controles interactivos)

---

## Constitution Check

*GATE: Conformidad estricta con las directrices de MediFlow.*

| Principio Constitucional | Evaluación de Conformidad | Estado |
|---|---|---|
| **I. Test-First y Puerta de Calidad Estricta** | Todas las pruebas unitarias y de integración (14 tests en `DocumentViewer.test.tsx` y suite de backend) pasan al 100% en verde antes de dar por finalizado. | ✅ PASA |
| **II. Consulta Obligatoria ante Dudas** | Especificación y criterios de aceptación alineados con la Tarea 5.2 de frontend y el Issue oficial FE-14. | ✅ PASA |
| **III. PostgreSQL Fuente de Verdad** | La ruta `/api/v1/documents/{id}/file` valida la existencia y pertenencia del documento en PostgreSQL antes de servir el binario. | ✅ PASA |
| **IV. Stack Frontend y Tailwind CSS** | Se erradican las clases legadas de Bootstrap en `DocumentViewer.tsx` adoptando exclusivamente Tailwind CSS y maquetación responsive. | ✅ PASA |
| **V. Trazabilidad y Seguridad** | La descarga directa y apertura en pestaña independiente preservan atributos de seguridad `rel="noreferrer"` y respetan los tokens o permisos de acceso del origen. | ✅ PASA |

---

## Project Structure

### Documentation (this feature)

```text
specs/013-clinical-pdf-viewer/
├── spec.md              # Especificación funcional validada y alineada
├── plan.md              # Este archivo (Plan de arquitectura e implementación)
├── research.md          # Decisiones técnicas: streaming binario, full screen y Tailwind
├── data-model.md        # Diagrama de secuencia end-to-end y máquina de estados
├── quickstart.md        # Guía de ejecución y validación manual/automatizada
├── checklists/
│   └── requirements.md  # Checklist de calidad de requerimientos
└── contracts/
    └── document-viewer.contract.md # Contratos de API de streaming y componente UI
```

### Source Code Impacted

```text
backend/
├── app/
│   └── api/
│       └── v1/
│           └── documents.py         # Endpoint binario GET /documents/{id}/file y proyección de url_archivo

frontend/
├── src/
│   ├── api/
│   │   └── documentsApi.ts          # Mapeo de url_archivo en normalizeBackendDocument()
│   ├── components/
│   │   └── documents/
│   │       ├── DocumentViewer.tsx   # Visor clínico interactivo con Skeleton, Zoom y Fullscreen
│   │       └── DocumentViewer.types.ts # Tipos TypeScript
│   └── tests/
│       └── components/
│           └── documents/
│               └── DocumentViewer.test.tsx # Suite de 14 pruebas unitarias
```

---

## Complexity Tracking

> **Sin violaciones a la Constitución ni complejidades adicionales no justificadas.**

| Item | Evaluación |
|---|---|
| Streaming binario vs Base64 | Se optó por `FileResponse` / bytes streaming para evitar sobrecarga del 33% en la serialización JSON de archivos de gran tamaño. |
| Full Screen API nativa vs Solo CSS | Se implementó enfoque híbrido (API nativa con fallback CSS) para asegurar inmersión en estaciones clínicas y soporte en entornos restringidos. |
