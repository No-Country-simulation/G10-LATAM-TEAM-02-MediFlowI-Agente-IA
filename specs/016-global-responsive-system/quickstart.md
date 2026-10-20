# Quickstart & Verification Guide: Responsive Design System

**Feature**: `016-global-responsive-system`  
**Date**: 2026-10-20  

---

## Prerrequisitos y Preparación

1. Docker y contenedores de MediFlow iniciados (`mediflow-backend-dev`, `mediflow-frontend-dev`).
2. Navegador web moderno con DevTools de emulación responsive (Google Chrome, Firefox o Edge).
3. Terminal en el directorio `frontend/`.

---

## Escenarios de Validación

### Escenario 1: Navegación Móvil y Drawer de Sidebar (375px)
1. Abrir `http://localhost:5175/` en DevTools emulando un iPhone (375x667).
2. **Verificación**:
   - La barra lateral de escritorio no es visible ni genera scroll horizontal.
   - En la parte superior aparece la barra móvil con el botón de hamburguesa (`FaBars`).
   - Al hacer clic en el botón de hamburguesa, el menú lateral se desliza suavemente desde la izquierda sobre un backdrop oscuro semitransparente.
   - Al tocar cualquier enlace o el fondo oscuro, el menú se cierra automáticamente.

### Escenario 2: Panel de Métricas (Dashboard) en Múltiples Anchos
1. Navegar a `/dashboard` con sesión activa.
2. Probar los anchos de pantalla:
   - **360px**: Las 4 tarjetas de triaje se apilan en 1 sola columna ocupando todo el ancho.
   - **768px**: Las tarjetas se distribuyen en cuadrícula de 2x2.
   - **1280px**: Las tarjetas se alinean en 1 fila de 4 columnas horizontales.

### Escenario 3: Tabla de Documentos y Paginación Táctil (390px)
1. Navegar a `/documentos`.
2. Verificar que el contenedor de la tabla permite desplazarse horizontalmente con el dedo/cursor sin desbordar el ancho de página.
3. Observar la barra de paginación inferior:
   - El texto "Mostrando X a Y de Z documentos" se muestra centrado arriba.
   - Los botones "Anterior", números de página y "Siguiente" se muestran cómodamente debajo con un tamaño táctil mínimo de 40px.

### Escenario 4: Auditoría y Detalle de Documento Dividido (768px vs 1440px)
1. Abrir `/documentos/:id` o `/auditoria/:id`.
2. En pantalla de 1440px: Verificar que el visor de documento y el panel de extracción clínica IA se presenten en 2 columnas paralelas.
3. En pantalla de 768px: Verificar que ambos paneles se apilen verticalmente de forma ordenada, con el visor de PDF/imagen manteniendo sus botones de zoom y ajuste completos.

---

## Comandos de Verificación Automática

```bash
# 1. Compilación estricta TypeScript y Vite
cd frontend
npm run build

# 2. Ejecución de pruebas unitarias y de componentes
npm test
```
