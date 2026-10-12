# Guía Rápida de Validación (Quickstart): Flujo de Login y Gestión de Sesión

**Feature**: `006-login-email-auth`  
**Fecha**: 2026-10-12

---

## 🚀 1. Prerrequisitos

- Entorno de desarrollo levantado con Docker:
  ```bash
  docker compose -f infrastructure/docker/docker-compose.dev.yml up -d
  ```
- Base de datos `mediflow_dev` migrada con Alembic:
  ```bash
  docker exec mediflow-backend-dev alembic upgrade head
  ```
- Dependencias de frontend instaladas en `frontend/`:
  ```bash
  cd frontend && npm install
  ```

---

## 🧪 2. Escenarios de Validación Automatizada

### Escenario 1: Pruebas Unitarias del Formulario de Login (Frontend)
Ejecuta la suite de pruebas del componente `Login` en Vitest:
```bash
cd frontend
npx vitest run src/pages/Login.test.tsx --pool=forks
```
**Resultado Esperado**:
- `16/16` pruebas pasando en verde.
- Comprueba que el campo `CORREO` se renderiza correctamente con `type="email"`.
- Comprueba que el botón está deshabilitado si los campos están vacíos.
- Comprueba que escribir actualiza el estado y no el nombre del input.
- Comprueba que un correo mal formado (`"cadena_invalida"`) muestra el mensaje de error:
  `"Por favor, introduzca una dirección de correo electrónico válida"`.
- Comprueba que el login exitoso navega al `/dashboard`.

---

### Escenario 2: Compilación y Verificación de Tipos Estrictos
Verifica que TypeScript compile sin errores de tipos en contratos o componentes:
```bash
cd frontend
npm run build
```
**Resultado Esperado**:
- Salida limpia de `tsc -b` con código de retorno `0`.
- Bundle generado por Vite sin errores ni advertencias.

---

### Escenario 3: Validación de Endpoints Backend con Pytest
Verifica los endpoints de autenticación y sesiones:
```bash
docker exec mediflow-backend-dev pytest -v
```
**Resultado Esperado**:
- Validación de login por correo y DNI.
- Validación de rechazo de contraseñas incorrectas y cuentas inactivas.
- Comprobación de que `/auth/me` expone `especialidad_medica`, `rol`, `estado` y demás atributos de sesión.

---

## 🖥️ 3. Validación Manual Paso a Paso en el Navegador

1. Abre el navegador en `http://localhost:5173/login`.
2. Verifica visualmente que los únicos campos mostrados son **CORREO** y **CONTRASEÑA**.
3. Confirma que el botón "Iniciar sesión" se encuentra deshabilitado inicialmente.
4. Escribe un correo inválido como `prueba` y una contraseña:
   - Al pulsar o intentar enviar, observa el mensaje de advertencia debajo del campo:
     `"Por favor, introduzca una dirección de correo electrónico válida"`.
5. Ingresa credenciales válidas:
   - Correo: `admin@mediflow.local`
   - Contraseña: (contraseña asignada)
6. Haz clic en "Iniciar sesión":
   - El sistema valida, genera la sesión y redirige a `/dashboard`.
7. Abre la consola de desarrollador (`F12` ➔ pestaña *Application* / *Almacenamiento Local*):
   - Verifica que `mediflow_auth_session` almacena únicamente `{"access_token":"mf_session_..."}`.
8. En la consola (`F12`), inspecciona el objeto `user` en memoria del `AuthContext`:
   - Confirma que contiene: `id`, `documento_identidad`, `nombres`, `apellidos`, `correo`, `especialidad_medica`, `rol` y `estado`.
9. Presiona `F5` para recargar la página:
   - La sesión permanece activa e intacta, rehidratando todos los campos desde `/auth/me`.
10. Haz clic en "Cerrar sesión":
    - La sesión se revoca en base de datos, se borra el token local y el sistema redirige al `/login`.

