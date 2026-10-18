# Implementation Plan: Visor Interactivo y Robusto de Documentos PDF Clínicos con Skeleton Loader y Zoom

**Branch**: `013-clinical-pdf-viewer` | **Date**: 2026-10-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/013-clinical-pdf-viewer/spec.md`

## Summary

Modernizar y fortalecer el componente `DocumentViewer.tsx` del frontend clínico de MediFlow para proporcionar una experiencia de visualización fluida, accesible y resiliente tanto para documentos PDF como para imágenes clínicas. La solución técnica incorpora un indicador de carga esqueleto (Skeleton Loader) animado con Tailwind CSS mientras se descarga y prepara el documento, una barra de herramientas unificada con controles de zoom (acercar, alejar, restablecer al 100%), botón de descarga directa del archivo original, alternancia a pantalla completa mediante la Full Screen API nativa (con fallback CSS de ventana completa), y un panel de contingencia ante errores de renderizado embebido sin perder el contexto asistencial.

## Technical Context

**Language/Version**: TypeScript 6.0.2 / React 19.2.8 (Node.js 18+)

**Primary Dependencies**: React 19, `react-icons` (FontAwesome icons), Tailwind CSS 3.4.19

**Storage**: N/A (Estado reactivo del cliente; visualización de archivos servidos mediante URLs seguras o Blob URLs)

**Testing**: Vitest 5.0.2, `@testing-library/react` 16.3.3, `@testing-library/jest-dom` 7.0.1

**Target Platform**: Navegadores modernos de escritorio clínico y tabletas médicas (Chrome, Edge, Firefox, Safari)

**Project Type**: Componente de interfaz de usuario para aplicación web SPA (React / Vite)

**Performance Goals**: Despliegue de Skeleton Loader en <100ms tras recibir `fileUrl`, respuesta a interacciones de zoom en <150ms, transiciones fluidas a 60 fps sin parpadeos

**Constraints**:
- Cumplimiento de la Constitución v1.2.0: 100% Tailwind CSS (reemplazo de clases Bootstrap en el visor), responsividad obligatoria (768px a 4K)
- Cero regresiones en los 87 tests existentes del frontend
- Accesibilidad WAI-ARIA (roles `toolbar`, `status`, `alert`, `aria-label` en todos los controles interactivos)

**Scale/Scope**: Actualización directa de `DocumentViewer.tsx` y expansión de la suite de pruebas `DocumentViewer.test.tsx`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio Constitucional | Evaluación de Conformidad | Estado |
|---|---|---|
| **I. Test-First y Puerta de Calidad Estricta** | Los 87 tests actuales del frontend pasan al 100% en verde. Se planifica la expansión de pruebas unitarias cubriendo todas las historias de usuario (skeleton, zoom, fullscreen, descarga y fallback) antes de finalizar. | ✅ PASA |
| **II. Consulta Obligatoria ante Dudas** | Especificación y criterios de aceptación derivados directamente del requerimiento explícito sin asunciones no fundamentadas. | ✅ PASA |
| **III. PostgreSQL Fuente de Verdad** | No muta la base de datos de desarrollo. El componente consume las URLs de documentos provistas por las consultas clínicas. | ✅ PASA |
| **IV. Stack Frontend y Tailwind CSS** | Se erradican las clases legadas de Bootstrap en `DocumentViewer.tsx` adoptando exclusivamente Tailwind CSS y maquetación responsive. | ✅ PASA |
| **V. Trazabilidad y Seguridad** | La descarga directa y apertura en pestaña independiente preservan atributos de seguridad `rel="noreferrer"` y respetan los tokens o permisos de acceso del origen. | ✅ PASA |

## Project Structure

### Documentation (this feature)

```text
specs/013-clinical-pdf-viewer/
├── spec.md              # Especificación funcional validada
├── plan.md              # Este archivo (Plan de implementación)
├── research.md          # Fase 0: Decisiones arquitectónicas y alternativas
├── data-model.md        # Fase 1: Interfaces TypeScript y máquina de estados
├── quickstart.md        # Fase 1: Guía de ejecución y validación
├── checklists/
│   └── requirements.md  # Lista de verificación de calidad de la especificación
└── contracts/
    └── document-viewer.contract.md # Fase 1: Contrato de interfaz y accesibilidad
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   └── documents/
│   │       ├── DocumentViewer.tsx    # Componente modernizado con Skeleton y Controles
│   │       └── DocumentUploader.tsx  # Componente existente de subida
│   └── tests/
│       └── components/
│           └── documents/
│               └── DocumentViewer.test.tsx # Suite de pruebas ampliada
```

**Structure Decision**: El trabajo se concentra modularmente en `frontend/src/components/documents/DocumentViewer.tsx` y su suite de pruebas unitarias correspondiente en `frontend/src/tests/components/documents/DocumentViewer.test.tsx`, manteniendo la cohesión y evitando acoplamiento innecesario con otras áreas del sistema.

## Complexity Tracking

> **Sin violaciones a la Constitución ni complejidades adicionales no justificadas.**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| *Ninguna* | *N/A* | *N/A* |
