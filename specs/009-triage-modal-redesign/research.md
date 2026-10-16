# Technical Research: Rediseño Visual del Modal y Carga de Archivos en NewDocument

**Feature**: `009-triage-modal-redesign`
**Date**: 2026-10-13
**Status**: Completed

---

## 1. Iconografía: Integración de FontAwesome

### Decision
Utilizar `@fortawesome/react-fontawesome` junto con iconos seleccionados de `@fortawesome/free-solid-svg-icons` (y `@fortawesome/free-regular-svg-icons` si se requiere estilo outline).

### Rationale
- Los paquetes ya se encuentran instalados en `frontend/package.json` (`@fortawesome/fontawesome-svg-core: ^7.3.1`, `@fortawesome/free-solid-svg-icons: ^7.3.1`, `@fortawesome/react-fontawesome: ^3.5.0`).
- Mapeo exacto de iconos para cada elemento visual:
  - Dropzone Folder: `faFolder` o `faFolderOpen` (en contenedor circular con halo/sombra difuminada).
  - Archivo adjunto: `faPaperclip`.
  - Loader de procesamiento: `faSpinner` o `faCircleNotch` con clase `fa-spin` / `animate-spin`.
  - Icono de acción de archivo (eliminar/cancelar): `faTimes` / `faTrashAlt` / `faCircleXmark`.
  - Píldora del modelo IA: `faRobot` / `faBrain` / `faSparkles`.
  - Icono de ajustes / configuración de tarjeta: `faSliders` o `faSlidersH`.
  - Icono de canal de origen / tags: `faHospital` / `faTag`.

### Alternatives Considered
- `react-icons/lu` o `react-icons/fa`: Descartado porque el requerimiento del usuario pide explícitamente "Utiliza los íconos de FontAwesome" mediante el paquete oficial ya configurado en el proyecto.

---

## 2. Paleta de Colores y Estilos (index.css & Tailwind CSS)

### Decision
Vincular el diseño a las variables CSS preexistentes de `frontend/src/index.css` y las utilidades de Tailwind CSS con colores extendidos de `tailwind.config.js`:

- **Primario institucional**: `--primary: #2C5282` (o clase `bg-[#2C5282]` / `bg-mediflow-primary` con hover `hover:bg-[#1E3A5F]`). Utilizado en el botón "Seleccionar archivos" y el botón primario "Continuar".
- **Secundario / Verde Acento**: `--secondary: #6FCF97` / `--green: #10B981`. Utilizado en el badge pill de `GPT-5.2` (`bg-[#6FCF97]/20 text-[#10B981]` o verde esmeralda suave idéntico a las capturas) y en el estado de arrastre activo.
- **Tonos neutros y sombras**:
  - Fondo de la barra de archivo cargado: `bg-slate-100/90` o `bg-[#F1F5F9]`.
  - Textos principales: `--text-main: #1A1816` y `--dark-shade-100: #1F2041`.
  - Bordes suaves de dropzone: `border-slate-300` o `border-dashed border-gray-300` con `border-2`.
  - Fondo de modal / card: Blanco puro `#FFFFFF` con `rounded-3xl` y sombra `shadow-sm` / `shadow-md`.
  - Píldoras de navegación superior: Fondo gris suave/blanco redondeado cápsula `bg-white/80 backdrop-blur border border-slate-200/80 rounded-full`.

### Rationale
- Garantiza total uniformidad de marca con la aplicación MediFlow y cumple rigurosamente con la Constitución v1.2.0.

---

## 3. Navegación RBAC en Píldoras Superiores

### Decision
Implementar la navegación tipo píldora (`[ Enrutamiento | Historial | Solicitudes ]`) utilizando `useNavigate` de `react-router-dom` y `useAuth`:

- **Condición RBAC**:
  - `isAdmin = currentUser?.rol === 'ADMINISTRADOR'`
- **Píldoras Renderizadas**:
  1. `Enrutamiento`: Siempre visible. Ruta `/triaje` (activo por defecto en `NewDocument`).
  2. `Historial`: Siempre visible. Navega a `/documentos`.
  3. `Solicitudes`: Visible **únicamente** si `isAdmin === true`. Navega a `/auditoria`.
- **Comportamiento al clic**:
  - Clic en `Enrutamiento`: Permanece en la vista actual (o restablece vista si aplica).
  - Clic en `Historial`: Ejecuta `navigate('/documentos')`.
  - Clic en `Solicitudes`: Ejecuta `navigate('/auditoria')`.

### Rationale
- Cumple directamente con el requerimiento del usuario aprovechando las rutas ya declaradas y protegidas en `AppRoutes.tsx`.

---

## 4. Preservación del Canal de Origen y Loader de Procesamiento

### Decision
1. **Dropdown Canal de Origen**:
   - Se mantiene el estado `canalOrigen` (`Guardia_Emergencias`, `Consulta_Externa`, `Admision`, `Laboratorio`).
   - Se ubica de forma elegante y limpia dentro de la tarjeta de nuevo análisis (por ejemplo, en un selector superior compacto dentro del modal o junto al título) para que el usuario pueda seleccionarlo antes de procesar sin sobrecargar la dropzone.
2. **Loader de Procesamiento**:
   - Se preserva el estado `loading` que controla la llamada a `subirArchivo` o `procesarDocumento`.
   - Cuando `loading === true`, la barra del archivo muestra:
     - Icono clip + Nombre del archivo.
     - Porcentaje simulado/progreso (ej. `68%` o dinámico mientras procesa).
     - Spinner FontAwesome `faCircleNotch` o `faSpinner` giratorio (`animate-spin`).
     - Tamaño del archivo.
     - Botón "Continuar" deshabilitado con estado visual de procesamiento.
3. **Botón Cancelar**:
   - Limpia el estado `fileToUpload = null`, cancelando la carga y regresando a la dropzone.

---

## 5. Alcance e Invariantes

- **Sidebar**: No se modifica bajo ninguna circunstancia.
- **Funcionalidad de Triaje Backend**: Los contratos con los endpoints de FastAPI y LangGraph (`/api/v1/triage`) permanecen intactos.
- **Diseño Responsive**: Maquetado con flexbox y grid responsivo con Tailwind CSS (`sm:`, `md:`, `lg:`).

