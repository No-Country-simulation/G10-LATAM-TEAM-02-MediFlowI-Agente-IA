# 📜 Historial de Cambios — [AAAA-MM-DD]

**Fecha**: [DD/MM/AAAA] *(Fecha generada automáticamente por el Agente)*  
**Autor**: [Nombre del Autor]  
**Sprint / Fase**: [Número o Nombre de la Fase]  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
[Breve descripción del alcance y objetivos de los cambios realizados en la jornada.]

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🗄️ 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)
1. **[Nombre del cambio / Migración]** (`[archivo_o_migracion.py]`):
   - **SQL / DDL**: [Sentencia SQL o cambio exacto en tablas, columnas o FK/UNIQUE/CHECK.]
   - **Propósito**: [Explicación técnica de la necesidad del cambio.]

### ⚙️ 2. Backend & Agente IA (FastAPI / LangGraph / Python)
2. **[Nombre del servicio o endpoint]** (`[ruta/archivo.py]`):
   - **Cambio técnico**: [Funciones creadas/modificadas, parámetros Pydantic, lógica de negocio o nodos de LangGraph.]

### 🎨 3. Frontend & UX (React / Vite / TypeScript / CSS)
3. **[Nombre del componente o interfaz]** (`[ruta/Componente.tsx]`):
   - **Cambio de UI / Estado**: [Estados de React, props, clases CSS, llamadas API en triage.api.ts.]

### 🐳 4. Infraestructura, Scripts & Documentación
4. **[Nombre del script o configuración]** (`[ruta/archivo]`):
   - **Configuración**: [Modificaciones en Docker Compose, Makefile, .gitignore o documentación.]

---

## 🧪 Verificación y Pruebas
- **Backend (Pytest)**: `[Resultado de pytest]`
- **Frontend (TypeScript)**: `[Resultado de npm run build]`
- **Migraciones (Alembic)**: `[Estado de alembic upgrade head]`
