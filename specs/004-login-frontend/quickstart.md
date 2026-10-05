# Quickstart: Frontend de Login

**Date**: 2026-10-05

## Prerequisites

- Node.js 18+
- npm
- Backend MediFlow corriendo en `http://localhost:8000` (para testear login real; no obligatorio para tests unitarios)

## Setup

```bash
cd frontend
npm install
```

## Run Tests

```bash
# Tests unitarios (vitest)
npm run test

# Compilación TypeScript&build
npm run build
```

**Expected outcomes**:
- `vitest run`: 100% pruebas en verde, 0 fallos.
- `npm run build`: Compilación limpia, 0 errores TypeScript, 0 warnings.

## Run Dev Server

```bash
npm run dev
```

**Validación manual**:
1. Navegar a `http://localhost:5173/login`
2. Verificar: logo MediFlow, título "Bienvenido", campos DNI + contraseña, botón "Iniciar sesión"
3. Verificar: sección testimonial visible en escritorio (lado izquierdo)
4. Redimensionar a < 768px: testimonial se oculta, formulario centrado
5. Presionar "Iniciar sesión" con campos vacíos: validación de requeridos
6. Ingresar credenciales válidas: redirect a `/dashboard`
7. Ingresar credenciales inválidas: mensaje de error amigable
8. Presionar "Regístrate": navega a ruta de registro
9. Inspeccionar código fuente: 0 credenciales hardcodeadas

## Verify No Hardcoded Credentials

```bash
# Buscar patrones sospechosos en el código del login
rg -i "password|credencial|token|secret|12345678|admin" src/pages/Login.tsx src/components/login/
# Expected: solo referencias a variables (password state, autoComplete), no valores literales
```
