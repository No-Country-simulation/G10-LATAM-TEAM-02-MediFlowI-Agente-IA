# 12. 🚀 Pull Request #12 — 2026-09-25

Este documento registra los Pull Requests generados el día **2026-09-25** para el proyecto **MediFlow**.

---

## 🔀 12. PR #12 — Módulo 2: Pacientes (RF-06 al RF-09) & Módulo 3: Recepción de Documentos (RF-10) con Migración Alembic, API REST y Buscador Search Select

### 📌 Datos del Pull Request
- **Título del PR**: `feat(patients): Módulo 2 Pacientes (RF-06 a RF-09) y Módulo 3 Recepción (RF-10) con Migración Alembic, API REST y Buscador Search Select`
- **Número de PR**: 12 (PR #12 del día 2026-09-25)
- **Fecha**: 2026-09-25
- **Autor**: Erick Pariona
- **Rama de Origen**: `feature/modulo-pacientes-rf06-rf10`
- **Rama de Destino**: `main`
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal
- **Historial de Cambios Asociado**: [`Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO12.md`](file:///c:/proyectos_git_institutos/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO12.md)

---

### 📋 Resumen del PR
Este PR añade el **Módulo 2: Pacientes** y su acoplamiento con la **Recepción de Documentos (Módulo 3)**. Permite el registro de pacientes sin requerir usuario ni contraseña para el MVP (RF-06), la búsqueda por DNI, Historia Clínica o Nombres/Apellidos (RF-07), la visualización del árbol documental del paciente (RF-08), la conservación inmutable de datos extraídos por la IA (RF-09) y la ingesta/recepción directa precompletada (RF-10). Incluye un buscador interactivo Search Select (`SearchableDocSelect`) con filtrado dinámico exclusivo para documentos sin asociar y la migración de base de datos con comentarios relacionales en PostgreSQL.

---

### 🛠️ Cambios Detallados por Capa Técnica

#### 🗄️ Base de Datos & Migraciones
- Creada migración Alembic `backend/alembic/versions/i2j302266ef8_add_pacientes_table.py` con tabla `pacientes` y FK `paciente_id` en `documentos_triaje`.
- Añadidos comentarios descriptivos en la tabla y en todas las columnas conforme a las reglas del proyecto.

#### ⚙️ Backend & Agente IA
- Implementado repositorio asyncpg `backend/app/repositories/patient_repository.py` con fallback a tienda en memoria para entorno local.
- Endpoints REST en `backend/app/api/v1/patients.py` para registro, búsqueda, consulta de árbol documental y asociación manual.
- Autenticación mediante `get_current_user_or_api_key` para soportar tokens Bearer y API Key.
- Registrado el router en `backend/app/main.py`.

#### 🎨 Frontend & UX
- Cliente API `frontend/src/api/patients.api.ts` con normalización de URL base en `getApiBaseUrl()`.
- Componente `SearchableDocSelect` en `frontend/src/pages/PatientsManagementView.tsx` con sombra `z-index: 1080` y listener de clics externos.
- Modales con encabezado `.modal-header-mediflow` (`linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0284c7 100%)`) y cero guiones em (`—`).
- Registradas las rutas `/pacientes` en `AppRoutes.jsx` e ícono `<FaUserInjured />` en `Sidebar.jsx`.

---

### 🛠️ Archivos Modificados / Creados

| Tipo de Cambio | Ruta del Archivo | Descripción del Cambio |
| :--- | :--- | :--- |
| **Nuevo** | `backend/alembic/versions/i2j302266ef8_add_pacientes_table.py` | Migración Alembic para la tabla `pacientes` y columna `paciente_id`. |
| **Nuevo** | `backend/app/repositories/patient_repository.py` | Repositorio asyncpg con CRUD de pacientes y consultas documentales. |
| **Nuevo** | `backend/app/api/v1/patients.py` | Router REST con endpoints para gestión de pacientes y asociación. |
| **Modificado** | `backend/app/main.py` | Registro del router `patients.router`. |
| **Nuevo** | `frontend/src/api/patients.api.ts` | Cliente API TypeScript para pacientes. |
| **Nuevo** | `frontend/src/pages/PatientsManagementView.tsx` | Vista principal de Pacientes con buscador Search Select y modales. |
| **Modificado** | `frontend/src/App.css` | Clases CSS `.modal-header-mediflow` y `.modal-backdrop-custom`. |
| **Modificado** | `frontend/src/routes/AppRoutes.jsx` | Ruta `/pacientes`. |
| **Modificado** | `frontend/src/components/layout/Sidebar.jsx` | Ícono y elemento del menú Pacientes. |

---

### 🏆 Checklist de la Regla de Oro
- [x] **PostgreSQL es la Fuente Única de Verdad**: Persistencia garantizada en `mediflow_dev`.
- [x] **Control 100% Manual de Almacenamiento**: Almacenamiento `LOCAL` vs `OCI` controlado manualmente por el usuario.
- [x] **Pruebas Backend Passing**: Verificación con `python -m py_compile` exitosa sin errores.
- [x] **Compilación Frontend Limpia**: `npm run build` ejecutado sin errores de TypeScript (0ms/0 errors).
- [x] **Migraciones Alembic Sincronizadas**: Tabla `pacientes` y comentarios relacionales migrados.

---

### 🧪 Verificación y Pruebas
1. `python -m py_compile backend/app/main.py backend/app/api/v1/patients.py backend/app/repositories/patient_repository.py`
2. `cd frontend && npm run build`
