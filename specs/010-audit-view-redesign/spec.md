# Feature Specification: Rediseño Visual de la Vista de Auditoría Clínica (Human-in-the-Loop)

**Feature Branch**: `010-audit-view-redesign`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Refactoriza únicamente el diseño de la vista correspondiente a 'Auditoría clínica' que se encuentra en el archivo 'frontend\\src\\pages\\Audit.tsx'. El diseño se debe de ver similar a la imagen. Sin embargo, conserva las columnas y campos que se deben de mostrar en la tabla ya que deberán de ser exactamente los mismos que se encuentran en la tabla actual. En cambio, para la columna con los botrones 'Revisar', utiliza los íconos de FontAwesome y respeta que sea un ojo el que se muestre, cada botón que sea outline pero que al hacer hover su color cambie a azul (var(--primary)) y el contenido en blanco. Omite el filtro que viene mencionado en la tabla de referencia de la imagen (dropdown). Para el color de los badges de confianza establece que si es menor al 25% de confianza entonces que sea de color rojo (var(--error)), si es entre 25% y 50% en anaranjado (var(--orange)), de 50% a 75% en amarillo (warning) y para un nivel de confianza superior al 75% entonces color verde (var(--green))"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Presentación Visual de la Bandeja de Auditoría Clínica y Encabezado Central (Priority: P1)

Como coordinador médico o administrador hospitalario, al ingresar a la pantalla de Auditoría Clínica (`frontend/src/pages/Audit.tsx`), deseo ver una interfaz médica moderna, sobria y centrada que refleje fielmente el diseño de la imagen de referencia, con la barra de píldoras de navegación superior (`Enrutamiento`, `Historial`, `Solicitudes`), el título prominente centrado "Solicitudes de auditoría clínica", y una tarjeta contenedora blanca de esquinas redondeadas amplias y bordes limpios, omitiendo el selector dropdown de filtros.

**Why this priority**: Es la estructura visual base de la pantalla de intervención manual que homogeniza la experiencia de usuario con el resto de la plataforma clínica MediFlow y replica la estética acordada en las referencias visuales.

**Independent Test**:
- Cargar la ruta `/auditoria` en el navegador o ejecutar la suite de pruebas de renderizado.
- Comprobar que se muestra la cabecera con el título principal centrado "Solicitudes de auditoría clínica".
- Comprobar que se muestra la tarjeta contenedora blanca con esquinas redondeadas y sombra suave.
- Verificar empíricamente que **NO** existe ningún dropdown de filtros en la esquina superior derecha de la tabla.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado navegando a `/auditoria`, **When** se renderiza la vista, **Then** visualiza en la parte superior el título principal destacado "Solicitudes de auditoría clínica", la barra de navegación de píldoras coherente con el sistema, y la tarjeta blanca central con esquinas redondeadas.
2. **Given** la vista de auditoría basada en la imagen de referencia, **When** el usuario inspecciona el encabezado de la tarjeta de la tabla, **Then** constata que el dropdown de filtro ("Urgencias Médicas") ha sido omitido completamente, manteniendo una cabecera despejada y enfocada en los datos.

---

### User Story 2 - Conservación Integral de Columnas y Campos Clínicos en la Tabla Rediseñada (Priority: P1)

Como profesional clínico responsable de la revisión manual, deseo que la tabla conserve exactamente las mismas columnas y campos que existen actualmente en `Audit.tsx` (`ID`, `Documento`, `Confianza`, `Motivo de Derivación`, `Fecha`, y acción/visualización), garantizando que no se pierda ningún dato clínico necesario para la toma de decisiones.

**Why this priority**: La integridad de la información clínica y la compatibilidad con el modelo de datos de documentos (`ClinicalDocument`) y la API de auditoría no pueden verse comprometidas por cambios cosméticos.

**Independent Test**:
- Inspeccionar las filas de la tabla con datos simulados o reales.
- Verificar que cada fila exhibe: identificador único (`documento_id`), nombre del archivo (`nombre_archivo`), badge de confianza, motivo de derivación con icono explicativo, fecha de creación formateada y la columna de acción.

**Acceptance Scenarios**:

1. **Given** una lista de documentos devuelta por `auditApi.obtenerAuditorias()`, **When** se puebla la tabla en pantalla, **Then** las columnas visibles corresponden estrictamente a: `ID`, `Documento`, `Confianza`, `Motivo de Derivación`, `Fecha`, y la columna de acción/visualización.
2. **Given** un documento con motivo de derivación específico (o el valor por defecto "Confianza baja o datos incompletos detectados"), **When** el usuario lee la fila, **Then** el texto del motivo y su fecha de creación permanecen legibles y completos.

---

### User Story 3 - Badges de Confianza con Regla Cuádruple de Colores Institucionales (Priority: P2)

Como auditor médico, deseo identificar a golpe de vista la severidad o incertidumbre del diagnóstico a través de un badge de confianza cuyos colores respondan a la escala clínica especificada:
- Menor al 25%: Rojo (`var(--error)` / `#F72C2C`).
- Entre 25% y 50%: Anaranjado (`var(--orange)` / `#F59E0B`).
- Entre 50% y 75%: Amarillo (`var(--warning)` / `#EAB308` / clase warning).
- Superior al 75%: Verde (`var(--green)` / `#10B981`).

**Why this priority**: La categorización visual por colores según umbrales de confianza permite al profesional priorizar de inmediato los casos más críticos o ambiguos durante el triaje.

**Independent Test**:
- Probar documentos con scores de confianza de 15%, 35%, 65% y 90%.
- Comprobar que las clases CSS y variables aplicadas a los badges coinciden respectivamente con rojo (`--error`), anaranjado (`--orange`), amarillo (`warning`) y verde (`--green`).

**Acceptance Scenarios**:

1. **Given** un documento con score de confianza < 25% (ej. 15%), **When** se muestra en la tabla, **Then** el badge se colorea en rojo utilizando `var(--error)`.
2. **Given** un documento con score de confianza entre 25% y 50% (ej. 35%), **When** se muestra en la tabla, **Then** el badge se colorea en anaranjado utilizando `var(--orange)`.
3. **Given** un documento con score de confianza entre 50% y 75% (ej. 60%), **When** se muestra en la tabla, **Then** el badge se colorea en amarillo (`warning`).
4. **Given** un documento con score de confianza > 75% (ej. 85%), **When** se muestra en la tabla, **Then** el badge se colorea en verde utilizando `var(--green)`.

---

### User Story 4 - Botón de Revisión Outline con Icono de Ojo FontAwesome y Efecto Hover Azul (Priority: P2)

Como usuario clínico que va a revisar un documento pendiente, deseo que la columna de acción cuente con botones estilo *outline* que muestren el icono de un ojo de FontAwesome (`faEye` / `FaEye`) y la etiqueta descriptiva, de modo que al situar el cursor encima (*hover*), su fondo cambie dinámicamente a azul (`var(--primary)` / `#2C5282`) y el contenido (icono y texto) se vuelva blanco puro (`#ffffff`), redirigiendo a `/auditoria/${documento_id}` al hacer clic.

**Why this priority**: Cumple con el requerimiento de interacción visual del usuario y asegura accesibilidad, claridad en el llamado a la acción y transición fluida.

**Independent Test**:
- Inspeccionar el botón de cada fila: verificar presencia del icono de ojo FontAwesome.
- Aplicar estado hover mediante CSS/interacción y verificar que el fondo pasa a `var(--primary)` y el texto/icono a blanco.
- Hacer clic en el botón y constatar que navega a `/auditoria/${item.documento_id}`.

**Acceptance Scenarios**:

1. **Given** una fila de auditoría, **When** el botón está en estado de reposo, **Then** tiene estilo outline con borde sutil, fondo transparente o claro, y contenido en color acorde al tema.
2. **Given** el botón de acción, **When** el usuario realiza hover con el cursor sobre él, **Then** el fondo cambia a `var(--primary)` (`#2C5282`) y el contenido (icono de ojo y texto) se torna completamente blanco (`#ffffff`).
3. **Given** un clic sobre el botón, **When** se procesa la navegación, **Then** se abre la pantalla de detalle de auditoría del documento correspondiente (`/auditoria/${documento_id}`).

---

### User Story 5 - Controles de Paginación Visual y Estados de Carga/Vacío Responsivos (Priority: P3)

Como usuario que interactúa con la lista de auditoría, deseo visualizar en el pie de la tabla un control de paginación estilizado semejante a la imagen de referencia (ej. indicadores de página `01`, `02`, etc.), y contar con retroalimentación clara en estados de carga (`Loading`), error (`ErrorMessage`) o ausencia de datos (`EmptyState`), adaptándose de forma 100% responsiva a cualquier tamaño de pantalla.

**Why this priority**: Completa la coherencia estética con la imagen maqueta y garantiza robustez ante diferentes volúmenes de documentos y dispositivos.

**Independent Test**:
- Redimensionar la ventana a resoluciones de escritorio, tableta y móvil: la tabla debe contar con scroll horizontal o apilamiento limpio sin romper el layout.
- Verificar la presencia del bloque de paginación en el pie de la tarjeta.

**Acceptance Scenarios**:

1. **Given** la tabla renderizada, **When** el usuario llega al final de la tarjeta, **Then** visualiza los controles de paginación alineados al centro/derecha con numeración compacta estilo badge/pill.
2. **Given** una petición en curso o un listado sin elementos pendientes, **When** no hay registros para mostrar, **Then** se presenta el componente `EmptyState` preservando la estructura limpia de la página.

---

### Edge Cases

- **Valores nulos, indefinidos o fuera de escala en la confianza**: Si un documento no posee `score_confianza` o es nulo, el sistema debe asignarle por defecto la escala más cautelosa (< 25%, color rojo `var(--error)`).
- **Documento con nombre o motivo de derivación muy extenso**: Las celdas de texto deben aplicar truncamiento suave o salto de línea controlado para evitar desbordar el ancho de las columnas.
- **Visualización en dispositivos móviles reducidos**: La tabla debe estar envuelta en un contenedor con desbordamiento horizontal suave (`overflow-x-auto`) para no alterar el ancho del viewport general.
- **Acceso con error de red en la API de auditoría**: El componente debe conservar el estado de error con el botón de reintento (`onRetry`).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La vista `frontend/src/pages/Audit.tsx` DEBE refactorizar su maquetado empleando **Tailwind CSS**, adoptando una estructura de diseño similar a la imagen de referencia: fondo limpio, cabecera centrada con el título principal exacto **"Solicitudes de auditoría clínica"**, y tarjeta central blanca con esquinas redondeadas (`rounded-2xl` / `rounded-3xl`) y sombra suave.
- **FR-002**: La interfaz DEBE incorporar la barra superior de píldoras de navegación (`Enrutamiento`, `Historial`, `Solicitudes`), marcando como activa la opción correspondiente a las auditorías y permitiendo la navegación a `/triaje`, `/documentos` y `/auditoria`.
- **FR-003**: La tabla de datos DEBE conservar exactamente las columnas y campos actuales de `Audit.tsx`:
  - `ID`: `item.documento_id`
  - `Documento`: `item.nombre_archivo`
  - `Confianza`: Porcentaje de confianza con badge clasificado por color
  - `Motivo de Derivación`: `item.decision_enrutamiento?.motivo_auditoria` con icono de alerta/detalle
  - `Fecha`: `item.fecha_creacion` formateada mediante `formatDateShort`
  - `Acción`: Botón de revisión individual
- **FR-004**: Los botones de la columna de acción DEBEN utilizar la librería **FontAwesome** mostrando expresamente el icono de un ojo (`faEye` / `FaEye`).
- **FR-005**: El botón de revisión DEBE poseer estilo *outline* en reposo y cambiar en *hover* a fondo azul (`var(--primary)` / `#2C5282`) con icono y texto en color blanco (`#ffffff`).
- **FR-006**: La cabecera de la tabla DEBE omitir expresamente el menú dropdown de filtros visible en la imagen de referencia.
- **FR-007**: La asignación de colores en los badges de confianza DEBE estructurarse en 4 rangos definidos:
  - Confianza < 25%: Rojo (`var(--error)` / `#F72C2C`).
  - Confianza entre 25% y 50%: Anaranjado (`var(--orange)` / `#F59E0B`).
  - Confianza entre 50% y 75%: Amarillo (`var(--warning)` / warning / `#EAB308`).
  - Confianza > 75%: Verde (`var(--green)` / `#10B981`).
- **FR-008**: La tarjeta DEBE incluir en su pie un bloque de paginación estilizado con diseño numerado (ej. `01`, `02`, `03`...) coherente con la referencia visual.
- **FR-009**: La vista DEBE mantener la gestión de estados de carga (`Loading`), fallo con reintento (`ErrorMessage`) y lista vacía (`EmptyState`).
- **FR-010**: El diseño DEBE ser 100% responsivo para resoluciones móviles, tablets y monitores de escritorio.

### Key Entities

- **ClinicalDocument (Auditoría)**: Documento clínico en cola de revisión que incluye identificador único (`documento_id`), nombre original del archivo (`nombre_archivo`), fecha de creación (`fecha_creacion`), clasificación diagnóstica con score numérico de confianza (`clasificacion.score_confianza`), y decisión de enrutamiento con motivo de retención humana (`decision_enrutamiento.motivo_auditoria`).
- **ConfidenceRange**: Objeto de presentación visual que define el porcentaje formateado, la etiqueta descriptiva y la clase/color correspondiente según los 4 rangos establecidos (<25%, 25-50%, 50-75%, >75%).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las columnas y campos de datos preexistentes en `Audit.tsx` se preservan y renderizan sin pérdida de información clínica.
- **SC-002**: Los badges de confianza aplican con 100% de precisión cromática los 4 intervalos de color solicitados (<25% rojo, 25-50% naranja, 50-75% amarillo, >75% verde).
- **SC-003**: El botón de acción muestra el icono de ojo de FontAwesome y responde a la interacción *hover* con transición suave a fondo azul `var(--primary)` y texto blanco.
- **SC-004**: La compilación del frontend (`npm run build`) se ejecuta limpia con 0 errores de TypeScript y las pruebas unitarias (`vitest run`) pasan en verde al 100%.
- **SC-005**: La interfaz se visualiza correctamente en pantallas desde 375px hasta 1920px sin desbordamiento no controlado de elementos.

---

## Assumptions

- Se reutilizan las variables CSS declaradas en `frontend/src/index.css` (`--primary`, `--error`, `--orange`, `--green`, `--dark-shade-100`, etc.) combinadas con utilidades de Tailwind CSS.
- La navegación por píldoras superiores utiliza el hook `useAuth` y las definiciones `NAV_PILLS` de `triageModal.types.ts` para mantener la consistencia RBAC con la vista `NewDocument.tsx`.
- Para los iconos de FontAwesome se utiliza `@fortawesome/react-fontawesome` (o `react-icons/fa` con equivalentes estándar) asegurando uniformidad con los componentes del frontend.
- La paginación en esta iteración de diseño visual implementa la presentación estética acorde a la imagen de referencia, manteniendo la navegación entre páginas o registros.

