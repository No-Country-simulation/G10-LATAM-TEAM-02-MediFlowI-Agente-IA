# Implementation Plan: Soporte Integral para Carga y Visualización de Imágenes WebP en Visor Clínico

**Branch**: `012-webp-clinical-viewer` | **Date**: 2026-10-17 | **Spec**: [specs/012-webp-clinical-viewer/spec.md](spec.md)

**Input**: Feature specification from `specs/012-webp-clinical-viewer/spec.md`

---

## Summary

Esta funcionalidad amplía la compatibilidad de medios clínicos en MediFlow mediante el soporte nativo e integral para imágenes en formato WebP (`.webp`, `image/webp`). Abarca:
1. Admisión de archivos `.webp` en la zona de arrastre y selección del componente `DocumentUploader.tsx`.
2. Renderizado responsivo de imágenes WebP con controles interactivos de zoom (acercar, alejar, restablecer) y contención dinámica en `DocumentViewer.tsx`.
3. Manejo resiliente de errores ante fallos de decodificación o archivos corruptos mediante `onError` y una alerta clínica profesional con opción de apertura externa.
4. Creación de una suite de pruebas unitarias exhaustiva en `frontend/src/tests/components/documents/DocumentViewer.test.tsx` bajo Vitest y React Testing Library.

---

## Technical Context

**Language/Version**: TypeScript 5.8+ / React 19.2+  
**Primary Dependencies**: React, Lucide/React-Icons (`react-icons/fa`), Tailwind CSS  
**Storage**: N/A (Consumo y renderizado de URLs públicas / blobs de documentos clínicos existentes)  
**Testing**: Vitest 5.0+, `@testing-library/react`, `@testing-library/jest-dom`  
**Target Platform**: Web (Navegadores modernos en entornos hospitalarios de escritorio, tabletas y móviles)  
**Project Type**: Frontend Web Application (React + Vite)  
**Performance Goals**: Renderizado visual inmediato (<1s) y transiciones de zoom fluidas (60fps)  
**Constraints**: Límite de carga de 10 MB, diseño responsive estricto con Tailwind CSS, 100% pruebas en verde con Vitest  
**Scale/Scope**: 2 componentes de frontend (`DocumentUploader.tsx`, `DocumentViewer.tsx`) y 1 suite de prueba unitaria  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio Constitucional | Evaluación | Justificación / Cumplimiento |
|---|---|---|
| **I. Test-First y Puerta de Calidad Estricta en Verde** | PASA | Se implementarán pruebas unitarias exhaustivas en `DocumentViewer.test.tsx` y validación de `DocumentUploader`. Todo cambio debe pasar `vitest run` y `npm run build` sin errores. |
| **II. Consulta Obligatoria ante Dudas** | PASA | Los requerimientos fueron provistos con precisión quirúrgica por el usuario. No existen supuestos ni asimilaciones no validadas. |
| **III. PostgreSQL como Fuente Única de Verdad** | PASA (N/A) | No se alteran esquemas de base de datos ni metadatos clínicos; solo se permite la carga y renderizado del tipo MIME `image/webp` en la capa visual. |
| **IV. RBAC Hospitalario** | PASA | Se respetan los permisos de visualización y roles existentes en las pantallas que integran el uploader y el visor. |
| **V. Trazabilidad Inmutable** | PASA | No se eliminan registros ni se alteran flujos de auditoría del triaje. |
| **Estándar Frontend: Tailwind CSS y Responsividad** | PASA | La interfaz del visor y uploader cumple con maquetado responsive y clases utilitarias de Tailwind, adaptándose a cualquier viewport. |

---

## Project Structure

### Documentation (this feature)

```text
specs/012-webp-clinical-viewer/
├── plan.md              # Este plan de implementación técnica
├── research.md          # Decisiones técnicas y justificaciones (Fase 0)
├── data-model.md        # Modelos de datos, interfaces y estados (Fase 1)
├── quickstart.md        # Guía de validación y ejecución rápida (Fase 1)
├── contracts/           # Contratos de UI y firmas de componentes (Fase 1)
│   └── ui-contracts.md
└── checklists/
    └── requirements.md  # Checklist de calidad de la especificación
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   └── documents/
│   │       ├── DocumentUploader.tsx     # Soporte .webp en tipos aceptados, input file y validación
│   │       └── DocumentViewer.tsx       # Renderizado WebP, zoom ergonómico y captura onError
│   └── tests/
│       └── components/
│           └── documents/
│               └── DocumentViewer.test.tsx # Suite de pruebas unitarias automatizadas
```

**Structure Decision**: Aplicación web frontend pura en React + Vite + TypeScript. Las modificaciones se acotan a los componentes de documentos clínicos existentes sin afectar contratos de API del backend.

---

## Complexity Tracking

> **Violaciones a la Constitución**: Ninguna. No se agregan librerías externas superfluas ni se introducen dependencias redundantes.
