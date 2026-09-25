# 🚀 Guía de Ejecución Local de MediFlow (Sin Docker)

Esta guía detalla los pasos para levantar el proyecto **MediFlow (Backend FastAPI + Frontend React + Base de Datos PostgreSQL 17)** directamente en el sistema operativo local sin utilizar contenedores Docker.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instaladas las siguientes herramientas en tu máquina local:

1. **Python 3.11+** (verificar con `python --version`).
2. **Node.js 18+ y npm** (verificar con `node -v` y `npm -v`).
3. **PostgreSQL 17** instalado y corriendo como servicio en `localhost:5432`.
4. **Git** (para clonación y gestión del repositorio).

---

## 🗄️ Paso 1: Configurar la Base de Datos PostgreSQL Local

1. Abrir la terminal SQL (`psql`) o tu cliente preferido (pgAdmin, DBeaver, TablePlus).
2. Conectarte a tu instancia local de PostgreSQL y crear la base de datos de desarrollo `mediflow_dev`:
   ```sql
   CREATE DATABASE mediflow_dev;
   ```
3. Verificar las credenciales de tu usuario local de PostgreSQL (por defecto usuario `postgres`, contraseña `postgres` o la configurada durante tu instalación).

---

## ⚙️ Paso 2: Configurar y Levantar el Backend (FastAPI & Python)

1. Abrir una terminal y navegar al directorio del backend:
   ```bash
   cd backend
   ```

2. Crear y activar el entorno virtual de Python (`.venv`):
   - **En Windows (PowerShell / CMD)**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **En Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Instalar el paquete backend y sus dependencias en modo editable:
   ```bash
   pip install --upgrade pip
   pip install -e .[dev]
   ```

4. Crear el archivo de variables de entorno `.env` dentro de la carpeta `backend/`:
   ```env
   APP_ENV=development
   LOG_LEVEL=INFO
   API_KEY=mediflow-dev-secret-key-change-in-prod
   
   # Conexión a la Base de Datos PostgreSQL local
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mediflow_dev
   
   # Credenciales LLM (Google Gemini)
   GOOGLE_API_KEY=tu_gemini_api_key_aqui
   GEMINI_MODEL=gemini-1.5-flash
   ```

5. Aplicar las migraciones de la base de datos con **Alembic**:
   ```bash
   alembic upgrade head
   ```

6. Iniciar el servidor ASGI FastAPI con **Uvicorn**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

7. **Verificación**:
   - Backend API corriendo en: `http://localhost:8000`
   - Documentación Interactiva (Swagger UI): `http://localhost:8000/docs`
   - Endpoint de salud: `http://localhost:8000/api/v1/health`

---

## 🎨 Paso 3: Configurar y Levantar el Frontend (React + Vite)

1. Abrir una **nueva terminal** y navegar a la carpeta `frontend/`:
   ```bash
   cd frontend
   ```

2. Instalar los paquetes de Node.js:
   ```bash
   npm install
   ```

3. Crear el archivo `.env` en la carpeta `frontend/` (opcional, por defecto apunta a localhost:8000):
   ```env
   VITE_API_URL=http://localhost:8000/api/v1
   ```

4. Iniciar el servidor de desarrollo de Vite:
   ```bash
   npm run dev
   ```

5. **Verificación**:
   - Aplicación Frontend disponible en: `http://localhost:5173`

---

## ⚡ Paso 4: Ejecución Rápida mediante Makefile (Opcional)

Si utilizas `make` en tu terminal local, puedes ejecutar todo el stack sin Docker con un solo comando:

```bash
make dev
```

Este comando instalará las dependencias necesarias y abrirá las ventanas de terminal para el backend (`http://localhost:8000`) y frontend (`http://localhost:5173`).

---

## 🧪 Paso 5: Verificación de Pruebas y Compilación (Regla de Oro)

Para asegurarte de que tu entorno local cumple con los estándares del proyecto antes de subir cambios:

1. **Ejecutar Pruebas Backend (`pytest`)**:
   ```bash
   cd backend
   python -m pytest tests
   ```
   *(Debe reportar 100% pasados sin alterar los datos reales de `mediflow_dev`)*

2. **Verificar Compilación del Frontend (`tsc` + `vite build`)**:
   ```bash
   cd frontend
   npm run build
   ```
   *(Debe compilar limpiamente con 0 errores de TypeScript)*
