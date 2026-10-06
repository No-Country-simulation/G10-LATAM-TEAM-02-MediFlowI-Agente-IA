# Data Model: Frontend de Login

**Date**: 2026-10-05

## Entities

### LoginFormData

Formulario de inicio de sesión. No se persiste. Datos en memoria (React state).

| Field | Type | Validation | Notes |
|-------|------|------------|-------|
| `documentoIdentidad` | `string` | Required, numeric, maxLength 8 | DNI del usuario |
| `password` | `string` | Required, minLength 1 | Contraseña del usuario |

**State transitions**: `empty` → `typing` → `submitting` → `success` | `error`

### LoginResult (existente, no se modifica)

Contrato del hook `useAuth().login()`. Ya definido en `src/context/auth-context.ts`.

| Field | Type | Notes |
|-------|------|-------|
| `success` | `boolean` | Resultado de la autenticación |
| `user` | `SessionUser` (optional) | Datos del usuario si success |
| `message` | `string` (optional) | Mensaje de error si !success |

### SessionUser (existente, no se modifica)

Ya definido en `src/context/auth-context.ts`. Incluye `id`, `documento_identidad`, `nombres`, `apellidos`, `rol`, `estado`, `token`, etc.

## Component State

### Login.tsx (página contenedor)

| State | Type | Initial | Notes |
|-------|------|---------|-------|
| `documentoIdentidad` | `string` | `""` | Campo controlado |
| `password` | `string` | `""` | Campo controlado |
| `error` | `string` | `""` | Mensaje de error |
| `isSubmitting` | `boolean` | `false` | Estado de carga |

**No se añade state para credenciales de desarrollo.** No hay panel dev-only.

## Relationships

```
Login.tsx
  ├── LoginForm.tsx (formulario DNI + password + botón submit + enlace registro)
  └── TestimonialSection.tsx (cita + autor + cargo, hidden en móvil)
```

- `Login.tsx` usa `useAuth()` para obtener `login()`.
- `Login.tsx` usa `useNavigate()` y `useLocation()` para redirección post-login.
- No se modifica `AuthContext`, `useAuth`, `auth.api.ts`, ni `httpClient.ts`.
