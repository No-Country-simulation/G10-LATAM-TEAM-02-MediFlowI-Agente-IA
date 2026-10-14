# UI Contracts: Rediseño Visual de la Vista de Auditoría Clínica

**Feature**: `010-audit-view-redesign`
**Date**: 2026-10-13
**Status**: Completed

---

## 1. Contrato del Encabezado y Píldoras de Navegación

### Componente: Barra Superior RBAC
- **Elemento**: `<nav aria-label="Navegación de consola">`
- **Píldoras Renderizadas**:
  - `Enrutamiento`: Redirige a `/triaje`
  - `Historial`: Redirige a `/documentos`
  - `Solicitudes`: Ruta activa (`/auditoria`), resaltada con fondo contrastante (`bg-slate-100 text-[#1F2041]`)
- **Restricción RBAC**: Si el usuario no es `ADMINISTRADOR`, solo se visualizan `Enrutamiento` e `Historial`.

### Componente: Título de la Vista
- **Elemento**: `<h1 className="text-3xl sm:text-4xl font-bold text-[#1F2041] text-center my-6">`
- **Texto**: `"Solicitudes de auditoría clínica"`

---

## 2. Contrato de la Tarjeta y Tabla de Datos

### Tarjeta Contenedora
- **Elemento**: `<div className="w-full max-w-6xl bg-white rounded-3xl shadow-sm border border-slate-100 p-6 md:p-8">`
- **Encabezado**: Despejado, **sin selector dropdown**.

### Tabla Responsiva
- **Contenedor**: `<div className="overflow-x-auto">`
- **Columnas**:
  1. `ID`: Columna izquierda, alineación texto izquierda.
  2. `Documento`: Columna central, alineación texto izquierda.
  3. `Confianza`: Columna central, alineación centrada o alineada a izquierda con badge.
  4. `Motivo de Derivación`: Columna central con icono de advertencia.
  5. `Fecha`: Columna alineada a derecha o izquierda.
  6. `Visualizar`: Columna derecha, alineada al centro.

---

## 3. Contrato del Botón de Acción ("Revisar" / "Visualizar")

### Especificación de Estilos y Estados
- **Elemento**: `<Link to={`/auditoria/${documento_id}`} className="...">`
- **Icono**: FontAwesome `faEye` / `FaEye`.
- **Estado Normal (Reposo)**:
  - Estilo: *Outline*
  - Borde: `border border-slate-300` o `border-[#2C5282]/40`
  - Fondo: Transparente (`bg-transparent`)
  - Color de texto / icono: `text-slate-700` o `text-[#2C5282]`
  - Forma: Esquinas redondeadas (`rounded-lg` o `rounded-full`), espaciado ergonómico (`px-3 py-1.5`).
- **Estado Hover**:
  - Fondo: `bg-[#2C5282]` (color `var(--primary)`)
  - Borde: `border-[#2C5282]`
  - Contenido (texto + icono de ojo): `text-white` (`#ffffff`)
  - Transición suave: `transition-all duration-200`

---

## 4. Contrato de Badges de Confianza

### Formato y Estructura Visual
- **Elemento**: `<span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ...">`
- **Punto Indicador**: Círculo de color sólido interior (`w-2 h-2 rounded-full`).
- **Reglas Cromáticas**:

```css
/* Confianza < 25%: Rojo */
badge-critical {
  color: var(--error); /* #F72C2C */
  background-color: rgba(247, 44, 44, 0.1);
  border: 1px solid rgba(247, 44, 44, 0.2);
}

/* Confianza 25% - 50%: Anaranjado */
badge-low {
  color: var(--orange); /* #F59E0B */
  background-color: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

/* Confianza 50% - 75%: Amarillo */
badge-medium {
  color: #D97706; /* tono amarillo/ámbar de alta legibilidad */
  background-color: rgba(234, 179, 8, 0.12);
  border: 1px solid rgba(234, 179, 8, 0.3);
}

/* Confianza > 75%: Verde */
badge-high {
  color: var(--green); /* #10B981 */
  background-color: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
}
```

---

## 5. Contrato del Pie de Paginación

- **Elemento**: `<div className="flex items-center justify-center gap-2 mt-6 pt-4 border-t border-slate-100">`
- **Botones Numéricos**: Píldoras con números con formato de dos dígitos (`01`, `02`, `03`...).
- **Página Activa**: Borde y texto resaltados (`border border-slate-400 font-bold text-[#1F2041] rounded-md px-2.5 py-1`).

