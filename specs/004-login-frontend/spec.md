# Feature Specification: Frontend de Login - Pantalla de Inicio de Sesión

**Feature Branch**: `004-login-frontend`

**Created**: 2026-10-05

**Status**: Draft

**Input**: User description: "Crea el front de login revisa la carpeta de modulo login y toma en cuenta que solo sera front nada de tocar back y considera no quemar nada en el front respecto a datos reales o credenciales"

**Scope Clarification**: La carpeta `src-codigo-modulos/Modulo-Login` es **exclusivamente referencia visual** (prototipo). La implementación se realiza en los archivos reales del frontend bajo `frontend/src/` (ej. `src/pages/Login.tsx`, `src/styles/`, `src/assets/`). No se crea ni modifica ningún archivo dentro de `src-codigo-modulos/`.

**Constitution Reference**: v1.2.0 — Tailwind CSS obligatorio, responsividad obligatoria, TypeScript estricto, estilo clínico sobrio sin emojis.

## Clarifications

### Session 2026-10-05

- Q: ¿Debe mantenerse el panel de credenciales de desarrollo en la pantalla de login? → A: Eliminar completamente. No existe ningún panel, helper ni botón de autocompletar credenciales en ninguna modalidad (dev o prod).
- Q: En pantallas móviles (375px), ¿debe ocultarse la sección testimonial o apilarse? → A: Ocultar la sección testimonial en pantallas < 768px, mostrar solo el formulario.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Usuario visualiza la pantalla de login (Priority: P1)

Un usuario accede a la aplicación MediFlow sin estar autenticado y visualiza la pantalla de inicio de sesión. La pantalla presenta el branding de MediFlow, un formulario con campos de identificación (documento de identidad) y contraseña, y un botón de inicio de sesión. El diseño visual corresponde al prototipo de la carpeta `Modulo-Login` (estilo limpio, profesional, con orbes de fondo, sección testimonial y tipografías Quicksand/Montserrat).

**Why this priority**: Es la base del flujo de autenticación. Sin esta pantalla, ningún usuario puede acceder al sistema. Es el primer punto de contacto con la aplicación.

**Independent Test**: Can be fully tested by navigating to `/login` and verifying que la pantalla renderiza correctamente con todos los elementos visuales y campos del formulario, sin necesidad de un backend activo.

**Acceptance Scenarios**:

1. **Given** un usuario no autenticado, **When** navega a la ruta de login, **Then** visualiza la pantalla de inicio de sesión con el logo de MediFlow, el título "Bienvenido", los campos de documento y contraseña, y el botón "Iniciar sesión"
2. **Given** la pantalla de login renderizada, **When** se inspecciona el código fuente, **Then** no existe ninguna credencial real, contraseña, token ni dato sensible embebido o hardcodeado en el código
3. **Given** la pantalla de login renderizada, **When** se verifica la accesibilidad, **Then** todos los campos tienen etiquetas asociadas, atributos `autoComplete` correctos y son navegables por teclado

---

### User Story 2 - Usuario completa el formulario e intenta iniciar sesión (Priority: P1)

Un usuario completa los campos de documento de identidad y contraseña con sus credenciales y presiona el botón "Iniciar sesión". El formulario valida que los campos no estén vacíos antes de permitir el envío. El estado de envío se refleja visualmente (botón deshabilitado / indicador de carga).

**Why this priority**: Es la interacción principal del formulario. Sin validación y feedback visual, el usuario no sabe si su acción fue procesada.

**Independent Test**: Can be fully tested by llenar el formulario con datos de prueba (no reales) y verificar que las validaciones de campos vacíos y el estado de carga funcionan correctamente, usando mocks para la llamada de autenticación.

**Acceptance Scenarios**:

1. **Given** el formulario de login visible, **When** el usuario presiona "Iniciar sesión" sin completar los campos, **Then** el formulario no se envía y muestra validación de campos requeridos
2. **Given** el formulario con datos completados, **When** el usuario presiona "Iniciar sesión", **Then** el botón se deshabilita y muestra un indicador de carga mientras se procesa la solicitud
3. **Given** una solicitud de login en proceso, **When** ocurre un error de autenticación, **Then** se muestra un mensaje de error amigable y el formulario vuelve a su estado editable

---

### User Story 3 - Usuario navega a la opción de registro (Priority: P2)

Un usuario que no tiene cuenta ve el enlace "Regístrate" al pie del formulario. Al presionarlo, es redirigido a la pantalla de registro correspondiente.

**Why this priority**: Es un flujo secundario pero necesario para usuarios nuevos. No bloquea el login de usuarios existentes.

**Independent Test**: Can be fully tested by verificar que el enlace "Regístrate" está presente y que al accionarlo navega a la ruta de registro.

**Acceptance Scenarios**:

1. **Given** la pantalla de login visible, **When** el usuario presiona el enlace "Regístrate", **Then** es redirigido a la ruta de registro de usuarios

---

### User Story 4 - Sección testimonial y branding visual (Priority: P3)

La pantalla de login muestra una sección lateral con un testimonio de cliente y un fondo decorativo con orbes de color, siguiendo el prototipo de la carpeta `Modulo-Login`. Esta sección refuerza la identidad visual de MediFlow y transmite profesionalismo clínico.

**Why this priority**: Mejora la experiencia visual y percepción de marca, pero no afecta la funcionalidad core de autenticación.

**Independent Test**: Can be fully tested by verificar que la sección testimonial y los elementos decorativos renderizan correctamente en distintas resoluciones de pantalla.

**Acceptance Scenarios**:

1. **Given** la pantalla de login en un dispositivo de escritorio, **When** se renderiza la página, **Then** se muestra la sección testimonial con cita, autor y cargo, además del fondo decorativo con orbes
2. **Given** la pantalla de login en un dispositivo con pantalla reducida (< 768px), **When** se renderiza la página, **Then** la sección testimonial se oculta y solo se muestra el formulario, manteniendo legibilidad y funcionalidad

---

### Edge Cases

- ¿Qué sucede cuando el usuario introduce caracteres no numéricos en el campo de documento de identidad? El campo debe aceptar solo el formato esperado (DNI numérico) con validación de longitud.
- ¿Cómo maneja el sistema un token expirado o inválido al cargar la pantalla de login? Se debe mostrar la pantalla limpia sin errores residuales de sesiones anteriores.
- ¿Qué sucede si el backend no responde (timeout/conexión rechazada)? Se debe mostrar un mensaje de error genérico sin exponer detalles técnicos internos.
- ¿Qué sucede con los campos autocompletados por el navegador? Los valores deben ser tratados igual que los ingresados manualmente, sin credenciales pre-cargadas en el código.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La pantalla de login MUST renderizar un formulario con dos campos: documento de identidad (DNI) y contraseña, con sus respectivas etiquetas y atributos de accesibilidad.
- **FR-002**: La pantalla de login MUST mostrar el logo y nombre de MediFlow, así como el título "Bienvenido" y subtítulo de bienvenida, siguiendo el prototipo de `Modulo-Login`.
- **FR-003**: El formulario MUST validar que ambos campos no estén vacíos antes de permitir el envío.
- **FR-004**: El botón de inicio de sesión MUST mostrar un estado de carga (deshabilitado + indicador visual) mientras se procesa la solicitud.
- **FR-005**: El sistema MUST mostrar mensajes de error amigables cuando la autenticación falla, sin exponer detalles técnicos internos del backend.
- **FR-006**: La pantalla MUST incluir un enlace o botón "Regístrate" que navegue a la ruta de registro de usuarios.
- **FR-007**: La pantalla MUST incluir una sección testimonial lateral con cita, nombre y cargo, siguiendo el prototipo de `Modulo-Login`.
- **FR-008**: El código del frontend MUST NOT contener credenciales reales, contraseñas, tokens, documentos de identidad ni ningún dato sensible hardcodeado. No debe existir ningún panel, helper o botón de autocompletar credenciales, ni siquiera en modo desarrollo. Toda credencial se ingresa manualmente por el usuario.
- **FR-009**: El formulario MUST utilizar campos controlados de React (state) para los valores de documento y contraseña, sin valores por defecto pre-cargados que simulen credenciales reales.
- **FR-010**: La implementación MUST limitarse exclusivamente al frontend bajo `frontend/src/`. No se debe alterar, crear ni modificar ningún endpoint, modelo, migración o archivo del backend.
- **FR-011**: La carpeta `src-codigo-modulos/Modulo-Login` MUST NOT ser modificada. Sirve únicamente como referencia visual de diseño. Todo el código de implementación va en los archivos reales del frontend (`src/pages/Login.tsx`, estilos, assets, etc.).
- **FR-012**: La pantalla MUST respetar la constitución del proyecto: estilo sobrio, limpio, accesible y apto para entorno clínico, sin saturación de emojis en botones o encabezados.
- **FR-013**: Los estilos MUST implementarse con Tailwind CSS, según la constitución v1.2.0 y AGENTS.md. No se usa Vanilla CSS ni CSS nativo en hojas separadas para el maquetado. La configuración de Tailwind ya presente en `src-codigo-modulos/Modulo-Login/Codigo/tailwind.config.js` sirve como referencia para tokens y variables.
- **FR-014**: Tailwind CSS MUST estar instalado y configurado en el proyecto frontend (`tailwind.config.js`/`ts`, `postcss.config.js`, directivas `@tailwind` en el CSS de entrada). Si no está instalado previamente, su instalación y configuración forman parte de esta feature.
- **FR-015**: La pantalla MUST ser responsiva, adaptando el layout para escritorio (1920x1080), tablet (768px) y móvil (375px) sin perder funcionalidad ni legibilidad, usando utilidades responsivas de Tailwind CSS. La sección testimonial MUST ocultarse en pantallas menores a 768px (`hidden md:flex`) y mostrarse solo en escritorio y tablet.
- **FR-016**: El código MUST cumplir con TypeScript estricto: cero errores de compilación (`tsc --noEmit`), prohibido el uso de `any` para entidades de dominio.

### Key Entities *(include if feature involves data)*

- **Credenciales de Login**: Documento de identidad (DNI numérico) y contraseña. Datos ingresados por el usuario, nunca persistidos ni hardcodeados en el frontend. Se envían al backend vía la función de autenticación existente (`login` del hook `useAuth`).
- **Respuesta de Autenticación**: Token de acceso, tipo de token, datos del usuario (rol, estado, especialidad médica) y mensaje. Manejada por el `AuthContext` existente, no se modifica su contrato.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios pueden visualizar la pantalla de login completa (formulario, branding, sección testimonial) en menos de 2 segundos desde la navegación.
- **SC-002**: El 100% de los campos del formulario son accesibles por teclado y lectores de pantalla, con etiquetas y atributos ARIA correctos.
- **SC-003**: El código fuente de la pantalla de login contiene cero (0) credenciales, contraseñas, tokens o datos sensibles hardcodeados, verificable por inspección de código y análisis estático.
- **SC-004**: La pantalla de login se renderiza correctamente en resoluciones de escritorio (1920x1080), tablet (768px) y móvil (375px) sin pérdida de funcionalidad.
- **SC-005**: El 100% de las pruebas de componentes (vitest) pasan en verde, cubriendo renderizado, validación de campos, estados de carga y manejo de errores.
- **SC-006**: La compilación del frontend (`npm run build`) completa con 0 errores de TypeScript y 0 warnings.

## Assumptions

- Se reutilizará el hook `useAuth` y el `AuthContext` existentes para la llamada de autenticación, sin modificar su contrato ni su lógica interna.
- Se reutilizará el cliente HTTP existente (`src/api/httpClient.ts` y `src/api/auth.api.ts`) para la comunicación con el backend, sin alterarlos.
- El prototipo visual de `src-codigo-modulos/Modulo-Login/Codigo/index.lua` sirve **únicamente como referencia de diseño** (layout, tipografías, colores, orbes decorativos, sección testimonial). La implementación real se hace en `frontend/src/` adaptándose al stack del proyecto (React + TypeScript + Tailwind CSS según constitución v1.2.0). No se trabaja ni modifica nada dentro de `src-codigo-modulos/`.
- El campo de identificación principal es el documento de identidad (DNI), consistente con el backend actual que usa `documento_identidad`, no correo electrónico como sugiere el prototipo original de `Modulo-Login`.
- La ruta de registro de usuarios ya existe o será creada independientemente; esta feature solo incluye el enlace de navegación hacia ella.
- Las variables de entorno de desarrollo no se utilizan para credenciales. No existe ningún panel ni helper de autocompletar credenciales en ninguna modalidad (dev o prod).
- El enrutamiento existente (`react-router-dom`) se mantiene sin cambios estructurales; solo se actualiza el componente visual de la ruta `/login`.
- El proyecto actualmente usa Bootstrap para estilos. La pantalla de login se implementa íntegramente con Tailwind CSS, reemplazando las clases de Bootstrap del `Login.tsx` actual. La migración global de Bootstrap a Tailwind del resto de la aplicación queda fuera del alcance de esta feature.
- La configuración de Tailwind del prototipo (`src-codigo-modulos/Modulo-Login/Codigo/tailwind.config.js` y `tailwind.css`) sirve como referencia para tokens, variables CSS y fuentes (Quicksand, Montserrat).
