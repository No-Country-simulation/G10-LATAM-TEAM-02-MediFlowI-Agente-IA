# Phase 1 Data Model: Rediseño Visual de la Vista de Auditoría Clínica

**Feature**: `010-audit-view-redesign`
**Date**: 2026-10-13
**Status**: Completed

---

## 1. Entidades del Dominio y Tipos de Datos

### ClinicalDocument (Consumida desde API)
Representa cada documento clínico procesado por el agente IA en espera de revisión humana.

```typescript
export interface ClinicalDocument {
  documento_id: string
  nombre_archivo: string
  fecha_creacion: string
  canal_origen?: string
  clasificacion?: {
    categoria?: string
    score_confianza?: number | null
    codigo_cie10?: string
  }
  decision_enrutamiento?: {
    destino?: string
    requiere_auditoria_humana?: boolean
    motivo_auditoria?: string
  }
}
```

---

## 2. Modelo de Confianza Cuádruple (AuditConfidenceTier)

Estructura de cálculo y mapeo visual para badges de confianza en la bandeja de auditoría humana:

```typescript
export type ConfidenceTierKey = 'CRITICAL' | 'LOW' | 'MEDIUM' | 'HIGH'

export interface AuditConfidenceInfo {
  percentage: number
  tier: ConfidenceTierKey
  label: string
  badgeClass: string
  dotClass: string
  colorVar: string // CSS variable ('var(--error)', 'var(--orange)', etc.)
  hexColor: string
}
```

### Reglas de Mapeo de Umbrales:

| Rango de Confianza | Tier | Variable CSS | Color Hex | Etiqueta / Nivel |
|---|---|---|---|---|
| `< 25%` | `CRITICAL` | `var(--error)` | `#F72C2C` | `< 25%` |
| `25% - 50%` | `LOW` | `var(--orange)` | `#F59E0B` | `25% - 50%` |
| `50% - 75%` | `MEDIUM` | `var(--warning)` | `#EAB308` | `50% - 75%` |
| `> 75%` | `HIGH` | `var(--green)` | `#10B981` | `> 75%` |

*Nota de seguridad*: Ante valores nulos (`null`), no numéricos (`NaN`) o no definidos (`undefined`), se asigna de manera preventiva el rango `CRITICAL` (< 25%, rojo).

---

## 3. Estado de UI y Paginación

```typescript
export interface AuditPaginationState {
  currentPage: number
  itemsPerPage: number
  totalPages: number
  totalItems: number
}
```

- `currentPage`: Página activa (índice 1-based, inicializada en 1).
- `itemsPerPage`: Cantidad de registros visibles por página (ej. 8 o 10 registros).
- `totalPages`: `Math.max(1, Math.ceil(totalItems / itemsPerPage))`.

---

## 4. Estructura de Columnas Preservadas

La tabla mantiene la correspondencia exacta 1:1 con los campos clínicos existentes:

| # | Encabezado Columna | Campo / Expresión Origen | Componente Visual |
|---|---|---|---|
| 1 | **ID** | `item.documento_id` | Texto en negrita con color institucional (`text-primary` / `text-[#2C5282]`) |
| 2 | **Documento** | `item.nombre_archivo` | Texto descriptivo semibold con truncamiento elíptico en pantallas angostas |
| 3 | **Confianza** | `item.clasificacion?.score_confianza` | Badge redondeado con punto indicador y color según la escala cuádruple |
| 4 | **Motivo de Derivación** | `item.decision_enrutamiento?.motivo_auditoria` | Texto explicativo acompañado de icono FontAwesome de alerta (`faTriangleExclamation` / `FaExclamationTriangle`) |
| 5 | **Fecha** | `item.fecha_creacion` | Fecha formateada mediante `formatDateShort` en texto atenuado |
| 6 | **Visualizar** | Enlace a `/auditoria/${item.documento_id}` | Botón outline con icono de ojo FontAwesome (`faEye`), hover azul y texto blanco |

