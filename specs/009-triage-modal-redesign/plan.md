# Implementation Plan: Rediseño Visual del Modal y Carga de Archivos en NewDocument

**Branch**: `009-triage-modal-redesign` | **Date**: 2026-10-13 | **Spec**: [specs/009-triage-modal-redesign/spec.md](file:///c:/Users/owl_d/Documents/CURSOS/ORACLE_ONE_AI_FOR_TECH/Hackaton/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/specs/009-triage-modal-redesign/spec.md)

**Input**: Feature specification from `specs/009-triage-modal-redesign/spec.md`

---

## Summary

Refactorizar la jerarquía visual de `NewDocument` para alinearla al 100% con las 3 imágenes de referencia:
1. Barra superior tipo cápsula con navegación RBAC dinámica (`[ Enrutamiento | Historial | Solicitudes ]` para `ADMINISTRADOR`, y `[ Enrutamiento | Historial ]` para otros roles, con redirección a `/triaje`, `/documentos`, `/auditoria`).
2. Encabezado centrado de bienvenida (`Buen día Dr. [Nombre]` con subtítulo descriptivo).
3. Barra de motor IA con badge verde del modelo (`GPT-5.2`) e icono de ajustes de FontAwesome.
4. Tarjeta modal "Ejecutar nuevo análisis" con bordes curvados (`rounded-3xl`), dropzone estilizada con icono FontAwesome `faFolder`, botón institucional "Seleccionar archivos" (`--primary`), y selector funcional de canal de origen preservado.
5. Fila horizontal estilizada para archivo seleccionado (icono `faPaperclip`, nombre, tamaño y acciones "Cancelar" / "Continuar").
6. Estado de procesamiento con spinner animado de FontAwesome (`faSpinner` / `faCircleNotch`) y porcentaje de progreso dentro de la fila del archivo mientras el backend evalúa el documento.
7. Maquetado completo con Tailwind CSS y respeto estricto a las variables de color predefinidas en `index.css`. Sidebar intacto.

---

## Technical Context

**Language/Version**: TypeScript 5.8+ / ECMAScript 2022
**Primary Dependencies**: React 19, React Router 7 (`useNavigate`), `@fortawesome/react-fontawesome`, `@fortawesome/free-solid-svg-icons`, Tailwind CSS 3.4+
**Storage**: N/A (Estado local en React; persistencia delegada al backend FastAPI / PostgreSQL)
**Testing**: Vitest (`npm run test`), compilación TypeScript estricta (`npm run build`)
**Target Platform**: Web Browser (Responsive: Desktop, Tablet, Mobile)
**Project Type**: Single Page Application (SPA Frontend)
**Performance Goals**: Renderizado inmediato y transiciones en < 300ms, cero lag en dropzone
**Constraints**:
- Cumplimiento de la Constitución MediFlow v1.2.0 (Tailwind CSS obligatorio, 100% responsive, cero regresiones en tests).
- Preservar dropdown `canalOrigen` y spinner de carga durante llamadas API.
- Sidebar actual completamente inmutable.
- Iconografía exclusiva con FontAwesome (`@fortawesome/react-fontawesome`).
- Respeto a variables de color corporativas en `index.css` (`--primary`, `--secondary`, etc.).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio Constitucional | Estado | Justificación |
|---|---|---|
| **I. Test-First y Calidad en Verde** | PASA | `npm run build` y `vitest run` deben aprobar sin errores de TypeScript ni regresiones. |
| **II. Consulta Obligatoria ante Dudas** | PASA | Especificación y aclaraciones del usuario (FontAwesome, `index.css`, RBAC en píldoras) formalizadas. |
| **III. PostgreSQL como Fuente Única de Verdad** | PASA | La vista continúa enviando las cargas al backend FastAPI para su persistencia en `mediflow_dev`. |
| **IV. Seguridad y RBAC** | PASA | Solo `ADMINISTRADOR` accede a la pestaña de `Solicitudes` (auditoría HITL). |
| **V. Trazabilidad Médica Inmutable** | PASA | No se altera el flujo de auditoría ni la creación de episodios clínicos. |
| **Stack CSS: Tailwind CSS & Responsividad** | PASA | Maquetado 100% con clases de Tailwind CSS y diseño adaptable. |

---

## Project Structure

### Documentation (this feature)

```text
specs/009-triage-modal-redesign/
├── spec.md              # Especificación de requisitos funcionales y diseño
├── plan.md              # Este plan de implementación arquitectónica
├── research.md          # Fase 0: Investigación técnica y decisiones de diseño
├── data-model.md        # Fase 1: Arquitectura de estados y tipos de datos
├── quickstart.md        # Fase 1: Guía de ejecución y validación
├── contracts/           # Fase 1: Contratos de UI y eventos
│   └── ui-contracts.md
├── checklists/
│   └── requirements.md  # Checklist de calidad de especificación
└── tasks.md             # Fase 2: Tareas de implementación TDD (/speckit-tasks)
```

### Source Code Impact

```text
frontend/src/
├── pages/
│   ├── NewDocument.tsx       # Modificación principal: Refactorización del modal, cabecera y píldoras
│   └── NewDocument.test.tsx  # Pruebas unitarias de renderizado visual y RBAC de píldoras
```

---

## Complexity Tracking

> **Sin violaciones constitucionales.** No se introducen dependencias redundantes; se utilizan librerías ya instaladas en el repositorio (`@fortawesome/react-fontawesome`, `react-router-dom`, `tailwindcss`).
