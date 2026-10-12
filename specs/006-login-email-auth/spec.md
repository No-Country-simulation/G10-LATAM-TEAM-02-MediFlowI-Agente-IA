# Feature Specification: Autenticación por Correo y Gestión Global de Sesión Hospitalaria

**Feature Branch**: `006-login-email-auth`  
**Created**: 2026-10-12  
**Status**: Draft  
**Input**: User description: "Revisa y modifica (en caso de ser necesario) los archivos que corresponden al flujo de Login, de tal manera que se respete que al usuario solamente se le solicitará correo y contraseña para poder iniciar sesión. Igualmente verifica que al iniciar sesión se estén obteniendo y almacenando de manera global y segura los datos del usuario necesarios para navegar por la aplicación (id, documento_identidad, nombres, apellidos, correo, especialidad, rol, estado). Revisa el modelo de datos por si hay algún detalle que deba de considerarse que no se haya listado, como tokens o semejante."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inicio de Sesión Exclusivo por Correo Electrónico (Priority: P1)

Como profesional o personal hospitalario de MediFlow (Administrador, Coordinador u Operador), deseo iniciar sesión en el sistema ingresando únicamente mi correo electrónico registrado y mi contraseña, para acceder de manera ágil y segura a mis funciones operativas sin tener que memorizar o ingresar mi documento de identidad en la pantalla de bienvenida.

**Why this priority**: Es la puerta de entrada indispensable a todo el sistema. Si el inicio de sesión no utiliza el identificador principal esperado (correo electrónico) con validación estricta, los usuarios no pueden acceder al flujo de triaje, auditoría ni gestión de pacientes.

**Independent Test**: Puede probarse de forma independiente en la ruta `/login` ingresando un correo electrónico válido registrado y su contraseña correspondiente, verificando que se autentica y redirige al panel de control (`/dashboard`).

**Acceptance Scenarios**:

1. **Given** un usuario no autenticado en la pantalla `/login`, **When** visualiza el formulario, **Then** se le solicita únicamente su correo electrónico (`label="CORREO"`, `placeholder="email@example.com"`) y su contraseña (`label="CONTRASEÑA"`), sin requerir el documento de identidad en la interfaz.
2. **Given** un usuario que introduce una dirección de correo válida y su contraseña correcta, **When** presiona "Iniciar sesión", **Then** el sistema autentica al usuario y lo redirige a la ruta solicitada o al `/dashboard`.
3. **Given** un usuario que introduce un formato de correo inválido (ej. una cadena sin `@` o sin dominio), **When** interactúa con el formulario o intenta enviarlo, **Then** el campo de correo muestra el mensaje de error "Por favor, introduzca una dirección de correo electrónico válida" y el formulario bloquea el envío.
4. **Given** que alguno de los dos campos (correo o contraseña) está vacío, **When** el usuario se encuentra en el formulario, **Then** el botón "Iniciar sesión" permanece deshabilitado.

---

### User Story 2 - Obtención y Persistencia Global Segura del Perfil de Usuario (Priority: P1)

Como usuario autenticado que navega por los diferentes módulos de la aplicación (triaje, bandeja de auditoría, gestión de pacientes, administración de usuarios), requiero que el sistema obtenga y almacene de manera global en el contexto de la aplicación todos mis datos de perfil operativo (`id`, `documento_identidad`, `nombres`, `apellidos`, `correo`, `especialidad_medica`, `rol`, `estado`) y mi token de sesión, para que las vistas apliquen el control de acceso adecuado por rol y muestren mi identidad clínica de forma consistente.

**Why this priority**: Sin la disponibilidad global de los metadatos del usuario (especialmente `rol`, `especialidad_medica` y `estado`), las rutas protegidas no pueden evaluar permisos críticos (como restringir `/auditoria` a `COORDINADOR` y `ADMINISTRADOR`) ni atribuir firmas en trazabilidad clínica.

**Independent Test**: Puede probarse validando que tras un inicio de sesión exitoso, el contexto global de autenticación (`useAuth()`) expone el objeto completo `user` con todos los atributos requeridos (`id`, `documento_identidad`, `nombres`, `apellidos`, `correo`, `especialidad_medica`, `rol`, `estado`, `token`), y que la sesión se rehidrata íntegra al recargar el navegador.

**Acceptance Scenarios**:

1. **Given** una autenticación exitosa, **When** el servidor responde a la solicitud de login, **Then** la respuesta contiene el token de acceso (`access_token`) y el objeto de usuario con: `id`, `documento_identidad`, `nombres`, `apellidos`, `correo`, `especialidad_medica`, `rol` y `estado`.
2. **Given** la recepción de las credenciales de sesión en el cliente, **When** se actualiza el estado de la aplicación, **Then** el contexto global (`AuthContext`) almacena en memoria el usuario completo con su token para disponibilidad inmediata en toda la navegación.
3. **Given** el almacenamiento del token de acceso, **When** se guarda en el almacenamiento del navegador (`localStorage`), **Then** se almacena exclusivamente el identificador del token de sesión para rehidratación segura, sin exponer contraseñas, hashes ni sales criptográficas en texto plano.
4. **Given** un usuario que recarga la página en una ruta protegida, **When** la aplicación inicializa, **Then** utiliza el token de acceso para consultar el perfil activo (`/auth/me`), validando en PostgreSQL que la sesión no haya sido revocada ni haya expirado, y rehidrata los datos completos del usuario (`especialidad_medica`, `rol`, `estado`, etc.).

---

### User Story 3 - Cierre e Invalidación Revocable de Sesión en Base de Datos (Priority: P2)

Como usuario del sistema hospitalario que finaliza su turno de trabajo, deseo cerrar mi sesión en la aplicación para que mi token de acceso sea revocado de inmediato tanto en el cliente como en el servidor, impidiendo que otra persona pueda operar la terminal clínica con mis permisos.

**Why this priority**: Cumple con las normativas de seguridad de la información clínica hospitalaria, asegurando que un token revocado no pueda seguir siendo utilizado por peticiones posteriores.

**Independent Test**: Puede probarse ejecutando la acción de cerrar sesión (`logout`), verificando que se limpia el estado en memoria, se remueve el token de `localStorage`, se registra `revoked_at` en `sesiones_usuario` en PostgreSQL, y cualquier petición posterior con ese token es rechazada con HTTP 401.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado, **When** ejecuta la acción de cerrar sesión (`logout`), **Then** se invoca el endpoint de invalidación, se marca la sesión como revocada en la base de datos (`revoked_at = NOW()`), se limpia el estado global y se redirige a `/login`.
2. **Given** un token que ha sido revocado en el servidor, **When** se intenta consultar cualquier recurso o el endpoint `/auth/me`, **Then** el servidor retorna HTTP 401 Unauthorized y la interfaz expulsa al usuario hacia la pantalla de inicio de sesión.

---

### Edge Cases

- ¿Qué sucede si el usuario ingresa su correo con espacios accidentales al inicio o al final? El sistema debe aplicar un recorte automático (`trim()`) antes de validar el formato y antes de enviar la petición de autenticación.
- ¿Qué sucede si el usuario intenta autenticarse con una cuenta cuyo estado es `INACTIVO`? El sistema debe rechazar el acceso con HTTP 403 Forbidden y mostrar el mensaje claro de que la cuenta se encuentra inactiva o pendiente de confirmación por el administrador.
- ¿Qué sucede si la base de datos PostgreSQL no se encuentra disponible durante el intento de inicio de sesión o validación de token? El sistema backend debe retornar un error explícito HTTP 503 sin inventar sesiones ni saltarse la verificación de seguridad.
- ¿Qué sucede si el usuario tiene caracteres en mayúsculas en su correo? La búsqueda en base de datos debe ser insensible a mayúsculas/minúsculas (`LOWER(correo)`) para evitar rechazos por capitalización accidental en dispositivos móviles.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La interfaz de inicio de sesión en el frontend MUST solicitar única y exclusivamente el **correo electrónico** (`correo`) y la **contraseña** (`password`) del usuario.
- **FR-002**: El componente de entrada de datos (`Input`) MUST actualizar su valor en tiempo real con el texto tecleado por el usuario, sin propagar ni renderizar el nombre técnico del campo.
- **FR-003**: El formulario de login MUST validar en tiempo real y al envío el formato de correo electrónico mediante expresión regular (`/^[^\s@]+@[^\s@]+\.[^\s@]+$/`), desplegando el mensaje de error: `"Por favor, introduzca una dirección de correo electrónico válida"` ante formatos incorrectos.
- **FR-004**: El botón de acción "Iniciar sesión" MUST permanecer en estado deshabilitado (`disabled`) mientras alguno de los campos obligatorios (correo o contraseña) no contenga texto.
- **FR-005**: El backend MUST permitir la autenticación de usuarios por **correo electrónico**, validando criptográficamente la contraseña provista contra el hash y sal almacenados en la tabla `usuarios` de PostgreSQL.
- **FR-006**: La respuesta exitosa de inicio de sesión MUST retornar de manera obligatoria la estructura completa de datos del usuario, conteniendo:
  - `id`: Identificador universal único (UUID)
  - `documento_identidad`: Número de identificación del trabajador
  - `nombres`: Nombres del usuario
  - `apellidos`: Apellidos del usuario
  - `correo`: Dirección de correo electrónico
  - `especialidad_medica`: Especialidad clínica asignada (o `null` para roles administrativos puros)
  - `rol`: Rol clínico del usuario (`ADMINISTRADOR`, `COORDINADOR`, `OPERADOR`)
  - `estado`: Estado operativo (`ACTIVO`, `INACTIVO`)
  - `access_token`: Token de sesión Bearer persistido en PostgreSQL
- **FR-007**: El proveedor de autenticación en el frontend (`AuthContext`) MUST almacenar de manera global en el estado de React el objeto `SessionUser` con todos los atributos enumerados en **FR-006** más el token activo, exponiéndolos mediante el hook `useAuth()`.
- **FR-008**: La persistencia local en el navegador (`localStorage`) MUST almacenar únicamente el token de acceso bajo la clave `"mediflow_auth_session"`, prohibiendo terminantemente almacenar contraseñas, hashes o credenciales en texto claro.
- **FR-009**: Al iniciar o recargar la aplicación en el navegador, el sistema MUST rehidratar el contexto global consultando el endpoint `/auth/me`, el cual consultará en PostgreSQL (`sesiones_usuario` JOIN `usuarios`) y devolverá el perfil completo con todos los campos especificados en **FR-006**.
- **FR-010**: El endpoint de cierre de sesión (`/auth/logout`) MUST registrar la marca temporal `revoked_at` en la tabla `sesiones_usuario` para invalidar inmediatamente el token a nivel de servidor.

---

### Key Entities *(include if feature involves data)*

#### 1. Entidad de Credenciales de Entrada (`LoginCredentials`)
- **`correo`** (String): Dirección de correo electrónico registrada del usuario. Formato estándar `usuario@dominio.ext`.
- **`password`** (String): Contraseña en texto plano provista en el formulario de acceso para su validación contra el hash en base de datos.

#### 2. Entidad de Usuario del Sistema (`User` / `usuarios`)
- **`id`** (UUID): Identificador único universal en PostgreSQL.
- **`documento_identidad`** (String): Documento nacional de identidad (8 cifras).
- **`nombres`** (String): Nombres de pila del usuario.
- **`apellidos`** (String): Apellidos del usuario.
- **`correo`** (String): Correo electrónico institucional / personal único.
- **`telefono`** (String, opcional): Teléfono de contacto.
- **`rol`** (Enum): Rol operativo hospitalario (`ADMINISTRADOR`, `COORDINADOR`, `OPERADOR`).
- **`especialidad_medica`** (String, opcional): Especialidad clínica (`Medicina General`, `Cardiología`, etc.).
- **`estado`** (Enum): Estado de habilitación (`ACTIVO`, `INACTIVO`).

#### 3. Entidad de Sesión y Token (`sesiones_usuario` / `SessionUser`)
- **`token_hash`** (String SHA-256): Hash irreversible del token de sesión almacenado en la tabla `sesiones_usuario`.
- **`access_token`** (String Bearer): Token aleatorio seguro de 64 caracteres hex emitido al cliente con prefijo `mf_session_`.
- **`expires_at`** (Timestamp with timezone): Momento exacto de expiración (por defecto 12 horas tras emisión).
- **`revoked_at`** (Timestamp with timezone, nullable): Momento en que la sesión fue explícitamente cerrada o revocada.
- **`SessionUser`**: Agregación en memoria cliente de `User` + `token: string`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los intentos de inicio de sesión exitosos completan la autenticación y reorientan al usuario en menos de 1.5 segundos en condiciones de red local/desarrollo.
- **SC-002**: El formulario de login solicita exactamente dos (2) campos de entrada interactivos: correo electrónico y contraseña.
- **SC-003**: El 100% de los campos del objeto de usuario (`id`, `documento_identidad`, `nombres`, `apellidos`, `correo`, `especialidad_medica`, `rol`, `estado`) se encuentran presentes y accesibles a través de `useAuth().user` en todos los módulos de la aplicación.
- **SC-004**: Al recargar la aplicación en el navegador con sesión activa, el 100% de los datos del perfil se rehidratan satisfactoriamente a través de `/auth/me` sin pérdida de la especialidad médica ni del rol.
- **SC-005**: El 100% de las pruebas unitarias y de integración del frontend (`vitest run`) pasan en verde.
- **SC-006**: La compilación estricta de TypeScript (`npm run build`) se ejecuta con cero (0) errores.

---

## Assumptions

- La tabla `usuarios` en PostgreSQL ya cuenta con la columna `especialidad_medica VARCHAR(100)` incorporada desde la migración unificada `o8p808522kl4_implement_unified_db_proposal.py`.
- La tabla `sesiones_usuario` ya almacena de forma irreversible el digest SHA-256 del token para evitar exposición de credenciales en base de datos.
- Las cuentas creadas a través de auto-registro (`/signup`) inician por defecto con estado `INACTIVO` requiriendo activación administrativa, mientras que las cuentas sembradas de desarrollo ya cuentan con estado `ACTIVO`.
- El frontend gestiona la navegación protegida mediante `ProtectedRoute.tsx`, el cual evalúa `isAuthenticated` y el rol del usuario para autorizar el acceso a rutas clínicas como `/auditoria`.

