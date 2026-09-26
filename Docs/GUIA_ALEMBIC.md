# ⚗️ Guía de Uso de Alembic en MediFlow

Esta guía detalla para los desarrolladores del equipo **MediFlow** cómo gestionar las migraciones de la base de datos PostgreSQL (`mediflow_dev`) tanto de **forma manual (CLI / Consola)** como de **forma automática (Makefile / Docker)**.

---

## 📌 ¿Qué es Alembic y cómo se usa en MediFlow?

En MediFlow, **Alembic** es la herramienta oficial de control de versiones y migraciones para PostgreSQL. Permite actualizar la estructura de las tablas (`documentos_triaje`, `configuracion_sistema`, etc.) de forma controlada, reversible y sincronizada entre los entornos de desarrollo local y producción.

- **Archivo de configuración**: `backend/alembic.ini`
- **Script de entorno**: `backend/alembic/env.py`
- **Directorio de versiones**: `backend/alembic/versions/`
- **Base de datos objetivo**: PostgreSQL 17 (`mediflow_dev` en `localhost:5432`)

---

## 💻 1. FORMA MANUAL: Ejecución por Línea de Comandos (CLI)

El uso manual se realiza directamente desde la terminal del sistema dentro del directorio `backend/` activando el entorno virtual de Python (`.venv`).

### A. Preparar la Terminal (Modo Manual)

```bash
# 1. Posicionarse en la carpeta backend
cd backend

# 2. Activar el entorno virtual de Python
# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# En Linux / macOS:
source .venv/bin/activate

# 3. Asegurar que las dependencias estén instaladas
pip install -e .
```

---

### B. Comandos Manuales de Aplicación y Control

#### 1. Aplicar la última migración disponible (Manual)
Aplica todas las migraciones pendientes hasta dejar la base de datos en la última versión (`head`):
```bash
alembic upgrade head
```

#### 2. Avanzar de a una migración (Paso a paso)
Aplica solo la siguiente migración pendiente:
```bash
alembic upgrade +1
```

#### 3. Revertir la última migración (Downgrade Manual)
Deshace únicamente la última migración aplicada en la base de datos:
```bash
alembic downgrade -1
```

#### 4. Revertir todas las migraciones (Base cero)
Regresa la base de datos al estado inicial antes de cualquier migración:
```bash
alembic downgrade base
```

#### 5. Consultar el estado actual de la base de datos
Muestra el ID de la migración actualmente activa en PostgreSQL:
```bash
alembic current
```

#### 6. Ver el historial de revisiones registradas
Muestra el árbol cronológico de todas las migraciones creadas:
```bash
alembic history --verbose
```

---

### C. Crear una Nueva Migración Manualmente

Cuando un desarrollador añade o modifica tablas en PostgreSQL, debe crear una nueva revisión manual:

```bash
cd backend

# Generar el archivo de migración
alembic revision -m "descripcion_del_cambio"
```

Esto creará un nuevo archivo Python en `backend/alembic/versions/` (ej: `g9h001143cd6_descripcion_del_cambio.py`).

El desarrollador edita el archivo definiendo la lógica en `upgrade()` y `downgrade()`:

```python
"""descripcion_del_cambio

Revision ID: g9h001143cd6
Revises: f8g990032bc5
Create Date: 2026-09-24 22:30:00

"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    """Modificación manual a aplicar."""
    op.execute("""
    ALTER TABLE documentos_triaje 
    ADD COLUMN mi_nueva_columna VARCHAR(255);
    """)

def downgrade() -> None:
    """Reverso manual de la modificación."""
    op.execute("""
    ALTER TABLE documentos_triaje 
    DROP COLUMN IF EXISTS mi_nueva_columna;
    """)
```

Finalmente, aplica la migración manualmente:
```bash
alembic upgrade head
```

---

## 🐳 2. FORMA MANUAL EN DOCKER (Contenedores)

Si PostgreSQL o el backend están corriendo en contenedores Docker, también se puede ejecutar Alembic manualmente dentro del contenedor:

```bash
# Ejecución manual de Alembic dentro del contenedor de backend
docker compose -f infrastructure/docker/docker-compose.dev.yml exec backend alembic upgrade head
```

---

## ⚡ 3. FORMA AUTOMÁTICA (Makefile)

Para mayor comodidad durante el desarrollo diario desde la raíz del proyecto:

```bash
# Levanta la base de datos PostgreSQL 17 en Docker
make db

# Ejecuta automáticamente alembic upgrade head
make migrate
```

---

## 🏆 Buenas Prácticas para el Equipo

1. **Commit obligatorio de migraciones**: Todo archivo creado en `backend/alembic/versions/` **debe subirse a Git**.
2. **Nunca editar migraciones ya compartidas**: Si una migración ya está en `main` o `develop`, crea una nueva revisión arriba.
3. **Ejecutar `alembic upgrade head` tras `git pull`**: Garantiza que tu base de datos local tenga las últimas columnas creadas por tus compañeros.
