# Research: Frontend de Login

**Date**: 2026-10-05

## R1: Tailwind CSS Installation & Configuration

**Decision**: Instalar Tailwind CSS v3 con PostCSS y Autoprefixer en el frontend.

**Rationale**: Tailwind v3 es estable, ampliamente soportado, y compatible con Vite 8. El prototipo en `src-codigo-modulos/Modulo-Login/Codigo/tailwind.config.js` ya usa Tailwind v3 con tokens personalizados (dark-shade, variable-collection). Se reutiliza esa configuración como base.

**Alternatives considered**:
- Tailwind v4: Muy nuevo, cambios breaking en configuración. Rechazado por riesgo.
- Mantener Bootstrap: Violación directa de constitución v1.2.0 y AGENTS.md.

**Config files to create**:
- `frontend/tailwind.config.js` — content paths, theme extend (colores, fuentes del prototipo)
- `frontend/postcss.config.js` — tailwindcss + autoprefixer plugins
- `frontend/src/index.css` — añadir `@tailwind base; @tailwind components; @tailwind utilities;`

## R2: Bootstrap Coexistence Strategy

**Decision**: Tailwind CSS coexiste con Bootstrap temporalmente. Solo la pantalla de login usa Tailwind. El resto de la app sigue con Bootstrap hasta migración futura.

**Rationale**: La spec limita el alcance al login. Migrar toda la app de Bootstrap a Tailwind está fuera de scope. Tailwind's `preflight` puede resetear estilos de Bootstrap, por lo que se configura `corePlugins: { preflight: false }` en `tailwind.config.js` para evitar conflictos.

**Alternatives considered**:
- Remover Bootstrap completamente: Fuera de scope, alto riesgo de regresiones.
- Usar Tailwind sin preflight: Seguro, no afecta estilos existentes de Bootstrap.

## R3: Login Component Architecture

**Decision**: `Login.tsx` como página contenedor + 2 sub-componentes: `LoginForm.tsx` (formulario) y `TestimonialSection.tsx` (sección lateral).

**Rationale**: Separación de responsabilidades. `LoginForm` maneja state, validación y submit. `TestimonialSection` es presentacional pura. Facilita testing unitario aislado.

**Alternatives considered**:
- Todo en un solo componente: Difícil de testear y mantener.
- Más sub-componentes (orbes, footer): Over-engineering para una pantalla.

## R4: Form Validation Approach

**Decision**: Validación nativa de HTML5 (`required`) + validación de longitud de DNI (8 dígitos) en el handler de submit.

**Rationale**: Sin dependencias externas. HTML5 `required` + `inputMode="numeric"` + `maxLength={8}` cubren los casos. El handler valida antes de llamar `login()`.

**Alternatives considered**:
- react-hook-form: Overkill para 2 campos.
- zod: No justificado para validación simple de presencia y longitud.

## R5: Assets Strategy

**Decision**: Mover las imágenes del prototipo (logo, orbes, línea separadora) a `src/assets/login/`. Importarlas como módulos ES en los componentes.

**Rationale**: Vite optimiza assets importados. Evita referencias a `src-codigo-modulos/`. Las imágenes del prototipo están en `src-codigo-modulos/Modulo-Login/Codigo/` pero no se importan desde ahí; se copian a `src/assets/login/`.

**Alternatives considered**:
- SVG inline en JSX: Viable para orbes y línea. Se usa para elementos decorativos simples.
- CDN: No aplicable en entorno clínico offline.

## R6: Responsive Test Strategy

**Decision**: Tests con vitest + @testing-library/react. Para responsive, se verifica la presencia de clases responsivas de Tailwind (`hidden md:flex`) en el DOM rather than viewport simulation.

**Rationale**: vitest/jsdom no renderiza CSS real. Verificar clases responsivas en el output es suficiente para confirmar el comportamiento. Para validación visual real, se usa `npm run dev` + inspección manual.

**Alternatives considered**:
- Playwright/Cypress: Fuera de scope, no instalado en el proyecto.
- @testing-library/react con resize: Complejo en jsdom, poco confiable.
