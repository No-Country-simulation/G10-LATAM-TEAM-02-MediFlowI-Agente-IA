# Implementation Plan: Sistema Global de Diseño Adaptable y Responsive

**Branch**: `016-global-responsive-system` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/016-global-responsive-system/spec.md`

---

## Summary

Implementar la adaptación responsiva integral del frontend de MediFlow utilizando Tailwind CSS conforme a la Constitución del proyecto, resolviendo los problemas actuales de desbordamiento horizontal (`overflow-x`), superposición de la barra lateral en viewports menores a 1024px, colapso de tablas clínicas de alta densidad y rotura visual en paneles KPI y visores divididos.

El enfoque técnico se basa en:
1. Shell responsivo con `MainLayout` y `Sidebar` retráctil tipo drawer en `< 1024px` con cabecera móvil.
2. Contenedores de tabla con aislamiento de scroll horizontal y controles de paginación apilables.
3. Migración de cuadrículas fijas a Tailwind Responsive Grid (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`).
4. Reorganización de visores documentales y detalles clínicos a modo apilado vertical en pantallas compactas.
5. Modales clínicos con altura máxima acotada al viewport (`max-h-[90vh]`) y scroll interno.

---

## Technical Context

**Language/Version**: TypeScript 5.6+, React 18+  
**Primary Dependencies**: Tailwind CSS, React Router DOM 6, React Icons  
**Storage**: N/A (Frontend Layout & Component Styling, sin impacto en base de datos)  
**Testing**: Vitest, React Testing Library (`npm test`), TypeScript build (`npm run build`)  
**Target Platform**: Navegadores modernos (Chrome, Safari iOS 15+, Firefox, Edge) en Desktop, Tablets clínicas (iPad) y Smartphones  
**Project Type**: Single Page Application (SPA Web)  
**Performance Goals**: 60 fps en transiciones de layout, 0 desbordamiento horizontal de página, puntuación de usabilidad móvil > 90  
**Constraints**: Tailwind CSS obligatorio sin hojas Vanilla CSS adicionales para maquetado; mantener estilos limpios y accesibles para entornos clínicos sin emojis recargados  
**Scale/Scope**: Todas las vistas de la aplicación: Shell (`MainLayout`, `Sidebar`), `Dashboard`, `Documents`, `DocumentDetail`, `AuditDetail`, `PatientsManagementView`, `UsersManagementView`, `EmergencyAlertToast` y Modales  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio Constitucional | Estado | Justificación |
|---|---|---|
| **I. Test-First y Puerta de Calidad Estricta** | APROBADO | Se diseñan y actualizan pruebas unitarias para layout móvil, drawer y controles antes de finalizar la implementación (`npm test` y `npm run build` en verde). |
| **II. Consulta Obligatoria ante Dudas** | APROBADO | Las decisiones de diseño (breakpoints estándar, drawer para sidebar) respetan las directrices de la Constitución y la solicitud explícita del usuario. |
| **III. PostgreSQL Fuente de Verdad** | APROBADO | La feature es 100% de capa de presentación frontend; no muta ni altera esquemas ni datos de PostgreSQL. |
| **IV. RBAC Hospitalario** | APROBADO | Se preservan intactos todos los controles de acceso por roles en el sidebar y vistas. |
| **V. Trazabilidad Médica Inmutable** | APROBADO | No se modifica ningún flujo de auditoría ni trazabilidad clínica. |
| **Stack CSS: Tailwind CSS obligatorio** | APROBADO | Se emplean exclusivamente utilidades y responsive prefixes de Tailwind CSS (`sm:`, `md:`, `lg:`, `xl:`). |

---

## Project Structure

### Documentation (this feature)

```text
specs/016-global-responsive-system/
├── spec.md              # Especificación funcional validada
├── plan.md              # Este plan de implementación técnica
├── research.md          # Decisiones de arquitectura técnica y breakpoints
├── quickstart.md        # Guía de verificación en múltiples resoluciones
├── contracts/
│   └── ui-layout-contract.md # Contratos de layout y breakpoints
├── checklists/
│   └── requirements.md  # Lista de verificación de calidad del spec
└── tasks.md             # Tareas ejecutables TDD (fase 2)
```

### Source Code Impacted

```text
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── MainLayout.tsx         # Cabecera móvil, drawer y flex fluido
│   │   │   └── Sidebar.tsx            # Adaptabilidad off-canvas y botón de cierre
│   │   ├── common/
│   │   │   └── EmergencyAlertToast.tsx # Anclaje responsivo y touch targets
│   │   └── documents/
│   │       ├── DocumentTable.tsx      # Scroll horizontal contenido y paginación apilable
│   │       └── DocumentViewer.tsx     # Ajuste responsivo de visores
│   ├── pages/
│   │   ├── Dashboard.tsx              # Grid responsivo Bento (1/2/4 columnas)
│   │   ├── Documents.tsx              # Filtros y tabla responsivos
│   │   ├── DocumentDetail.tsx         # Modo apilado en pantallas intermedias
│   │   ├── AuditDetail.tsx            # Layout adaptable de auditoría
│   │   ├── PatientsManagementView.tsx # Tabla, modales y KPIs con Tailwind
│   │   └── UsersManagementView.tsx    # Tabla y filtros responsivos
│   └── tests/
│       └── components/
│           └── layout/
│               └── ResponsiveLayout.test.tsx # Pruebas del drawer móvil y breakpoints
```

---

## Complexity Tracking

*No violations detected. Arquitectura conforme a la Constitución.*
