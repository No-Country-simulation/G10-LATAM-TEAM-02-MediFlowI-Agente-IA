# Quickstart & Validation Guide: Rediseño Visual de la Vista de Auditoría Clínica

**Feature**: `010-audit-view-redesign`
**Date**: 2026-10-13
**Status**: Completed

---

## 1. Prerrequisitos y Entorno

- Node.js 20+ y npm instalados.
- Dependencias de frontend al día (`npm --prefix frontend install`).

---

## 2. Verificación Automatizada (Test Quality Gate)

Para certificar que no existen regresiones ni errores de tipado o compilación:

```bash
# 1. Compilación estricta de TypeScript y bundling Vite
npm --prefix frontend run build

# 2. Ejecución de la suite completa de pruebas unitarias de frontend
npm --prefix frontend run test
```

---

## 3. Lista de Verificación Visual y Manual

1. **Ruta y Acceso**:
   - Iniciar el servidor local: `npm --prefix frontend run dev`.
   - Iniciar sesión con un usuario con rol `ADMINISTRADOR` o `COORDINADOR`.
   - Navegar a la ruta: `http://localhost:5173/auditoria`.

2. **Cabecera y Píldoras**:
   - Verificar la presencia de la barra de píldoras centrada en la parte superior.
   - Confirmar que la opción activa es `Solicitudes`.
   - Confirmar que el título principal centrado es exactamente: **"Solicitudes de auditoría clínica"**.

3. **Tarjeta y Ausencia de Dropdown**:
   - La tabla debe encontrarse contenida en una tarjeta blanca con esquinas redondeadas y sombra suave.
   - Constatar que **NO** aparece ningún dropdown de filtro en la cabecera de la tarjeta.

4. **Columnas de la Tabla**:
   - Verificar la presencia de las 6 columnas en el orden requerido:
     1. `ID`
     2. `Documento`
     3. `Confianza`
     4. `Motivo de Derivación`
     5. `Fecha`
     6. `Visualizar` (o `Acción`)

5. **Badges de Confianza (4 Colores)**:
   - Para valores < 25%: Badge en rojo (`var(--error)` / `#F72C2C`).
   - Para valores 25% - 50%: Badge en anaranjado (`var(--orange)` / `#F59E0B`).
   - Para valores 50% - 75%: Badge en amarillo (`var(--warning)` / `#EAB308`).
   - Para valores > 75%: Badge en verde (`var(--green)` / `#10B981`).

6. **Botón de Acción / Visualización**:
   - El botón muestra el icono de un ojo de FontAwesome (`faEye`).
   - Posee contorno *outline* en reposo.
   - Al posicionar el cursor sobre él (*hover*), su fondo cambia a azul (`var(--primary)` / `#2C5282`) y su contenido (icono y texto) se vuelve blanco puro (`#ffffff`).
   - Al hacer clic, redirige hacia `/auditoria/:documento_id`.

7. **Paginación y Responsividad**:
   - En el pie de la tarjeta se observan los controles de paginación estilizados.
   - En pantallas móviles (< 768px), la tabla permite scroll horizontal sin deformar el contenedor ni el sidebar.

