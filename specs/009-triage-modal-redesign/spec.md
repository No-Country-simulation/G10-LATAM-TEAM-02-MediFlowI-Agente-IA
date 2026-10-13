# Feature Specification: Rediseño Visual del Modal y Carga de Archivos en NewDocument

**Feature Branch**: `009-triage-modal-redesign`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Refactoriza el diseño del modal, el título y la forma en la que se ve un archivo cuando ya ha sido subido en el modal en la vista del archivo NewDocument para que sea igual al que se muestra en las imágenes. Preserva el dropdown que establece el canal de origen y también el loader que se muestra al procesar un archivo. Limítate a refactorizar el diseño para que sea lo más semejante posible a las imágenes, no es necesario modificar la funcionalidad. No hagas caso del diseño del sidebar ya que ese se encuentra bien tal cual está al día de hoy. Utiliza los íconos de FontAwesome. Respeta la paleta de colores. El archivo index.css ya contiene el nombre de las variables con el color de la paleta predefinida. Por otro lado, en cuanto la navegación a través de las píldoras: Solamente un ADMINISTRADOR puede ver tres opciones (Enrutamiento, Historial y Solicitudes), la sección de enrutamiento corresponde a la pantalla de 'NewDocument', el Historial compete a la vista del historial de documentos procesados con anterioridad y la pantalla de solicitudes respecta a la pantalla de solicitudes de auditoría; todas estas pantallas ya existen, solamente tienes que colocar esa redirección al dar click sobre la píldora respectiva. El resto de usuarios con un rol distinto solamente pueden ver las opciones 'Enrutamiento' e 'Historial'."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Presentación Visual de Bienvenida, Píldoras RBAC y Zona de Ingesta (Priority: P1)

Como profesional clínico o usuario del sistema, al ingresar a la consola de triaje (`NewDocument`), deseo ver una interfaz centrada y moderna con un saludo personalizado, las píldoras de navegación según mi rol (`ADMINISTRADOR` ve Enrutamiento, Historial y Solicitudes; otros roles ven solo Enrutamiento e Historial), y un modal estilizado idéntico a las guías visuales con íconos de FontAwesome y la paleta de colores corporativa (`index.css`), preservando el selector de canal de origen.

**Why this priority**: Es la pantalla inicial y el punto de entrada principal para la interacción con el sistema de triaje automatizado; define la primera impresión de usabilidad y navegación médica.

**Independent Test**:
- Acceder como usuario `ADMINISTRADOR`: comprobar que el selector de píldoras muestra 3 pestañas: `Enrutamiento` (activa), `Historial` (redirige a `/documentos`) y `Solicitudes` (redirige a `/auditoria`).
- Acceder con cualquier otro rol (`OPERADOR`, `AUDITOR`, `SUPERVISOR`): comprobar que solo se visualizan 2 opciones: `Enrutamiento` e `Historial`.
- Comprobar que los iconos provienen de FontAwesome (`@fortawesome/react-fontawesome`) y que los colores respetan las variables de `index.css` (`--primary`, `--secondary`, etc.).

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con rol `ADMINISTRADOR`, **When** ingresa a la vista de triaje, **Then** visualiza la barra de píldoras superior con 3 opciones: `Enrutamiento`, `Historial` y `Solicitudes`. Al hacer clic en `Historial` navega a `/documentos`, y en `Solicitudes` navega a `/auditoria`.
2. **Given** un usuario autenticado con un rol distinto de `ADMINISTRADOR` (ej. `OPERADOR`, `AUDITOR`, `SUPERVISOR`), **When** ingresa a la vista de triaje, **Then** la barra de píldoras muestra únicamente 2 opciones: `Enrutamiento` e `Historial`, ocultando la opción `Solicitudes`.
3. **Given** el modal principal en estado inicial vacío, **When** el usuario inspecciona la zona de carga, **Then** ve una dropzone delimitada con borde punteado suave, un icono de carpeta de FontAwesome (`faFolder` o `faFolderOpen`) con halo difuso, textos instructivos, enlace de búsqueda y botón `Seleccionar archivos` con el color institucional `--primary` (`#2C5282`), manteniendo visible y funcional el selector de canal de origen.

---

### User Story 2 - Visualización Estilizada del Archivo Cargado y Acciones de Control (Priority: P2)

Como usuario que selecciona o arrastra un archivo al modal, deseo ver una representación compacta, sobria y elegante del archivo cargado (con icono de clip de FontAwesome `faPaperclip`, nombre del archivo, tamaño en MB e icono de acción) junto con los botones de acción "Cancelar" y "Continuar", coincidiendo con la imagen de referencia y respetando la paleta de colores.

**Why this priority**: Proporciona retroalimentación clara sobre el archivo adjunto listo para ser procesado antes de confirmar el triaje.

**Independent Test**: Adjuntar un archivo PDF o imagen: la dropzone se transforma en la barra horizontal con esquinas redondeadas y fondo suave, icono `faPaperclip`, nombre del archivo, peso formateado (ej. `4.6 MB`), botón "Cancelar" y botón primario "Continuar" (`--primary`).

**Acceptance Scenarios**:

1. **Given** un archivo local seleccionado, **When** se adjunta al componente, **Then** el modal reemplaza la dropzone por una barra horizontal estilizada con fondo neutro suave (`bg-slate-100` / `var(--dark-shade-5)`), mostrando a la izquierda el icono FontAwesome `faPaperclip`, el nombre del archivo y a la derecha su tamaño formateado.
2. **Given** un archivo cargado en el modal, **When** el usuario presiona "Cancelar" o el icono de descarte, **Then** el archivo se remueve y el modal regresa al estado inicial de dropzone vacía.
3. **Given** un archivo cargado en el modal, **When** el usuario hace clic en el botón primario "Continuar" (fondo `--primary`), **Then** se desencadena el envío del documento al flujo de triaje manteniendo el canal de origen seleccionado.

---

### User Story 3 - Retroalimentación de Procesamiento y Loader Circular con FontAwesome (Priority: P3)

Como usuario clínico que inicia el análisis de un documento, deseo ver el estado de procesamiento integrado armónicamente dentro del modal (con porcentaje de progreso, loader/spinner animado de FontAwesome `faSpinner` o `faCircleNotch` y botones en estado de carga) sin perder la respuesta de diagnóstico posterior.

**Why this priority**: Evita incertidumbre operativa durante la ejecución del agente autónomo de IA y mantiene la coherencia visual con la imagen de referencia durante la fase de análisis.

**Independent Test**: Al enviar el documento con el botón "Continuar", la barra del archivo refleja el estado de procesamiento con loader circular animado de FontAwesome y/o porcentaje, mientras los botones quedan deshabilitados hasta recibir la respuesta del backend.

**Acceptance Scenarios**:

1. **Given** un documento en proceso de análisis por el agente, **When** la petición está en curso (`loading === true`), **Then** la barra del archivo muestra un spinner animado de FontAwesome (`faSpinner` / `faCircleNotch` con animación de giro), el porcentaje de avance, y el botón "Continuar" permanece en estado de carga deshabilitado.
2. **Given** la finalización del análisis del agente, **When** se recibe la respuesta con éxito o error, **Then** se detiene el loader y se presentan los resultados del triaje o la notificación correspondiente sin romper la estructura de la consola.

---

### Edge Cases

- **Navegación entre píldoras con archivo cargado**: Si el usuario hace clic en `Historial` o `Solicitudes`, la navegación debe operar limpiamente a través de `react-router-dom` sin bloqueos de confirmación innecesarios.
- **Archivo con nombre excesivamente largo**: El contenedor del archivo debe aplicar truncamiento elíptico (`truncate`) en el texto del nombre para no desbordar en pantallas pequeñas.
- **Acciones durante procesamiento**: Los botones de navegación, "Cancelar" y "Continuar" deben deshabilitarse o protegerse contra doble clic mientras la llamada al backend está en curso.
- **Visualización Responsive**: En dispositivos móviles, la barra de píldoras y los botones inferiores deben acomodarse armónicamente sin generar scroll horizontal inesperado.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La vista `NewDocument` DEBE adoptar la jerarquía visual de cabecera centrada compuesta por:
  - Selector superior de píldoras de navegación.
  - Saludo principal (`Buen día Dr. [Nombre]` o equivalente).
  - Subtítulo explicativo de bienvenida al panel de control.
- **FR-002**: El selector de píldoras superior DEBE implementar control de acceso por roles (RBAC):
  - Si el usuario autenticado tiene rol `ADMINISTRADOR`: Muestra **3 opciones**: `Enrutamiento`, `Historial` y `Solicitudes`.
  - Si el usuario autenticado tiene cualquier otro rol: Muestra **únicamente 2 opciones**: `Enrutamiento` e `Historial`.
  - Al hacer clic en `Enrutamiento`: Permanece en `/triaje`.
  - Al hacer clic en `Historial`: Redirecciona a la ruta `/documentos`.
  - Al hacer clic en `Solicitudes`: Redirecciona a la ruta `/auditoria`.
- **FR-003**: Todos los iconos del componente DEBEN provenir de la librería **FontAwesome** (`@fortawesome/react-fontawesome` y `@fortawesome/free-solid-svg-icons` / `@fortawesome/free-regular-svg-icons`), tales como `faFolder` (carpeta de dropzone), `faPaperclip` (clip de archivo adjunto), `faSpinner` o `faCircleNotch` (loader circular de procesamiento), `faSliders` o `faSlidersH` (configuración) y `faRobot` / `faBrain` (agente IA).
- **FR-004**: Los estilos DEBEN respetar estrictamente la paleta de colores definida en `frontend/src/index.css`:
  - Color principal: `--primary: #2C5282` (botones de acción primarios como "Seleccionar archivos" y "Continuar").
  - Color secundario / verde: `--secondary: #6FCF97` o `--green: #10B981` (píldora del modelo `GPT-5.2` y estados de éxito).
  - Tonos oscuros y sombras: `--dark-shade-100`, `--dark-shade-50`, `--dark-shade-5` (textos, bordes y fondos suaves).
- **FR-005**: Encima de la tarjeta modal principal, la vista DEBE incorporar la barra de estado con la píldora informativa del motor/modelo (`GPT-5.2` con fondo verde secundario) a la izquierda y el icono de opciones/ajustes de FontAwesome a la derecha.
- **FR-006**: La tarjeta modal central "Ejecutar nuevo análisis" DEBE tener un contenedor blanco con esquinas redondeadas amplias (`rounded-2xl` / `rounded-3xl`), sombra suave y subtítulo descriptivo de formatos (`Formatos soportados: PDF, PNG, JPG, JPEG, JSON (Máx. 10 MB)`).
- **FR-007**: En estado inicial (sin archivo), la tarjeta DEBE mostrar la dropzone con borde punteado suave, icono de carpeta FontAwesome con halo difuso, texto `"Arrastre y suelte el archivo fuente para subirlo"`, enlace `"o, haga click para buscar (10 MB max)"` y botón `"Seleccionar archivos"`.
- **FR-008**: La interfaz DEBE preservar de forma completamente funcional y estéticamente integrada el dropdown de selección de `"Canal de Origen"` (`Guardia_Emergencias`, `Consulta_Externa`, `Admision`, `Laboratorio`).
- **FR-009**: Al subir o seleccionar un archivo, el modal DEBE transformar el área central en una fila horizontal redondeada con fondo suave (`bg-slate-100` / `var(--dark-shade-5)`), mostrando a la izquierda el icono `faPaperclip`, el nombre del archivo, y a la derecha su tamaño en MB junto al icono de acción.
- **FR-010**: La tarjeta con archivo cargado DEBE proveer en su parte inferior los botones: `"Cancelar"` (para descartar el archivo y reiniciar la carga) y `"Continuar"` (botón primario con color `--primary` para enviar y procesar el documento).
- **FR-011**: Al iniciar el procesamiento (`loading === true`), el sistema DEBE exhibir el loader circular animado de FontAwesome (`faSpinner` / `faCircleNotch` con animación) y el porcentaje de avance dentro de la fila del archivo, manteniendo deshabilitados los botones mientras la petición está en curso.
- **FR-012**: La refactorización DEBE emplear Tailwind CSS con diseño 100% responsivo para resoluciones móviles, tablets y escritorio, sin alterar la estructura del Sidebar existente.

---

### Key Entities

- **DocumentoTriajeEntrada**: Entidad que agrupa el archivo seleccionado (`File`), el identificador generado (`docId`), el canal hospitalario (`canalOrigen`) y el estado de la ingesta (vacío, cargado, procesando).
- **NavegacionPildorasRBAC**: Configuración de pestañas visibles y rutas asociadas según el rol del usuario autenticado (`ADMINISTRADOR`: 3 pestañas; otros roles: 2 pestañas).
- **EstadoCargaModal**: Estado de interfaz del modal que alterna entre `DROPZONE` (área punteada de arrastre/selección), `FILE_STAGED` (barra de archivo listo con botones Cancelar/Continuar) y `PROCESSING` (barra con loader y spinner activo).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La fidelidad visual de la vista `NewDocument` respecto a las 3 imágenes de referencia alcanza un 95% o superior en estructura, paleta de colores de `index.css`, tipografía, redondeo de bordes y estados de archivo.
- **SC-002**: Usuarios con rol `ADMINISTRADOR` pueden visualizar y navegar hacia las 3 rutas (`/triaje`, `/documentos`, `/auditoria`), mientras que el resto de roles únicamente visualiza las 2 permitidas (`/triaje`, `/documentos`) sin fugas de acceso visual.
- **SC-003**: El 100% de los iconos del modal y cabecera utilizan FontAwesome (`@fortawesome/react-fontawesome`), eliminando iconos inconsistentes.
- **SC-004**: Cero regresiones funcionales: El envío de análisis continúa operando con el 100% de éxito comunicándose con los endpoints de FastAPI y LangGraph, respetando el canal de origen seleccionado.
- **SC-005**: Compilación y pruebas frontend limpias: `npm run build` y `vitest run` aprueban con 0 errores de TypeScript y 100% de pruebas en verde.

---

## Assumptions

- El Sidebar lateral actual permanece intacto y no requiere modificaciones de diseño ni comportamiento.
- Las rutas `/documentos` e `/auditoria` ya existen en el enrutador de React (`AppRoutes.tsx`) y están listas para recibir la navegación desde las píldoras superiores.
- Las variables CSS de la paleta institucional (`--primary`, `--secondary`, `--dark-shade-100`, etc.) de `index.css` y las clases Tailwind configuradas se emplean como base estilística.
- Las dimensiones y límites de archivo se mantienen en un máximo de 10 MB para formatos PDF e imágenes (PNG, JPG, JPEG).
