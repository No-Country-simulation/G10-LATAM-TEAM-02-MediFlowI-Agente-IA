# 📜 Historial de Cambios — 2026-09-25 (CAMBIO6)

**Fecha**: 2026-09-25  
**Identificador de Cambio**: CAMBIO6  
**Autor**: Erick Pariona  
**Sprint / Fase**: Rediseño UX/UI — Formulario de Registro de Usuarios & Tabla RBAC  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
Se realizó un rediseño profundo del formulario de registro de nuevos usuarios (`RF-03`) y la tabla de usuarios registrados (`RF-04`) dentro del módulo de **Gestión de Usuarios**. Se corrigió la alineación de etiquetas (`labels`), el diseño de los campos de entrada (`password`, `email`, `text`, `select`), y el estilo de los botones de acción (`Activar`/`Desactivar` y `Cambiar Rol`).

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🎨 1. Frontend & UX (React / Vite / TypeScript / CSS)
1. **Alineación y Maquetación del Formulario (`RF-03`)**:
   - Forzada la alineación a la izquierda (`text-align: left !important`) para todas las etiquetas (`labels`), inputs y selectores del formulario de creación de usuarios.
   - Añadidos estilos específicos para `input[type='password']` y `input[type='email']`, otorgando bordes consistentes (`1px solid #cbd5e1`), bordes redondeados (`8px`) y ancho completo (`width: 100%`).
2. **Tabla de Usuarios Registrados (`RF-04`)**:
   - Estilizado de la cabecera de la tabla con fondo gris suave (`#f8fafc`), tipografía en mayúsculas pequeñas (`11px`) y espaciado consistente.
   - Rediseño de los botones de cambio de estado:
     - Botón `Desactivar`: Tono suave rojizo (`#fef2f2`) con borde y texto en bordó.
     - Botón `Activar`: Tono verde esmeralda suave (`#f0fdf4`) con borde y texto verde clínico.
   - Estilizado de los selectores de cambio de rol (`.select-role-change`) con bordes redondeados y tipografía en negrita.

### 🐳 2. Infraestructura & Documentación
- **Documentación de Auditoría**: Generados `HISTORIAL_CAMBIOS_2026-09-25_CAMBIO6.md` y `PULL_REQUEST_2026-09-25_PR6.md`.

---

## 🧪 Verificación y Pruebas
- **Backend (Pytest)**: `21 passed in 1.21s` (100% passing).
- **Frontend (TypeScript / Vite)**: `npm run build` compilación limpia en **338ms** con 0 errores.
- **Migraciones (Alembic)**: `alembic upgrade head` sincronizado en `h1i202255de7`.
