# ⚗️ Guía de Uso de Alembic en MediFlow

Esta guía explica a los desarrolladores del equipo **MediFlow** cómo gestionar las migraciones de la base de datos PostgreSQL (`mediflow_dev`) utilizando **Alembic**.

---

## 📌 ¿Qué es Alembic y cómo se usa en MediFlow?

En MediFlow, **Alembic** es la herramienta oficial de migraciones para PostgreSQL. Permite actualizar la estructura de las tablas (`documentos_triaje`, `configuracion_sistema`, etc.) de forma controlada, reversible y sincronizada entre todos los miembros del equipo y los entornos de Docker.

- **Ubicación de la configuración**: `backend/alembic.ini`
- **Ubicación de las migraciones**: `backend/alembic/versions/`
- **Base de datos objetivo**: PostgreSQL 17 (`mediflow_dev`)

---

## 🚀 Requisitos Previos

Asegúrate de estar en el entorno virtual del backend o haber instalado el proyecto:

```bash
# Desde el directorio raíz del proyecto
cd backend
# O instalar dependencias
pip install -e .
```

Si usas la consola en la raíz del proyecto, puedes utilizar directamente los comandos simplificados del **Makefile**:

```bash
make db       # Levanta PostgreSQL 17 + pgAdmin en Docker
make migrate  # Aplica todas las migraciones pendientes con Alembic
```

---

## 🛠️ Comandos Frecuentes para el Equipo

### 1. 🔄 Aplicar migraciones pendientes (Tras hacer `git pull`)

Cuando bajes cambios del repositorio que incluyan nuevas migraciones creadas por otros compañeros, ejecuta:

```bash
# Opción A: Usando Makefile desde la raíz
make migrate

# Opción B: Ejecutando directamente en la carpeta backend
cd backend
alembic upgrade head
```

---

### 2. 📍 Verificar la versión actual de la Base de Datos

Para consultar en qué migración se encuentra tu base de datos local y verificar si estás al día con `head`:

```bash
cd backend

# Muestra la versión aplicada en tu BD local
alembic current

# Muestra la última versión disponible en el código
alembic heads
```

---

### 3. ➕ Crear una nueva migración

Cuando necesites agregar una nueva tabla, nueva columna o modificar restricciones:

```bash
cd backend
alembic revision -m "nombre_descriptivo_del_cambio"
```

Esto generará un archivo Python en `backend/alembic/versions/` (ej. `f8g990032bc5_nombre_descriptivo_del_cambio.py`).

Abre el archivo generado y define las operaciones en la función `upgrade()` y su reverso en `downgrade()`:

```python
"""nombre_descriptivo_del_cambio

Revision ID: f8g990032bc5
Revises: g9h001143cd6
Create Date: 2026-09-24 22:30:00

"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    """Aplica la modificación."""
    op.execute("""
    ALTER TABLE documentos_triaje 
    ADD COLUMN mi_nueva_columna VARCHAR(255);
    """)

def downgrade() -> None:
    """Revierte la modificación."""
    op.execute("""
    ALTER TABLE documentos_triaje 
    DROP COLUMN IF EXISTS mi_nueva_columna;
    """)
```

---

### 4. ⏪ Revertir la última migración (Downgrade)

Si necesitas deshacer la última migración aplicada en tu base de datos local:

```bash
cd backend
alembic downgrade -1
```

O revertir hasta una revisión específica:

```bash
cd backend
alembic downgrade <revision_id>
```

---

## 🏆 Buenas Prácticas para el Equipo

1. **Siempre subir las migraciones a Git**:
   - Todo archivo creado en `backend/alembic/versions/` **debe ser enviado en tus commits**. Nunca los agregues al `.gitignore`.
2. **No modificar migraciones ya fusionadas**:
   - Si una migración ya fue subida a la rama `develop` o `main`, **no modifiques ese archivo**. Crea una nueva migración para realizar correcciones sobre el schema.
3. **Ejecutar `make migrate` tras cada `git pull`**:
   - Acostúmbrate a correr `make migrate` (o `alembic upgrade head`) para asegurarte de que tu PostgreSQL local tenga todas las columnas que el código del backend espera.
4. **Incluir comentarios SQL en las tablas**:
   - Si creas una nueva tabla o columna, incluye sentencias `COMMENT ON TABLE` y `COMMENT ON COLUMN` dentro de la función `upgrade()`.
