# Research & Architectural Decisions: Autenticación por Correo y Gestión Global de Sesión

**Feature**: `006-login-email-auth`  
**Date**: 2026-10-12  
**Status**: Completed

---

## 1. Decisiones de Arquitectura e Implementación

### Decision 1: Mecanismo de Identificación en Login (Correo Electrónico Primario)
- **Decisión**: La interfaz de usuario solicita exclusivamente `correo` y `contraseña`. El backend acepta `correo` o `documento_identidad` (retrocompatibilidad) resolviendo el usuario mediante búsqueda indexada en PostgreSQL (`get_user_by_email` vs `get_user_by_document`).
- **Racional**:
  - En entornos clínicos y hospitalarios modernos, el correo electrónico institucional es el identificador universal más amigable para el personal, reduciendo errores de tecleo asociados a documentos de identidad numéricos extensos.
  - El backend mantiene compatibilidad dual para no romper integraciones o suites de pruebas de API existentes que usaban DNI.
- **Alternativas consideradas**:
  - *Identificador unificado en un solo campo de texto*: Descartado en UI porque induce a ambigüedad en el placeholder y validaciones de formato de email.
  - *Migrar toda la base de datos eliminando documento_identidad*: Descartado porque el DNI de 8 cifras es legalmente requerido en la ficha de personal médico y auditoría clínica hospitalaria.

---

### Decision 2: Gestión y Seguridad de Tokens de Sesión
- **Decisión**: Los tokens de sesión son cadenas opacas generadas con `secrets.token_hex(32)` con prefijo `mf_session_`. En PostgreSQL (`sesiones_usuario`), se almacena únicamente el resumen irreversible `SHA-256` (`token_hash`), junto con `expires_at` y `revoked_at`.
- **Racional**:
  - Almacenar solo el hash del token en la base de datos previene el robo o secuestro de sesiones en caso de una fuga de volcado de base de datos.
  - El soporte de `revoked_at` permite revocación inmediata de sesiones activas desde el servidor (logout real), superando la limitación de los JWTs no revocables.
- **Alternativas consideradas**:
  - *JWTs sin estado (stateless)*: Descartados porque no permiten revocación centralizada en tiempo real ni invalidación forzada por el Administrador.
  - *Cookies HTTP-only*: Consideradas, pero la arquitectura de MediFlow expone API REST desacoplada que también es consumida por clientes móviles y herramientas de soporte.

---

### Decision 3: Almacenamiento Global y Rehidratación Segura en el Frontend
- **Decisión**:
  1. En `localStorage` se persiste **únicamente** `{ access_token: "mf_session_..." }` bajo la clave `"mediflow_auth_session"`. No se almacenan contraseñas, sales ni datos sensibles.
  2. En memoria volátil de React (`AuthContext`), se almacena el objeto de usuario completo (`SessionUser`) con:
     `id`, `documento_identidad`, `nombres`, `apellidos`, `correo`, `especialidad_medica`, `rol`, `estado` y `token`.
  3. Al recargar la página (`F5`), el efecto de inicialización lee el token, invoca `GET /auth/me` contra PostgreSQL y reconstruye el estado global de forma segura. Si el token está revocado o expirado, se expulsa al usuario al login.
- **Racional**:
  - Evita almacenar datos de perfil obsoletos en `localStorage`.
  - Asegura que cualquier cambio en los roles o estado del usuario (`ACTIVO` $\rightarrow$ `INACTIVO`) en la base de datos surta efecto inmediato en la siguiente recarga o verificación.
- **Alternativas consideradas**:
  - *Persistir todo el objeto User en localStorage*: Descartado por riesgo de sincronización (un usuario deshabilitado en base de datos podría seguir viendo temporalmente información en el cliente hasta que expire una llamada API).

---

### Decision 4: Integración Completa de `especialidad_medica`
- **Decisión**:
  - Asegurar que `u.especialidad_medica` forme parte del `SELECT` en `session_repository.py` y se exponga en `user_payload` en `auth.py`.
  - El frontend ya tipa `especialidad_medica?: string` en la interfaz `User`.
- **Racional**:
  - Para los roles clínicos (`COORDINADOR` y `OPERADOR`), la especialidad médica determina la aptitud para derivaciones y revisiones HITL. Al estar en la sesión global, los componentes pueden renderizar la especialidad del médico en la cabecera y en los reportes de atención.

