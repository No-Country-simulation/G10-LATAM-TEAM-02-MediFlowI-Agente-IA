# Phase 0 Research: Rediseño Visual de la Vista de Auditoría Clínica

**Feature**: `010-audit-view-redesign`
**Date**: 2026-10-13
**Status**: Completed

---

## 1. Mapeo de Umbrales de Confianza y Paleta Institucional

### Contexto
Actualmente, la función utilitaria `formatConfidence` utiliza una escala de 3 niveles (Alta >= 80%, Media >= 60%, Baja < 60%). El requerimiento del usuario estipula una escala clínica cuádruple específica para la bandeja de auditoría humana:
- `< 25%`: Rojo (`var(--error)` / `#F72C2C`)
- `25% - 50%`: Anaranjado (`var(--orange)` / `#F59E0B`)
- `50% - 75%`: Amarillo (`var(--warning)` / warning / `#EAB308`)
- `> 75%`: Verde (`var(--green)` / `#10B981`)

### Decisiones
- **Decisión**: Implementar una función helper dedicada (o extensión en el componente / utilitario) `getAuditConfidenceBadge(score: number | string | null | undefined)` que evalúe numéricamente el porcentaje y retorne:
  - `percentage`: valor numérico 0-100.
  - `colorVar`: variable CSS y clases Tailwind correspondientes.
  - `dotColor` / `badgeStyle`: estilo visual con píldora suave, punto o indicador sólido que emule fielmente el diseño de la imagen de referencia.
- **Alternativas consideradas**:
  - Modificar `formatConfidence` global: Descartado para evitar efectos colaterales en otras vistas (`DocumentDetail`, `NewDocument`, etc.). Una función modular local o especializada en auditoría garantiza cero regresiones.

---

## 2. Iconografía y Efectos Hover en el Botón "Revisar" / "Visualizar"

### Contexto
El requerimiento exige:
- Utilizar iconos de FontAwesome.
- Mostrar expresamente un icono de ojo (`faEye`).
- Botón estilo *outline*.
- Al hacer *hover*: cambiar el fondo a azul (`var(--primary)` / `#2C5282`) y el contenido (icono + texto) a blanco (`#ffffff`).

### Decisiones
- **Decisión**: Utilizar `@fortawesome/react-fontawesome` con el icono `faEye` de `@fortawesome/free-solid-svg-icons` (o `react-icons/fa` con `FaEye`). Para mantener coherencia con `NewDocument.tsx` y el stack del proyecto, se utilizará `@fortawesome/react-fontawesome` (`FontAwesomeIcon icon={faEye}`) envuelto en un enlace estilizado `<Link to={...}>`.
- **Estilos Tailwind**:
  - Reposo: `border border-slate-300 text-slate-700 bg-transparent rounded-lg px-3 py-1.5 transition-all duration-200`
  - Hover: `hover:bg-[#2C5282] hover:text-white hover:border-[#2C5282]`
- **Alternativas consideradas**:
  - Botón Bootstrap `.btn.btn-outline-primary`: Descartado para cumplir con la regla constitucional de **Tailwind CSS obligatorio** en todo el maquetado.

---

## 3. Estructura de Tabla, Contenedor y Omisión del Filtro Dropdown

### Contexto
La imagen de referencia contiene una tarjeta blanca flotante con bordes redondeados y un dropdown de filtro en la parte superior derecha ("Urgencias Médicas"). El usuario ordenó explícitamente:
- Conservar las columnas y campos actuales de la tabla de `Audit.tsx`.
- Omitir el filtro dropdown.
- Título principal exacto: "Solicitudes de auditoría clínica".

### Decisiones
- **Decisión**:
  - Cabecera: Título centrado `"Solicitudes de auditoría clínica"` con tipografía Quicksand / Inter en negrita (`text-[#1F2041]`, `text-2xl sm:text-3xl font-bold`).
  - Tarjeta: Contenedor `bg-white rounded-2xl md:rounded-3xl shadow-sm border border-slate-100 p-6`.
  - Columnas conservadas exactamente:
    1. `ID` (`documento_id`)
    2. `Documento` (`nombre_archivo`)
    3. `Confianza` (badge cuádruple de color)
    4. `Motivo de Derivación` (`motivo_auditoria` con icono de advertencia)
    5. `Fecha` (`fecha_creacion` formateada)
    6. `Visualizar` / `Acción` (botón outline con ojo FontAwesome)
  - Dropdown omitido: No se renderiza ningún selector dropdown en la esquina de la tabla.

---

## 4. Barra Superior de Píldoras de Navegación (RBAC)

### Contexto
La vista previa en `NewDocument.tsx` implementa la barra de píldoras compartida `[ Enrutamiento | Historial | Solicitudes ]`. La imagen de referencia también muestra esta barra superior centrada.

### Decisiones
- **Decisión**: Reutilizar el hook `useAuth` y las definiciones `NAV_PILLS` de `../types/triageModal.types.ts`.
- En esta vista (`Audit.tsx`), la píldora activa por defecto es `"solicitudes"`.
- Al hacer clic en `"enrutamiento"`, navega a `/triaje`. Al hacer clic en `"historial"`, navega a `/documentos`.
- Mantiene la regla RBAC: usuarios no administradores solo ven Enrutamiento e Historial (aunque la auditoría está restringida por ruta a administradores y coordinadores según la constitución).

---

## 5. Control Visual de Paginación

### Contexto
La imagen de referencia incluye en el pie de la tabla un control de paginación numérico compacto (`01`, `02`, `03`...).

### Decisiones
- **Decisión**: Implementar un control de paginación integrado con diseño acorde a la referencia:
  - Botones numéricos tipo píldora (`01`, `02`...), indicando la página activa con fondo contrastante o borde suave.
  - Si el número de registros es bajo o único, muestra la página 1 activa de manera limpia y accesible.

