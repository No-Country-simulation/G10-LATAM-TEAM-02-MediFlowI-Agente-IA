# UI Contract: Pantalla de Login

**Date**: 2026-10-05

## Route

- **Path**: `/login`
- **Access**: Public (no requiere autenticación)
- **Redirect on success**: `location.state?.from?.pathname || "/dashboard"`

## Component API

### Login (default export)

```typescript
// src/pages/Login.tsx
export default function Login(): JSX.Element
```

No recibe props. Usa `useAuth()` y `useNavigate()` internamente.

### LoginForm

```typescript
// src/components/login/LoginForm.tsx
interface LoginFormProps {
  onSubmit: (documentoIdentidad: string, password: string) => Promise<void>
  isSubmitting: boolean
  error: string
}
```

### TestimonialSection

```typescript
// src/components/login/TestimonialSection.tsx
// Sin props. Componente presentacional puro.
export function TestimonialSection(): JSX.Element
```

## DOM Structure (semantic)

```html
<main>                          <!-- contenedor principal, min-h-screen -->
  <div> (orbes decorativos)     <!-- aria-hidden="true", absolute positioned -->
  <div> (grid 2 columnas en desktop)
    <section> (testimonial)     <!-- hidden md:flex, aria-label="Testimonio" -->
      <blockquote> (cita)
      <cite> (autor)
      <div> (cargo)
    </section>
    <section> (formulario)      <!-- aria-labelledby="welcome-heading" -->
      <p> (sistema autónomo...)
      <img> (logo MediFlow)
      <form>
        <h1> "Bienvenido"
        <p> (subtítulo)
        <label> DNI → <input type="text" inputMode="numeric" maxLength=8>
        <label> Contraseña → <input type="password">
        <button type="submit"> "Iniciar sesión"
        <footer> "¿No tienes una cuenta?" + <button> "Regístrate"
      </form>
    </section>
  </div>
</main>
```

## Accessibility Contract

- Todos los `<input>` tienen `<label>` asociado vía `htmlFor`/`id`.
- `autoComplete="username"` en DNI, `autoComplete="current-password"` en contraseña.
- `aria-live="polite"` para mensajes de error.
- `aria-hidden="true"` en elementos decorativos (orbes, líneas).
- Navegable por teclado (tab order natural).
- Botón submit se deshabilita durante `isSubmitting`.

## Responsive Contract

| Breakpoint | Testimonial | Form | Layout |
|------------|-------------|------|--------|
| >= 768px (md) | Visible | Visible | 2 columnas (grid) |
| < 768px | Hidden (`hidden`) | Visible | 1 columna, centrado |

## Security Contract

- Cero strings que coincidan con patrones de credenciales (DNI, password, token).
- No hay `defaultValue` en inputs. Solo `value` controlado + `onChange`.
- No hay panel dev-only ni helper de autocompletar.
- El `error` del AuthContext se muestra tal cual pero nunca incluye stack traces.
