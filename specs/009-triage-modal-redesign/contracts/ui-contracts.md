# UI Contracts: Modal de Triaje y Píldoras de Navegación

**Feature**: `009-triage-modal-redesign`
**Date**: 2026-10-13
**Status**: Completed

---

## 1. Contrato del Selector de Píldoras RBAC (`PillNavigation`)

### Entradas (Props o Contexto)
- `currentRoute`: string (ej. `/triaje` o `/admin-triaje`)
- `userRole`: `'ADMINISTRADOR' | 'OPERADOR' | 'AUDITOR' | 'SUPERVISOR'`

### Salidas y Eventos
- `onNavigate(route: string)`: Desencadena `navigate(route)`.

### Reglas de Renderizado
| Rol | Píldoras Visibles | Acción al Clic |
|---|---|---|
| `ADMINISTRADOR` | `Enrutamiento`, `Historial`, `Solicitudes` | Redirige a `/triaje`, `/documentos`, `/auditoria` respectivamente |
| `OPERADOR` | `Enrutamiento`, `Historial` | Redirige a `/triaje`, `/documentos` |
| `AUDITOR` | `Enrutamiento`, `Historial` | Redirige a `/triaje`, `/documentos` |
| `SUPERVISOR` | `Enrutamiento`, `Historial` | Redirige a `/triaje`, `/documentos` |

---

## 2. Contrato de la Tarjeta Modal de Análisis (`TriageUploadModal`)

### Entradas
- `userDisplayName`: string (ej. `"Dr. Lucas"` o nombre del usuario)
- `canalOrigen`: string
- `onCanalOrigenChange(canal: string)`: callback
- `fileToUpload`: `File | null`
- `onFileSelect(file: File | null)`: callback
- `onSubmitTriage(e: React.FormEvent)`: callback
- `loading`: boolean
- `error`: string | null

### Eventos de Interacción del Archivo
1. **Drop / Select File**:
   - `onDragOver(e)`: Previene default y añade indicador visual de arrastre activo (`border-emerald-400 bg-emerald-50/30`).
   - `onDrop(e)`: Extrae `e.dataTransfer.files[0]`, valida tamaño (<= 10MB) y tipo, asigna archivo al estado.
   - `onChange(e)`: Extrae archivo desde input file nativo oculto activado por botón o enlace.
2. **Descarte de Archivo (Cancelar)**:
   - Limpia `fileToUpload = null` y reinicia el valor del input file.
3. **Confirmación (Continuar)**:
   - Dispara `onSubmitTriage` ejecutando `subirArchivo` con el `docId` y el `canalOrigen` actual.

