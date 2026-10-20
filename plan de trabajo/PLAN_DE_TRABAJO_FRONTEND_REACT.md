# 📋 Plan de Trabajo Operativo: Frontend, React & UI Clínica (MediFlow)

Este plan de trabajo establece el **inventario técnico 100% verídico y auditable** del código implementado en el Frontend (React 19, TypeScript, Tailwind CSS, Vite) en la rama `develop`. Desglosa cada módulo de forma atómica e independiente, detallando con exactitud:
1. **Tareas formales respaldadas por Specs en `specs/`** (Specs 004, 005, 006, 009, 010, 012 y 013).
2. **Tareas de módulos clínicos y administrativos implementados en `develop`** (Bienvenida, Nuevo Enrutamiento, Detalle con Medicamentos, Consola, Historial, Pacientes, Auditoría y Configuración).
3. **Tareas de visualización avanzada y alertas en tiempo real** (Soporte WebP y Visor interactivo PDF concluidos en PR #78; Alertas SSE pendiente).
4. **Lo que YA está implementado vs. lo que está INCONCLUSO** para que el equipo de frontend retome inmediatamente el desarrollo sin duplicar código.

---

## 🚀 0. Guía de Ejecución, Testing y Validación Local

Antes de iniciar cualquier desarrollo, todo miembro del equipo debe verificar su entorno local contra la API de FastAPI:

### Paso 1: Variables de Entorno (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Paso 2: Servidor de Desarrollo con Hot-Reload (Vite)
```powershell
cd frontend
npm run dev
```
Acceso web: 👉 **[http://localhost:5173](http://localhost:5173)**

### Paso 3: Validación Estricta de TypeScript y Compilación
Conforme a la **Regla de Oro**, ningún cambio es válido si genera errores de compilación:
```powershell
cd frontend
npm run build
```

### Paso 4: Ejecución de la Suite de Pruebas Unitarias (Vitest)
```powershell
cd frontend
npm test
```
*(Para modo observador continuo durante el desarrollo: `npx vitest`).*

---

## 👥 Asignación del Equipo Frontend

| Especialidad | Responsables | Módulos a Cargo |
|---|---|---|
| **Autenticación & Acceso Clínico** | Desarrollador 1 & Desarrollador 2 | Login (Spec 004/006), Registro (Spec 005), Bienvenida/Onboarding, Sidebar RBAC y Solicitudes de Acceso |
| **Ingesta, Triaje & Visores Clínicos** | Desarrollador 3 & Desarrollador 4 | Nuevo Enrutamiento, Detalle de Documento, Consola de Triaje, Visor WebP y Visor Interactivo PDF |
| **Trazabilidad & Administración Hospitalaria** | Desarrollador 5 & Desarrollador 6 | Historial de Documentos, Auditoría Médica (HITL), Pacientes, Configuración Storage y Alertas SSE |

---

## 🗺️ Matriz de Control: Estado Real en la Rama `develop` (100% Cobertura)

| # | Tarea / Módulo | Issue | Archivos Reales en `develop` | Spec / Origen | Estado Real | % Avance | Faltante Concreto para Concluir |
|---|---|---|---|---|:---:|:---:|---|
| **1.1** | Módulo Login | `FE-01` | `Login.tsx`, `LoginForm.tsx`, `login.css` | `specs/004-login-frontend` | ✅ Concluido | 100% | Ninguno funcional (tests en verde). |
| **1.2** | Módulo Registro (Sign Up) | `FE-02` | `SignUp.tsx`, `SignUpForm.tsx` | `specs/005-sign-up-flow` | ✅ Concluido | 100% | Ninguno funcional (tests en verde). |
| **1.3** | Login por Correo & AuthContext | `FE-03` | `LoginForm.tsx`, `AuthContext.tsx` | `specs/006-login-email-auth` | ✅ Concluido | 100% | Ninguno funcional (tests en verde). |
| **2.1** | Bienvenida & Onboarding | `FE-04` | `Dashboard.tsx` (L49-86), `Sidebar.tsx` | Código `develop` (Figma) | 🟡 En Progreso | 90% | Tests unitarios y enlazar a `/api/v1/metrics`. |
| **2.2** | Nuevo Enrutamiento (Carga) | `FE-05` | `NewDocument.tsx`, `DocumentUploader.tsx`, `NewDocument.test.tsx` | `specs/009-triage-modal-redesign` / PR #78 | 🟢 En Progreso | 98% | Soporte WebP incorporado; botón de reintento ante error. |
| **2.3** | Detalle Clínico del Documento | `FE-06` | `DocumentDetail.tsx`, `ExtractedData.tsx`, `documentsApi.ts` | Código `develop` / IA-07 | 🟢 En Progreso | 98% | Medicamentos prescritos y vías integradas. Tests unitarios pendientes. |
| **2.4** | Consola de Triaje Clínico | `FE-07` | `TriageConsoleView.tsx` (28.5 KB) | Código `develop` / IA-07 | 🟢 En Progreso | 98% | Prescripciones integradas en consola. Tests interactivos pendientes. |
| **2.5** | Visualización Medicamentos & Visor | `IA-07` / `FE-06` | `types/documents.ts`, `documentsApi.ts`, `ExtractedData.tsx`, `TriageConsoleView.tsx`, `AuditDetail.tsx`, `DocumentViewer.tsx`, `ExtractedData.test.tsx` | IA-07 / Requisito R3 / Spec 014 | ✅ Concluido | 100% | Farmacoterapia estructurada con vías, badges, visor accesible y 100% tests en verde. |
| **3.1** | Historial de Enrutamiento | `FE-08` | `Documents.tsx`, `DocumentTable.tsx` | Código `develop` (Figma) | 🟡 En Progreso | 85% | Paginación remota de servidor y tests. |
| **3.2** | Auditoría Médica (HITL) | `FE-09` | `Audit.tsx`, `AuditDetail.tsx`, `Audit.test.tsx` | `specs/010-audit-view-redesign` | 🟢 En Progreso | 95% | Medicamentos integrados en resolución; observaciones del auditor pendientes. |
| **4.1** | Solicitudes de Acceso | `FE-10` | `UsersManagementView.tsx` (29.2 KB) | Código `develop` (Figma) | 🟡 En Progreso | 85% | Pestaña aislada para solicitudes y tests. |
| **4.2** | Gestión de Pacientes | `FE-11` | `PatientsManagementView.tsx` (44 KB) | RF-06 al RF-09 (`develop`) | 🟢 En Progreso | 95% | Tests unitarios del módulo de pacientes. |
| **4.3** | Configuración de Almacenamiento | `FE-12` | `StorageSettingsView.tsx` (12.6 KB) | Código `develop` (Figma) | 🟢 En Progreso | 95% | Tests unitarios de alternancia LOCAL/OCI. |
| **5.1** | Soporte para Imágenes WebP | `FE-13` | `DocumentUploader.tsx`, `DocumentViewer.tsx` | PR #78 / `specs/012-webp-clinical-viewer` | ✅ Concluido | 100% | Admitido en uploader y visor adaptativo con zoom. |
| **5.2** | Visor Interactivo de PDFs | `FE-14` | `DocumentViewer.tsx`, `DocumentViewer.test.tsx` | PR #78 / `specs/013-clinical-pdf-viewer` | ✅ Concluido | 100% | Skeleton Loader animado, zoom, fullscreen, descarga y 14 tests en verde. |
| **5.3** | Receptor de Alertas SSE | `FE-15` | Por crear (`alertStreamService.ts`) | Tarea 2.8 Backend / IA-08 | 🔴 Pendiente | 0% | Cliente EventSource hacia `/alerts/stream` y banner flotante. |
| **5.4** | Paginación Remota y Tests Unitarios | `FE-16` | `DocumentTable.tsx`, `DocumentTable.test.tsx` | Sprint 3 / Requisito QA | 🟡 En Progreso | 50% | Paginación por servidor y tests unitarios de componentes clave. |

---

## 🔐 Bloque 1: Tareas Formales Respaldadas por Specs (`specs/`)

### Tarea 1.1: Módulo de Inicio de Sesión (Login) y Shell Visual
- **Asignado**: Desarrollador 1 (Frontend / Auth)
- **Estado Real**: ✅ **CONCLUIDO (100%)**
- **Spec Oficial**: [specs/004-login-frontend](file:///home/wigsdev/GitHub/mediflow/specs/004-login-frontend/spec.md)
- **Objetivo**: Renderizar la pantalla de login con branding institucional, tipografías corporativas (Quicksand y Montserrat), orbes decorativos, diseño responsivo sin credenciales hardcodeadas y sección testimonial oculta en pantallas `< 768px`.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/pages/Login.tsx`: Contenedor principal con orbes decorativos animados y responsive.
  - `frontend/src/components/login/LoginForm.tsx`: Formulario de acceso con inputs estilizados, botón deshabilitado durante el envío y alertas de error visuales.
  - `frontend/src/components/login/TestimonialSection.tsx`: Sección testimonial con cita médica y autoría, adaptada para ocultarse en móviles.
  - `frontend/src/styles/login.css`: Keyframes de animación de orbes y tipografías.
  - Pruebas automatizadas en verde: `src/pages/Login.test.tsx`, `src/components/login/LoginForm.test.tsx`, `src/components/login/TestimonialSection.test.tsx`.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  - Ningún faltante funcional; el módulo está 100% operativo y probado.
- **🛠️ Ejecución MANUAL de Verificación**:
  ```powershell
  cd frontend
  npm test -- src/pages/Login.test.tsx
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Pantalla de inicio de sesion clinica con validaciones reactivas y gestion segura de tokens JWT
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 1.2: Módulo de Registro de Usuarios Clínicos (Sign Up)
- **Asignado**: Desarrollador 1 (Frontend / Auth)
- **Estado Real**: ✅ **CONCLUIDO (100%)**
- **Spec Oficial**: [specs/005-sign-up-flow](file:///home/wigsdev/GitHub/mediflow/specs/005-sign-up-flow/spec.md)
- **Objetivo**: Permitir a nuevos profesionales de la salud registrarse en MediFlow mediante formulario con validación de fortaleza de contraseñas y alta en estado `PENDIENTE` para posterior autorización administrativa.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/pages/SignUp.tsx` y `frontend/src/pages/SignUpPage.tsx`: Vistas de registro que alojan el formulario.
  - `frontend/src/components/auth/SignUpForm.tsx`: Formulario completo (Nombres, Apellidos, Teléfono, Correo, Contraseña, Confirmación), con validación reactiva de coincidencia de claves.
  - Conexión con `POST /api/v1/auth/signup` mediante `registerUser()` en `auth.api.ts`.
  - Tratamiento de respuesta: confirmación visual de solicitud enviada en estado `PENDIENTE` y tratamiento de HTTP 409 Conflict si el correo ya existe.
  - Pruebas automatizadas en verde: `src/tests/components/auth/SignUpForm.test.tsx`.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  - Ningún faltante funcional; el módulo está 100% operativo y probado.
- **🛠️ Ejecución MANUAL de Verificación**:
  ```powershell
  cd frontend
  npm test -- src/tests/components/auth/SignUpForm.test.tsx
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Formulario de registro de usuarios hospitalarios con validacion de credenciales y estado pendiente
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 1.3: Autenticación por Correo, AuthContext y Control RBAC
- **Asignado**: Desarrollador 2 (Frontend / Security & Shell)
- **Estado Real**: ✅ **CONCLUIDO (100%)**
- **Spec Oficial**: [specs/006-login-email-auth](file:///home/wigsdev/GitHub/mediflow/specs/006-login-email-auth/spec.md)
- **Objetivo**: Refactorizar la autenticación para operar exclusivamente con correo electrónico y contraseña, almacenar el objeto `SessionUser` tipado en `AuthContext` y gobernar la navegación protegida con `ProtectedRoute`.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/components/login/LoginForm.tsx`: Adaptado para exigir formato de correo electrónico (`/^[^\s@]+@[^\s@]+\.[^\s@]+$/`) y contraseña.
  - `frontend/src/api/auth.api.ts`: Cliente `loginUser()` adaptado para enviar `{ correo, password }` al backend.
  - `frontend/src/context/AuthContext.tsx`: Almacena `SessionUser` con rol (`ADMINISTRADOR`, `OPERADOR`, `COORDINADOR`, `AUDITOR`, `SUPERVISOR`, `PENDIENTE`), nombres, correo y token activo, exponiendo el hook `useAuth()`.
  - `frontend/src/routes/ProtectedRoute.tsx`: Intercepta la navegación y redirige a `/login` si no está autenticado o a `/dashboard` si el rol no tiene permisos.
  - Pruebas automatizadas en verde integradas en `Login.test.tsx`.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  - Ningún faltante funcional; el flujo de autenticación y sesión está completo.
- **🛠️ Ejecución MANUAL de Verificación**:
  ```powershell
  cd frontend
  npm test
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Autenticacion clinica por correo electronico almacenamiento de sesion en AuthContext y rutas protegidas
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

## ⚡ Bloque 2: Módulos Operativos y de Triaje Clínico *(Implementados en `develop`)*

### Tarea 2.1: Módulo de Bienvenida y Onboarding para Cuentas Pendientes + Dashboard
- **Asignado**: Desarrollador 2 (Frontend / UX)
- **Estado Real**: 🟡 **EN PROGRESO (90% implementado, faltan tests unitarios y métricas API)**
- **Origen**: Código en rama `develop` (Prototipos Figma / `Dashboard.tsx` y `Sidebar.tsx`)
- **Objetivo**: Proveer la experiencia de aterrizaje al iniciar sesión: vista institucional para cuentas con rol `PENDIENTE` que bloquee el menú operativo, y panel con KPIs y documentos recientes para usuarios activos.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/pages/Dashboard.tsx` (L49-86): Si `user?.rol === 'PENDIENTE'`, muestra vista limpia con el logo `assets/login/logo.png`, la ilustración institucional `assets/ImagenBienvenida.png` y el mensaje de espera de confirmación administrativa.
  - `frontend/src/components/layout/Sidebar.tsx` (L148-168): Si el usuario es `PENDIENTE`, oculta todos los enlaces y muestra exclusivamente "Inicio".
  - Para usuarios activos: Renderiza `PageHeader`, 4 `StatsCard` (Procesados, Urgentes, Auditoría, Errores) y tabla de `RecentDocuments`.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  1. Crear `frontend/src/pages/Dashboard.test.tsx` validando que:
     - El rol `PENDIENTE` no ejecuta llamadas a endpoints protegidos de documentos y renderiza la pantalla de bienvenida.
     - Un rol activo renderiza los KPIs y la tabla de documentos recientes.
  2. Conectar la consulta de estadísticas al endpoint formal `/api/v1/metrics` en lugar de calcular métricas locales a partir de los 20 documentos recientes de `DashboardSummary`.
- **🛠️ Ejecución MANUAL**:
  1. Crear `frontend/src/pages/Dashboard.test.tsx`.
  2. Correr la prueba con Vitest:
     ```powershell
     cd frontend
     npm test -- src/pages/Dashboard.test.tsx
     ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Pantalla de bienvenida institucional y bloqueo de navegacion para usuarios en estado pendiente
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 2.2: Módulo de Nuevo Enrutamiento y Carga de Documentos Clínicos
- **Asignado**: Desarrollador 3 (Frontend / Ingesta)
- **Estado Real**: 🟢 **EN PROGRESO (95% implementado, modal rediseñado y probado)**
- **Spec Oficial / Origen**: [specs/009-triage-modal-redesign](file:///home/wigsdev/GitHub/mediflow/specs/009-triage-modal-redesign/spec.md) (Rediseño visual de modal) y código en `develop` (`NewDocument.tsx`, `DocumentUploader.tsx`)
- **Objetivo**: Permitir la carga interactiva de documentos médicos (PDF, JPG, PNG, WEBP) seleccionando el canal hospitalario de procedencia, mostrando barra de progreso integrada durante la inferencia de IA, con navegación por píldoras RBAC y redirigiendo a la ficha clínica.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/pages/NewDocument.tsx`: Rediseño visual completo y estandarizado con Tailwind CSS conforme a `specs/009-triage-modal-redesign`:
    - **Barra de navegación de píldoras (`NAV_PILLS`)**: Píldora activa `Enrutamiento` con control de visibilidad RBAC (`ADMINISTRADOR` visualiza Enrutamiento, Historial y Solicitudes; otros roles visualizan Enrutamiento e Historial).
    - **Modal de carga Bento Card**: Dropzone delimitada con borde punteado suave, ícono FontAwesome (`faFolder`), halo difuso y botón primario corporativo `Seleccionar archivos` (`var(--primary)` / `#2C5282`).
    - **Visualización estilizada del archivo cargado**: Barra horizontal compacta con ícono FontAwesome `faPaperclip`, nombre de archivo, peso en MB (`formatFileSize`), y botones de acción `Cancelar` (`faTrashAlt`) y `Continuar`.
    - **Retroalimentación de procesamiento en tiempo real**: Loader circular animado (`faCircleNotch`) y estado deshabilitado en botones durante la inferencia del agente.
    - **Selector de canal hospitalario**: Menú desplegable para `Consulta_Externa`, `Guardia_Emergencias`, `Hospitalizacion` y `Farmacia_Hospitalaria`.
    - **Llamada a API**: Conexión con `documentsApi.procesarDocumento(file, canalOrigen)`.
  - `frontend/src/pages/NewDocument.test.tsx`:
    - Suite de 155 líneas de pruebas unitarias automatizadas con Vitest y React Testing Library que valida las píldoras RBAC (US1), selección de archivos (US2), estados de carga y procesamiento (US3) (100% pasando en verde).
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  1. Añadir botón explícito de reintento en la alerta de error si la petición falla por timeout o error 500.
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npm test -- src/pages/NewDocument.test.tsx
  npm run build
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Interfaz de carga de documentos clinicos con drag and drop seleccion de canal y barra de progreso
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 2.3: Ficha de Detalle Clínico del Documento y Extracción de Entidades
- **Asignado**: Desarrollador 4 (Frontend / Triaje)
- **Estado Real**: 🟢 **EN PROGRESO (95% implementado, prescripciones integradas)**
- **Origen**: Código en rama `develop` (`DocumentDetail.tsx`, `ExtractedData.tsx`)
- **Objetivo**: Mostrar en `/documentos/:id` la ficha médica completa del documento: previsualización del archivo, entidades clínicas estructuradas (paciente, diagnóstico CIE-10, hallazgos, medicamentos prescritos) y decisión de enrutamiento tomada por el agente.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/pages/DocumentDetail.tsx`: Consume `GET /api/v1/documents/{id}` vía `documentsApi.obtenerDocumentoPorId(id)`.
  - Columna Izquierda: Visor del archivo (`DocumentViewer`).
  - Columna Derecha: Tarjeta de datos extraídos (`ExtractedData.tsx`), nivel de prioridad (`PriorityBadge`), score de confianza (`ConfidenceIndicator`) y destino asignado (`RoutingDecision`).
  - `frontend/src/components/triage/ExtractedData.tsx`:
    - Tarjeta de Paciente (nombre, DNI, edad).
    - Tarjeta de Médico Tratante (nombre, colegiatura CMP).
    - Tarjeta de Documento y Especialidad.
    - Tarjeta de Información Clínica (diagnóstico, código CIE-10, estudio solicitado).
    - **Tabla estructurada de Medicamentos Prescritos (`FaPills`)**: Renderiza nombre del fármaco, dosis, frecuencia y vía de administración (inyectable, oral, etc.), deserializados dinámicamente desde el backend en `frontend/src/api/documentsApi.ts` y tipados con la interfaz `Medication` en `frontend/src/types/documents.ts` (alineado con la Tarea 2.7 / Requisito R3 / IA-07).
  - Selector de pestañas para alternar entre "Entidades Extraídas" y "Texto OCR Crudo" con botón para copiar al portapapeles.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  1. Crear pruebas unitarias `frontend/src/pages/DocumentDetail.test.tsx`.
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npm run build
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Ficha de detalle clinico de documento con visor integrado extraccion de entidades y trazabilidad
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 2.4: Consola Interactiva de Triaje Clínico y Casos Preestablecidos
- **Asignado**: Desarrollador 4 (Frontend / Consola Triaje)
- **Estado Real**: 🟢 **EN PROGRESO (95% implementado, faltan tests)**
- **Origen**: Código en rama `develop` (`TriageConsoleView.tsx` - 28.5 KB)
- **Objetivo**: Brindar una consola interactiva en `/triaje` para validar en tiempo real el pipeline del agente IA mediante 4 casos clínicos preconfigurados y visualización del JSON retornado.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/pages/TriageConsoleView.tsx`:
    - 4 casos clínicos listos: Caso 1 (Rutina / Analítica Normal), Caso 2 (Urgencia TEP), Caso 3 (Pediatría) y Caso 4 (Farmacia).
    - Selector dinámico con clase visual `.active-preset`.
    - Envío del caso hacia `triage.api.ts` y visualización del diagnóstico, CIE-10 y destino asignado.
    - Pestaña para inspeccionar el JSON crudo del `AgentState`.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  1. Crear pruebas unitarias `frontend/src/pages/TriageConsoleView.test.tsx`.
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npm run build
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Consola interactiva de triaje clinico con casos preestablecidos y visualizacion de diagnosticos CIE-10
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 2.5: Integración y Visualización Integral de Medicamentos Prescritos, Deserialización en API y Resiliencia del Visor Clínico
- **Asignado**: Desarrollador 4 (Frontend / Triaje & Prescripciones)
- **Estado Real**: ✅ **CONCLUIDO (100% implementado y verificado con pruebas unitarias y especificación Spec Kit)**
- **Spec / Origen**: Requisito R3 / Tarea Backend IA-07 / [specs/014-prescription-medication-viewer](file:///home/wigsdev/GitHub/mediflow/specs/014-prescription-medication-viewer/spec.md)
- **Objetivo**: Conectar el frontend con el modelo de datos de farmacoterapia y prescripciones médicas generado por el agente de triaje, permitiendo visualizar la lista estructurada de fármacos con su posología, frecuencia y vía de administración en todas las vistas clínicas (Detalle de Documento, Consola de Triaje y Auditoría Médica), además de corregir la accesibilidad semántica de encabezados en el visor de documentos para garantizar pruebas en verde con Testing Library.
- **📦 Lo que YA está implementado y probado**:
  - `frontend/src/types/documents.ts`:
    - Definición de la interfaz tipada `Medication`:
      ```typescript
      export interface Medication {
        nombre?: string
        medicamento?: string
        dosis?: string
        frecuencia?: string
        via_administracion?: string
      }
      ```
    - Extensión de la estructura `ClinicalDocument.datos_extraidos.medicamentos?: Medication[]`.
  - `frontend/src/api/documentsApi.ts`:
    - Deserialización dinámica de la colección `medicamentos` desde `datos_extraidos.medicamentos` del backend (mapeo dual `m.medicamento || m.nombre` y vías).
  - `frontend/src/components/triage/ExtractedData.tsx`:
    - Componente de tabla con ícono `FaPills`, encabezados (*Medicamento*, *Dosis*, *Frecuencia*, *Vía*), fila por cada fármaco detectado y badge estilizado para `via_administracion` (oral, inyectable, tópica, etc.).
    - Estado defensivo: si no hay medicamentos prescritos, despliega mensaje sobrio sin saturar la tarjeta clínica.
  - `frontend/src/pages/TriageConsoleView.tsx`:
    - Renderizado de la tabla de prescripciones extraídas en tiempo real para los casos clínicos preestablecidos y casos manuales.
  - `frontend/src/pages/AuditDetail.tsx`:
    - Tabla de medicamentos detectados en el formulario de resolución y rectificación de auditoría médica HITL, permitiendo al médico revisar las recetas antes de confirmar o rectificar el destino a `Farmacia_Hospitalaria`.
  - `frontend/src/components/documents/DocumentViewer.tsx`:
    - Desacoplamiento del encabezado `<h3>` del panel de contingencia clínica (`"Error de decodificación de imagen clínica"` / `"Error de visualización del documento PDF"`), eliminando colisiones en Testing Library y optimizando accesibilidad.
  - `frontend/src/tests/components/triage/ExtractedData.test.tsx`:
    - Suite de 4 pruebas unitarias con Vitest y Testing Library verificando renderizado de columnas, badges de vía, estado vacío y sanitización anti-XSS.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  - Ningún faltante técnico o funcional; módulo 100% concluido y verificado.
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npx vitest run src/tests/components/triage/ExtractedData.test.tsx
  npm run build
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Visualizacion estructurada de medicamentos prescritos vias de administracion y robustez del visor clinico
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

## 📊 Bloque 3: Trazabilidad, Historial & Auditoría Médica *(Implementados en `develop`)*

### Tarea 3.1: Módulo de Historial de Enrutamiento y Trazabilidad de Documentos
- **Asignado**: Desarrollador 5 (Frontend / Data Tables)
- **Estado Real**: 🟡 **EN PROGRESO (85% implementado, falta paginación remota de backend)**
- **Origen**: Código en rama `develop` (`Documents.tsx`, `DocumentTable.tsx`)
- **Objetivo**: Proveer la vista central de trazabilidad en `/documentos` para auditar, buscar y filtrar todos los documentos clínicos procesados por el sistema MediFlow.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/pages/Documents.tsx`:
    - Tarjetas de KPIs en la cabecera: Total, Procesados, En auditoría y Urgentes.
    - Barra de filtros: Estado (`PROCESADO`, `AUDITORIA`, etc.), Prioridad (`URGENTE`, `RUTINA`, `AMBIGUO`), Tipo de documento (`CLINICAL_DOCUMENT_TYPES`) y buscador de paciente/DNI en vivo.
    - Botón de refresco manual (`refetch`) con ícono `FaSync`.
  - `frontend/src/components/documents/DocumentTable.tsx`: Tabla responsiva con badges de prioridad, badges de estado y score de confianza (`formatConfidence`).
  - Consumo del endpoint `GET /api/v1/documents` mediante el hook `useDocuments.ts`.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  1. **Paginación Remota**: Actualmente el componente solo renderiza los primeros 20 documentos que el backend retorna por defecto. Se deben enviar los parámetros de paginación (`skip`, `limit`) al hook `useDocuments` para consultar páginas posteriores.
  2. Crear pruebas unitarias `frontend/src/pages/Documents.test.tsx` y `DocumentTable.test.tsx`.
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npm test
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Vista de historial de documentos clinicos con filtros avanzados trazabilidad y metricas KPI
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 3.2: Bandeja de Solicitudes de Intervención Manual / Auditoría Médica (HITL)
- **Asignado**: Desarrollador 5 (Frontend / Auditoría)
- **Estado Real**: 🟢 **EN PROGRESO (92% implementado, bandeja 100% rediseñada y testeada)**
- **Spec Oficial / Origen**: [specs/010-audit-view-redesign](file:///home/wigsdev/GitHub/mediflow/specs/010-audit-view-redesign/spec.md) (Rediseño visual de bandeja) y código en `develop` (`AuditDetail.tsx` - 14.5 KB)
- **Objetivo**: Permitir a coordinadores y médicos revisores examinar casos con baja confianza o discrepancias (*Human-in-the-Loop*), confirmando o rectificando el diagnóstico, la prioridad y el destino hospitalario en una interfaz clínica sobria, moderna y responsiva.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/pages/Audit.tsx`: Rediseño visual completo y estandarizado con Tailwind CSS conforme a `specs/010-audit-view-redesign`:
    - **Barra de navegación de píldoras (`NAV_PILLS`)**: Navegación superior con control de roles RBAC (`useAuth`), destacando la píldora activa `Solicitudes`.
    - **Jerarquía y contenedor**: Título principal centrado **"Solicitudes de auditoría clínica"** (tipografía *Montserrat*) y tarjeta blanca estilo "Bento" con esquinas redondeadas (`rounded-3xl`), sombra suave y bordes limpios (omitiendo el dropdown de filtros de la maqueta).
    - **Conservación íntegra de columnas clínicas**: `ID`, `Documento`, `Confianza`, `Motivo de Derivación`, `Fecha`, y `Visualizar`.
    - **Escala cuádruple de confianza**: Badges calculados por `frontend/src/utils/auditConfidence.ts` (<25% rojo `var(--error)`, 25%-50% naranja `var(--orange)`, 50%-75% amarillo `var(--warning)`, >75% verde `var(--green)`) con micro-indicador circular (`dotClass`) y porcentaje exacto.
    - **Botón de revisión outline interactivo**: Estilo outline con ícono de ojo de FontAwesome (`faEye`) y transición hover suave a azul (`var(--primary)` / `#2C5282`) con texto e ícono en blanco puro (`#ffffff`), redirigiendo a `/auditoria/${documento_id}`.
    - **Paginación visual numerada**: Control en el pie de la tarjeta con numeración formateada (`01`, `02`, etc.) a razón de 8 registros por página (`itemsPerPage = 8`).
    - **Diseño 100% responsivo**: Envoltorio `overflow-x-auto`, paddings adaptativos y truncado defensivo (`truncate`, `line-clamp-2`).
  - `frontend/src/pages/Audit.test.tsx`:
    - Suite de 227 líneas de pruebas unitarias automatizadas con Vitest y React Testing Library que valida los 4 tiers de confianza, las 6 columnas, estados de carga/vacío/error, paginación y navegación (100% pasando en verde).
  - `frontend/src/pages/AuditDetail.tsx`:
    - Formulario de resolución médica con tres acciones: **Aprobar**, **Rechazar** o **Corregir**.
    - Campos editables: Paciente, Médico, Tipo de documento, Especialidad, Diagnóstico, Código CIE-10, Prioridad y Destino.
    - Modal de confirmación (`ConfirmModal`) que envía `PATCH /api/v1/documents/{id}` vía `auditApi.ts`.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  1. Incluir el campo de texto "Observaciones del auditor médico" en el formulario de resolución en `AuditDetail.tsx` y asegurar su envío en el payload para trazabilidad hospitalaria.
  2. Crear pruebas unitarias `frontend/src/pages/AuditDetail.test.tsx` (notando que `Audit.test.tsx` ya se encuentra 100% implementado y probado).
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npm test -- src/pages/Audit.test.tsx
  npm run build
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Bandeja de auditoria medica asistida con formulario de rectificacion de diagnostico y resolucion HITL
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

## 👥 Bloque 4: Administración Hospitalaria, Pacientes & Ajustes *(Implementados en `develop`)*

### Tarea 4.1: Módulo de Gestión de Solicitudes de Acceso y Aprobación de Usuarios
- **Asignado**: Desarrollador 1 (Frontend / Admin)
- **Estado Real**: 🟡 **EN PROGRESO (85% implementado, falta vista aislada para solicitudes)**
- **Origen**: Código en rama `develop` (`UsersManagementView.tsx` - 29.2 KB)
- **Objetivo**: Proveer al Administrador del sistema un panel centralizado para autorizar cuentas en estado `PENDIENTE`, asignarles rol y especialidad médica, o inactivar usuarios.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/pages/UsersManagementView.tsx`:
    - Consulta de usuarios hospitalarios vía `fetchUsers()` (`GET /api/v1/users`).
    - Filtro por estado: `PENDIENTE`, `ACTIVO`, `INACTIVO`.
    - Modal para asignar rol (`OPERADOR`, `COORDINADOR`, `AUDITOR`, `SUPERVISOR`, `ADMINISTRADOR`) y especialidad médica.
    - Activación de cuenta mediante `updateUserDetails(id, { estado: 'ACTIVO', rol, especialidad })`.
    - Búsqueda por texto (nombre, correo, DNI), paginación y notificaciones Toast.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  1. Configurar la ruta `/solicitudes` y `/solicitudes-acceso` para que inicialice automáticamente el filtro `statusFilter` en `'PENDIENTE'`, mostrando directamente las solicitudes por autorizar sin mezclar con el catálogo general.
  2. Añadir un badge contador de solicitudes pendientes en el enlace correspondiente del `Sidebar.tsx`.
  3. Crear pruebas unitarias `UsersManagementView.test.tsx`.
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npm run dev
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Panel de administracion hospitalaria para aprobacion de solicitudes de acceso y asignacion de roles RBAC
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 4.2: Gestión de Pacientes y Empadronamiento Hospitalario
- **Asignado**: Desarrollador 6 (Frontend / Pacientes)
- **Estado Real**: 🟢 **EN PROGRESO (95% implementado, faltan tests)**
- **Origen**: Código en rama `develop` (`PatientsManagementView.tsx` - 44 KB de código)
- **Objetivo**: Administrar el padrón de pacientes hospitalarios (requisitos RF-06 al RF-09), permitiendo registrar pacientes, buscar por DNI o historia clínica y consultar sus episodios clínicos vinculados.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/pages/PatientsManagementView.tsx`:
    - Conexión con `GET /api/v1/patients`, `POST /api/v1/patients` y `GET /api/v1/patients/{id}/documents` mediante `patients.api.ts`.
    - Tabla completa de pacientes empadronados con filtros y paginación.
    - Modal de alta y edición de paciente con validación de tipo y número de documento.
    - Visualización de la historia clínica y documentos asociados al paciente seleccionado.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  1. Crear pruebas unitarias `frontend/src/pages/PatientsManagementView.test.tsx`.
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npm run build
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Modulo de empadronamiento y consulta de pacientes hospitalarios con historial de atenciones medicas
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 4.3: Configuración del Sistema y Preferencia de Almacenamiento (LOCAL vs OCI)
- **Asignado**: Desarrollador 6 (Frontend / Ajustes)
- **Estado Real**: 🟢 **EN PROGRESO (95% implementado, faltan tests)**
- **Origen**: Código en rama `develop` (`StorageSettingsView.tsx` - 12.6 KB)
- **Objetivo**: Administrar en `/configuracion` el modo de almacenamiento físico de archivos (`LOCAL` vs `OCI Object Storage`), garantizando el cumplimiento de la Regla de Oro (control 100% manual por el usuario).
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/pages/StorageSettingsView.tsx`:
    - Consulta de modo activo mediante `GET /api/v1/settings`.
    - Selector interactivo entre `LOCAL` (disco local del servidor) y `OCI` (Oracle Cloud Infrastructure).
    - Advertencia explícita informando que el cambio es estrictamente manual y afectará solo a las nuevas subidas.
    - Guardado mediante `PUT /api/v1/settings` con restricción exclusiva para usuarios `ADMINISTRADOR`.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  1. Crear pruebas unitarias `StorageSettingsView.test.tsx`.
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npm test
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Interfaz de configuracion de almacenamiento hospitalario para alternar entre modo local y Oracle Cloud
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

## 🖼️ Bloque 5: Tareas Independientes de Visualización Multimodal y Alertas *(Al Final)*

### Tarea 5.1: Soporte Completo para Carga, Validación y Previsualización de Imágenes en Formato WebP
- **Asignado**: Desarrollador 3 (Frontend / Visuals)
- **Estado Real**: ✅ **CONCLUIDO (100% implementado en develop vía PR #78)**
- **Referencia Oficial**: [specs/012-webp-clinical-viewer](file:///home/wigsdev/GitHub/mediflow/specs/012-webp-clinical-viewer/spec.md) e [Issue #70 / FE-13](https://github.com/No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/issues/70)
- **Objetivo**: Admitir el formato de imagen WebP (`image/webp`) tanto en la zona de carga de documentos como en los visores clínicos y auditorías, sincronizando el cliente con el pipeline multimodal de Gemini Vision del backend.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/components/documents/DocumentUploader.tsx`:
    - Incluye `"image/webp"` en `ALLOWED_TYPES`.
    - Regex de validación: `/\.(pdf|jpg|jpeg|png|webp)$/i`.
    - Atributo `accept` ampliado a `.pdf,.jpg,.jpeg,.png,.webp,image/webp`.
    - Chip visual `.WEBP` incorporado en las extensiones permitidas.
  - `frontend/src/components/documents/DocumentViewer.tsx`:
    - Detección de imágenes WebP y renderizado proporcional (`object-contain`).
    - Controles interactivos de zoom in, zoom out y reset al 100%.
    - Soporte de modo pantalla completa con la API nativa `requestFullscreen`.
    - Panel de contingencia clínica ante imágenes corruptas con opción de descarga y apertura externa.
  - Pruebas automatizadas en verde integradas en `DocumentViewer.test.tsx`.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  - Ningún faltante funcional; el módulo se encuentra 100% operativo y verificado.
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npx vitest run src/tests/components/documents/DocumentViewer.test.tsx
  ```

---

### Tarea 5.2: Optimización del Visor y Renderizado Interactivo de Documentos PDF con Skeleton Loader
- **Asignado**: Desarrollador 4 (Frontend / PDF Viewer)
- **Estado Real**: ✅ **CONCLUIDO (100% implementado en develop vía PR #78)**
- **Referencia Oficial**: [specs/013-clinical-pdf-viewer](file:///home/wigsdev/GitHub/mediflow/specs/013-clinical-pdf-viewer/spec.md) e [Issue #71 / FE-14](https://github.com/No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/issues/71)
- **Objetivo**: Optimizar la experiencia de lectura de documentos PDF clínicos en `DocumentViewer.tsx`, incorporando skeleton loader animado con Tailwind, controles de navegación rápida (descarga directa, abrir en nueva pestaña, pantalla completa) y tarjeta de error accesible ante fallos.
- **📦 Lo que YA está implementado en `develop`**:
  - `frontend/src/components/documents/DocumentViewer.tsx`:
    - **Skeleton Loader animado**: `role="status"` con pulso animado (`animate-pulse`) mientras el PDF se descarga y decodifica.
    - **Barra de herramientas superior**:
      - Botón **Descargar** (`FaDownload`) con atributo `download` y nombre original del archivo.
      - Botón **Abrir en nueva pestaña** (`FaExternalLinkAlt`) con `target="_blank"`.
      - Botón **Pantalla Completa** (`FaExpand`) conectado a `requestFullscreen` con fallback CSS.
      - Controles de zoom interactivo (50% a 250%) con escala preservada.
    - **Panel de contingencia clínica**: `role="alert"` con `FaExclamationTriangle`, encabezado accesible y botones de contingencia para descarga directa si falla el renderizado embebido.
  - `frontend/src/components/documents/DocumentViewer.types.ts`: Tipado estricto de props y estados de carga (`DocumentViewerProps`, `DocumentViewerState`).
  - `frontend/src/tests/components/documents/DocumentViewer.test.tsx`: Suite completa de 14 pruebas unitarias con Vitest y React Testing Library pasando al 100% en verde.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  - Ningún faltante funcional; el módulo se encuentra 100% operativo y probado.
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npx vitest run src/tests/components/documents/DocumentViewer.test.tsx
  ```

---

### Tarea 5.3: Receptor y Emisión de Alertas de Guardia en Tiempo Real (SSE)
- **Asignado**: Desarrollador 6 (Frontend / Realtime)
- **Estado Real**: 🔴 **PENDIENTE (0% implementado)**
- **Vinculación Oficial**: Tarea 2.8 de Backend (`GET /api/v1/alerts/stream`)
- **Objetivo**: Conectar el frontend clínico con el canal de Server-Sent Events (`/api/v1/alerts/stream`) para recibir y desplegar notificaciones acústicas y visuales inmediatas cuando el agente IA clasifique un caso crítico en `Cola_Emergencia_Medica` (Infarto, TEP, Shock).
- **📦 Lo que YA está implementado en `develop`**:
  - Ningún código cliente existe aún para Server-Sent Events en el frontend.
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  1. Crear el servicio `frontend/src/services/alertStreamService.ts` utilizando `EventSource` hacia `${API_BASE_URL}/api/v1/alerts/stream` con reconexión automática.
  2. Crear el componente visual flotante `frontend/src/components/common/EmergencyAlertToast.tsx` para mostrar notificaciones urgentes rojas con paciente, diagnóstico y botón de navegación directa al episodio.
  3. Incorporar sonido de alerta de guardia configurable (activable/desactivable por el usuario).
  4. Integrar el receptor en `frontend/src/components/layout/MainLayout.tsx` para escucha activa en toda la aplicación.
  5. Validar con pruebas unitarias en Vitest.
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npm test
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Receptor de alertas medicas criticas en tiempo real mediante SSE y notificaciones visuales flotantes
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 5.4: Paginación Remota de Documentos y Cobertura Integral de Pruebas Unitarias ([FE-16 / Issue #73])
- **Asignado**: Desarrollador 5 & 6 (Frontend / Admin & QA)
- **Estado Real**: 🟡 **EN PROGRESO (50% implementado)**
- **Referencia Oficial**: [Issue #73 / FE-16](https://github.com/No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/issues/73)
- **Objetivo**: Habilitar la paginación remota por servidor en la tabla de documentos (`DocumentTable.tsx`) y completar la suite de pruebas unitarias en Vitest para todos los módulos de la interfaz, asegurando 0 regresiones conforme a la Regla de Oro.
- **📦 Lo que YA está implementado en `develop`**:
  - `DocumentTable.tsx`: Tabla clínica con renderizado de estados, severidad, tipo de documento y chips de estado.
  - 14 archivos de pruebas y 98 tests unitarios pasando al 100% en verde en Vitest (`vitest run`).
- **⚠️ Lo que está INCONCLUSO / PENDIENTE**:
  1. Conectar parámetros de paginación `page` y `limit` en `DocumentTable.tsx` contra la API.
  2. Implementar selector de tamaño de página y controles de navegación de página.
  3. Crear `DocumentTable.test.tsx` y pruebas unitarias de los módulos administrativos (`PatientsManagementView.test.tsx`, `StorageSettingsView.test.tsx`).
- **🛠️ Ejecución MANUAL**:
  ```powershell
  cd frontend
  npm test
  ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Paginacion remota en tabla de historial y suite de pruebas unitarias para componentes react
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

## 🏁 Criterios de Aceptación Globales del Frontend (DoD)

Para dar por concluido cualquier bloque o entrega en el Frontend de MediFlow, se debe cumplir empíricamente:

1. **0 Errores de TypeScript**: `npm run build` debe generar el bundle de distribución sin errores tipográficos ni variables sin usar (`tsc -b` limpio).
2. **100% de Pruebas Automatizadas en Verde**: `npx vitest run` debe pasar todas las pruebas unitarias sin fallos (**14 archivos de prueba / 98 tests en verde**).
3. **Diseño Clínico Sobrio y Responsivo**: Utilizar Tailwind CSS, respetando la paleta de colores institucional, sin emojis amontonados en títulos o botones, y adaptable a dispositivos móviles y pantallas médicas.
4. **Respeto a la Regla de Oro**: Ninguna funcionalidad del cliente debe quemar credenciales, forzar modos de almacenamiento no autorizados ni alterar contratos REST sin sincronización con OpenAPI.
