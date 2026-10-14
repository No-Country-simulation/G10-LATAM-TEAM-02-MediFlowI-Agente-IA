# Implementation Plan: Rediseño Visual de la Vista de Auditoría Clínica

**Branch**: `010-audit-view-redesign` | **Date**: 2026-10-13 | **Spec**: [specs/010-audit-view-redesign/spec.md](file:///c:/Users/owl_d/Documents/CURSOS/ORACLE_ONE_AI_FOR_TECH/Hackaton/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/specs/010-audit-view-redesign/spec.md)

**Input**: Feature specification from `specs/010-audit-view-redesign/spec.md`

---

## Summary

Refactorizar el diseño de la vista de Auditoría Clínica en `frontend/src/pages/Audit.tsx` para replicar la estructura visual de la imagen de referencia y cumplir estrictamente los lineamientos solicitados:
1. **Encabezado y Jerarquía**: Barra superior de píldoras de navegación (`[ Enrutamiento | Historial | Solicitudes ]` con `Solicitudes` activa y control RBAC) y título principal exacto centrado **"Solicitudes de auditoría clínica"**.
2. **Tarjeta y Omisión de Filtro**: Contenedor blanco con esquinas redondeadas (`rounded-3xl`), sombra sutil y **omisión total** del menú dropdown de filtros visible en la imagen.
3. **Conservación de Datos**: Preservación íntegra de las 6 columnas existentes (`ID`, `Documento`, `Confianza`, `Motivo de Derivación`, `Fecha`, y `Acción / Visualizar`).
4. **Badges de Confianza Cuádruple**: Escala por colores según porcentaje:
   - `< 25%`: Rojo (`var(--error)` / `#F72C2C`).
   - `25% - 50%`: Anaranjado (`var(--orange)` / `#F59E0B`).
   - `50% - 75%`: Amarillo (`var(--warning)` / `#EAB308`).
   - `> 75%`: Verde (`var(--green)` / `#10B981`).
5. **Botón de Acción**: Botón *outline* con icono de ojo de FontAwesome (`faEye`). Al hacer *hover*, el fondo cambia dinámicamente a azul (`var(--primary)` / `#2C5282`) y el contenido (icono + texto) pasa a blanco puro (`#ffffff`).
6. **Paginación y Responsividad**: Control visual de paginación numerada al pie de la tarjeta y adaptación 100% responsiva con Tailwind CSS.

---

## Technical Context

**Language/Version**: TypeScript 5.8+ / React 19 / Vite
**Primary Dependencies**: React Router 7 (`useNavigate`, `Link`), `@fortawesome/react-fontawesome`, `@fortawesome/free-solid-svg-icons`, Tailwind CSS 3.4+
**Storage**: N/A (Estado local en React; persistencia remota mediante `auditApi` en backend FastAPI / PostgreSQL)
**Testing**: Vitest (`npm --prefix frontend run test`), compilación estricta de TypeScript (`npm --prefix frontend run build`)
**Target Platform**: Navegador Web (Escritorio, Tablet, Móvil - 375px a 1920px)
**Project Type**: Single Page Application (SPA Frontend)
**Performance Goals**: Carga inmediata de vista, transiciones CSS suaves en hover (< 200ms)
**Constraints**:
- Cumplimiento de la Constitución MediFlow v1.2.0 (Tailwind CSS obligatorio, 100% responsive, cero regresiones).
- Sidebar existente completamente inmutable.
- Iconografía exclusiva de FontAwesome (`faEye`, `faTriangleExclamation`).
- Colores vinculados a las variables de `index.css` (`--primary`, `--error`, `--orange`, `--green`).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio Constitucional | Estado | Justificación |
|---|---|---|
| **I. Test-First y Calidad en Verde** | PASA | Se planifican pruebas unitarias en `Audit.test.tsx` cubriendo el renderizado de columnas, badges cuádruples, efectos hover y navegación antes de finalizar. |
| **II. Consulta Obligatoria ante Dudas** | PASA | Todos los requerimientos fueron explicitados por el usuario (título exacto, colores por rangos de confianza, botón outline con hover azul, omisión de dropdown). |
| **III. PostgreSQL como Fuente Única de Verdad** | PASA | No se altera la ingesta ni el modelo de datos; se consumen los mismos endpoints de `auditApi`. |
| **IV. Seguridad y RBAC** | PASA | La barra de píldoras mantiene la restricción de visibilidad según roles (`useAuth`). |
| **V. Trazabilidad Médica Inmutable** | PASA | Se conservan los identificadores `documento_id` y motivos de derivación de auditoría HITL. |
| **Stack CSS: Tailwind CSS & Responsividad** | PASA | Maquetado 100% basado en clases Tailwind con envoltorio `overflow-x-auto` para garantizar responsividad total. |

---

## Project Structure

### Documentation (this feature)

```text
specs/010-audit-view-redesign/
├── spec.md              # Especificación funcional detallada
├── plan.md              # Este plan técnico de implementación
├── research.md          # Fase 0: Decisiones cromáticas, iconográficas y de layout
├── data-model.md        # Fase 1: Tipos de datos, rangos de confianza y estados de UI
├── quickstart.md        # Fase 1: Guía de ejecución y validación
├── contracts/           # Fase 1: Contratos visuales de componentes y estilos
│   └── ui-contracts.md
├── checklists/
│   └── requirements.md  # Checklist de calidad de especificación
└── tasks.md             # Fase 2: Tareas de implementación TDD (/speckit-tasks)
```

### Source Code Impact

```text
frontend/src/
├── pages/
│   ├── Audit.tsx        # Refactorización del maquetado visual, tabla, badges y botones
│   └── Audit.test.tsx   # Suite de pruebas unitarias para validar columnas, badges y botón outline
```

---

## Complexity Tracking

> **Sin violaciones ni complejidad técnica innecesaria.** No se incorporan dependencias externas adicionales. Toda la refactorización aprovecha las librerías ya instaladas (`@fortawesome/react-fontawesome`, `react-router-dom`, `tailwindcss`).
