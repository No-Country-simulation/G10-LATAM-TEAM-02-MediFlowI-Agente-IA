# 📋 Plan de Trabajo Operativo: Backend, LangGraph y Base de Datos (MediFlow)

Este plan de trabajo está diseñado para un equipo de **6 personas** enfocado exclusivamente en **Backend**, **Base de Datos** y el **Agente IA (LangGraph)**. Las tareas han sido desglosadas en unidades **pequeñas, atómicas y fáciles de ejecutar**, indicando con total precisión cómo realizarlas tanto de forma **Manual** como mediante **Spec Kit (`/specify`)**.

---

## 🚀 0. Cómo Ver y Testear la API con Scalar

Antes de iniciar cualquier desarrollo, todos los miembros del equipo deben verificar que pueden levantar la API y explorarla interactivamente con **Scalar**.

### Paso 1: Levantar el Backend
Elige una de las dos formas:
- **Opción A (Local con Python)**:
  ```powershell
  cd backend
  .venv\Scripts\uvicorn app.main:app --reload --port 8000
  ```
- **Opción B (Docker Compose)**:
  ```powershell
  docker compose -f infrastructure/docker/docker-compose.dev.yml up -d backend db
  ```

### Paso 2: Abrir la Documentación Interactiva Scalar
Abre tu navegador en:
👉 **[http://localhost:8000/scalar](http://localhost:8000/scalar)**

*(También dispones de Swagger tradicional en `http://localhost:8000/docs` y el esquema crudo en `http://localhost:8000/openapi.json`).*

### Paso 3: Probar un Endpoint en Vivo desde Scalar
1. En Scalar, haz clic en **Authorize** (o botón de candado / autenticación superior).
2. Para pruebas locales de desarrollo, introduce uno de los siguientes tokens Bearer preconfigurados:
   - **Administrador**: `test-admin-token`
   - **Coordinador Médico**: `test-coordinador-token`
   - **Operador de Admisión**: `test-operator-token`
3. Navega a `GET /api/v1/patients` o `POST /api/v1/patients`.
4. Haz clic en **Test Request / Send**, envía el payload y verifica que recibes respuesta `200 OK` o `201 Created` en formato JSON.

---

## 👥 Asignación del Equipo (6 Personas)

| Rol / Especialidad | Responsables | Enfoque Principal |
|---|---|---|
| **Base de Datos & Persistencia** | Persona 1 & Persona 2 | Migraciones Alembic, asyncpg, triggers, vistas y repositorios relacionales |
| **Agente Autónomo LangGraph & IA** | Persona 3 & Persona 4 | Nodos del grafo, extracción multimodal, enrutamiento, CIE-10 y confianza |
| **Backend Core & APIs FastAPI** | Persona 5 & Persona 6 | Endpoints REST, RBAC, servicios clínicos, contratos OpenAPI y validaciones |

---

## 🗄️ Bloque 1: Base de Datos & Repositorios (Personas 1 y 2)

### Tarea 1.1: Vistas y Funciones de Consulta para `episodios_clinicos`
- **Asignado**: Persona 1 (DBA / Data Engineer)
- **Objetivo**: Crear la vista `v_episodios_detalle` que une pacientes, médicos asignados y documentos de triaje para consultas rápidas sin múltiples joins.
- **🛠️ Ejecución MANUAL**:
  1. Crear archivo de migración Alembic en `backend/alembic/versions/`:
     ```powershell
     cd backend
     .venv\Scripts\alembic revision -m "add_episodios_view"
     ```
  2. Escribir el `CREATE VIEW v_episodios_detalle AS SELECT ...` uniendo `episodios_clinicos`, `pacientes`, y `usuarios`.
  3. Probar migración offline:
     ```powershell
     .venv\Scripts\alembic upgrade head --sql
     ```
  4. Crear test unitario en `backend/tests/test_episodios_db.py`.
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  Escribir en el chat de Antigravity:
  ```text
  /speckit-specify Crear vista SQL v_episodios_detalle en PostgreSQL mediante migración Alembic para relacionar episodios, paciente y médico asignado
  ```
  Seguido de:
  ```text
  /speckit-implement
  ```

---

### Tarea 1.2: Repositorio Asíncrono `episode_repository.py`
- **Asignado**: Persona 2 (Backend / Database)
- **Objetivo**: Crear métodos CRUD con `asyncpg` para registrar, buscar por código y actualizar el estado de episodios clínicos (`ingresado`, `en_triaje`, `atendido`, `derivado`).
- **🛠️ Ejecución MANUAL**:
  1. Crear `backend/app/repositories/episode_repository.py`.
  2. Implementar funciones:
     - `create_episode(data: dict) -> dict`
     - `get_episode_by_id(episode_id: str) -> dict | None`
     - `update_episode_status(episode_id: str, nuevo_estado: str) -> bool`
     - `list_episodes(estado: str | None = None) -> list[dict]`
  3. Manejar `DatabaseUnavailableError` si el pool no responde.
  4. Ejecutar validación de pruebas:
     ```powershell
     .venv\Scripts\pytest tests/test_episode_repository.py -v
     ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Implementar repositorio asíncrono episode_repository con asyncpg para gestionar la tabla episodios_clinicos
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 1.3: Repositorio de Trazabilidad y Auditoría Coordinación
- **Asignado**: Persona 1 (DBA / Data Engineer)
- **Objetivo**: Centralizar la inserción inmutable de eventos en `trazabilidad_eventos` y auditorías en `auditorias_coordinacion`.
- **🛠️ Ejecución MANUAL**:
  1. Crear `backend/app/repositories/audit_repository.py`.
  2. Implementar:
     - `registrar_evento_trazabilidad(episodio_id, documento_id, usuario_id, evento, descripcion, metadata)`
     - `registrar_auditoria_coordinacion(episodio_id, documento_id, coordinador_id, decision, justificacion)`
  3. Asegurar que las consultas usen parámetros `$1, $2, ...` para evitar SQL Injection.
  4. Verificar con tests unitarios mockeando el connection pool.
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Crear audit_repository para persistir eventos inmutables en trazabilidad_eventos y decisiones en auditorias_coordinacion
  /speckit-implement
  ```

---

### Tarea 1.4: Script de Datos Semilla Clínicos (`seed_data.py`)
- **Asignado**: Persona 2 (Backend / Database)
- **Objetivo**: Crear script para poblar la BD de desarrollo con 10 pacientes de prueba, 4 médicos con distintas especialidades y 5 documentos con diferentes severidades (Rojo, Amarillo, Verde).
- **🛠️ Ejecución MANUAL**:
  1. Crear `backend/app/scripts/seed_hospital_data.py`.
  2. Usar passwords hasheadas mediante `app.core.security.hash_password`.
  3. Añadir comando en `backend/pyproject.toml` o ejecutar directo con `.venv\Scripts\python -m app.scripts.seed_hospital_data`.
  4. Verificar visualmente en Scalar (`GET /api/v1/patients`) los datos insertados.
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Crear script de seed data hospitalario para pruebas de triaje con pacientes y médicos de urgencias
  /speckit-implement
  ```

---

## 🧠 Bloque 2: Agente Autónomo LangGraph & AI Clínica (Personas 3 y 4)

### Tarea 2.1: Enrutamiento Formal a `Farmacia_Hospitalaria` en LangGraph
- **Asignado**: Persona 3 (AI / LangGraph Engineer)
- **Objetivo**: Añadir la lógica clínica en el nodo `routing` para derivar automáticamente casos de prescripciones de medicamentos crónicos o dispensación prioritaria hacia `Farmacia_Hospitalaria`.
- **🛠️ Ejecución MANUAL**:
  1. Abrir `backend/app/agent/nodes/routing.py`.
  2. En la función `_calcular_destino()`, incorporar la regla:
     - Si el tipo de documento es `receta_medica` o si el diagnóstico sugiere farmacoterapia exclusiva sin descompensación aguda -> `Farmacia_Hospitalaria`.
  3. Asegurar que `requiere_auditoria_humana = False` para recetas estándar y `True` si contiene medicamentos controlados/narcóticos.
  4. Ejecutar pruebas unitarias del nodo:
     ```powershell
     .venv\Scripts\pytest tests/test_destinos_triaje_unit.py -v
     ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Actualizar nodo de enrutamiento en routing.py para derivar recetas y farmacoterapia hacia Farmacia_Hospitalaria
  /speckit-implement
  ```

---

### Tarea 2.2: Nodo de Resolución de Identidad y Conflictos DNI/HC
- **Asignado**: Persona 4 (AI / Data Engineer)
- **Objetivo**: Enriquecer el nodo `extraction` para comparar los identificadores extraídos en el documento con la base de datos de pacientes y detectar discrepancias.
- **🛠️ Ejecución MANUAL**:
  1. Abrir `backend/app/agent/nodes/extraction.py` o crear `backend/app/agent/nodes/patient_matcher.py`.
  2. Invocar `resolver_paciente_por_identificadores(dni, hc)`.
  3. Si el estado es `conflicto`:
     - Asignar destino `Cola_Revision_Ambigua`.
     - Activar `requiere_auditoria_humana = True`.
     - Notificar en metadata: `"discrepancia_identidad_detectada"`.
  4. Ejecutar tests:
     ```powershell
     .venv\Scripts\pytest tests/test_agent_cases.py -v
     ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Añadir verificación de coincidencia de DNI y HC en el pipeline del agente para derivar conflictos a Cola_Revision_Ambigua
  /speckit-implement
  ```

---

### Tarea 2.3: Validación y Normalización de Códigos CIE-10
- **Asignado**: Persona 3 (AI / LangGraph Engineer)
- **Objetivo**: Validar que los códigos CIE-10 sugeridos por el LLM pertenezcan al catálogo clínico oficial (`clinical_catalog.py`) y asignar descripción formal en caso de variaciones sintácticas.
- **🛠️ Ejecución MANUAL**:
  1. Revisar `backend/app/agent/clinical_catalog.py`.
  2. Implementar `validar_y_completar_cie10(codigo: str) -> dict`.
  3. Integrar en `backend/app/agent/nodes/extraction.py` antes de escribir en el estado.
  4. Comprobar con test:
     ```powershell
     .venv\Scripts\pytest tests/test_clinical_catalog.py -v
     ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Validar códigos CIE-10 sugeridos por el agente contra el catálogo oficial en clinical_catalog.py
  /speckit-implement
  ```

---

### Tarea 2.4: Calibrador de Score de Confianza Multimodal
- **Asignado**: Persona 4 (AI / Data Engineer)
- **Objetivo**: Ajustar el cálculo del score de confianza en `backend/app/agent/nodes/confidence.py` considerando: legibilidad del OCR/imagen, completitud de signos vitales y concordancia diagnóstica.
- **🛠️ Ejecución MANUAL**:
  1. Abrir `backend/app/agent/nodes/confidence.py`.
  2. Si el score resultante es `< 0.75`, marcar bandera `score_bajo` y derivar a `Cola_Auditoria_Humana`.
  3. Validar con fixtures sintéticas con texto ilegible o incompleto.
  4. Ejecutar suite de pruebas:
     ```powershell
     .venv\Scripts\pytest tests/test_sdd_pipeline.py -v
     ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Calibrar cálculo de score de confianza en confidence.py para retener casos con confianza menor a 0.75
  /speckit-implement
  ```

---

## ⚡ Bloque 3: Backend REST APIs & Servicios (Personas 5 y 6)

### Tarea 3.1: Endpoints de Gestión de Episodios Clínicos (`/api/v1/episodes`)
- **Asignado**: Persona 5 (Backend Engineer)
- **Objetivo**: Exponer endpoints REST en FastAPI para crear, listar y consultar el detalle de episodios clínicos, documentados en OpenAPI y probables en Scalar.
- **🛠️ Ejecución MANUAL**:
  1. Crear `backend/app/api/v1/episodes.py`.
  2. Definir Pydantic models: `EpisodeCreateRequest`, `EpisodeResponse`.
  3. Endpoints:
     - `POST /api/v1/episodes/` (Crear nuevo episodio clínico).
     - `GET /api/v1/episodes/` (Listar episodios filtrando por estado o prioridad).
     - `GET /api/v1/episodes/{id}` (Obtener detalle completo).
  4. Incluir el router en `backend/app/main.py`.
  5. Verificar en Scalar: `http://localhost:8000/scalar` sección "Episodios Clínicos".
  6. Crear `backend/tests/test_episodes_api.py` y correr:
     ```powershell
     .venv\Scripts\pytest tests/test_episodes_api.py -v
     ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Crear endpoints REST /api/v1/episodes en FastAPI para ciclo de vida de atención médica hospitalaria
  /speckit-plan
  /speckit-tasks
  /speckit-implement
  ```

---

### Tarea 3.2: Endpoint de Auditoría Médica Exclusiva para Coordinador (`/api/v1/coordination`)
- **Asignado**: Persona 6 (Backend Engineer)
- **Objetivo**: Crear endpoint especializado donde el `COORDINADOR` visualiza la lista de casos pendientes de HITL con filtros por especialidad y tiempo de espera.
- **🛠️ Ejecución MANUAL**:
  1. Crear `backend/app/api/v1/coordination.py`.
  2. Proteger con `Depends(require_roles("COORDINADOR", "ADMINISTRADOR"))`.
  3. Implementar:
     - `GET /api/v1/coordination/pending` (Bandeja exclusiva de triajes por auditar).
     - `POST /api/v1/coordination/resolve/{documento_id}` (Resolución médica con reasignación).
  4. Vincular con `audit_repository.py`.
  5. Probar con token `test-coordinador-token` en Scalar y verificar que `test-operator-token` recibe `403 Forbidden`.
  6. Crear test en `backend/tests/test_coordination_api.py`.
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Implementar endpoints /api/v1/coordination exclusivos para rol COORDINADOR con resolución médica y reasignación
  /speckit-implement
  ```

---

### Tarea 3.3: Orquestación Servicio de Triaje con Creación Automática de Episodio
- **Asignado**: Persona 5 (Backend Engineer)
- **Objetivo**: Al procesar un documento en `triage_service.py`, si el paciente existe y no tiene un episodio activo, generar automáticamente un registro en `episodios_clinicos` y vincular el `documento_id`.
- **🛠️ Ejecución MANUAL**:
  1. Abrir `backend/app/services/triage_service.py`.
  2. Tras ejecutar el grafo LangGraph, invocar `episode_repository.create_episode(...)`.
  3. Asignar el `episodio_id` generado a la tabla `documentos_triaje`.
  4. Registrar evento en `trazabilidad_eventos` con tipo `"DOCUMENTO_ASOCIADO_A_EPISODIO"`.
  5. Correr suite E2E:
     ```powershell
     .venv\Scripts\pytest tests/test_e2e_hospital_flow.py -v
     ```
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Integrar triage_service con episode_repository para vincular automáticamente cada triaje a un episodio clínico
  /speckit-implement
  ```

---

### Tarea 3.4: Endpoint de Métricas Hospitalarias y SLA de Triaje (`/api/v1/metrics`)
- **Asignado**: Persona 6 (Backend Engineer)
- **Objetivo**: Exponer métricas de rendimiento clínico: tiempo promedio de clasificación por IA, cantidad de pacientes por color de triaje (Rojo, Amarillo, Verde) y tasa de revisión HITL.
- **🛠️ Ejecución MANUAL**:
  1. Crear `backend/app/api/v1/metrics.py`.
  2. Implementar consulta agregada SQL con `asyncpg` sobre `documentos_triaje` y `auditorias_coordinacion`.
  3. Retornar JSON con:
     - `distribucion_prioridad`: conteos por color.
     - `tasa_hitl`: porcentaje de casos que requirieron revisión.
     - `tiempo_promedio_ia_segundos`: promedio de ejecución de nodos.
  4. Probar en Scalar `GET /api/v1/metrics`.
  5. Crear prueba unitaria en `backend/tests/test_metrics_api.py`.
- **⚡ Ejecución con Spec Kit (`/specify`)**:
  ```text
  /speckit-specify Crear endpoint /api/v1/metrics para exponer estadísticas hospitalarias de triaje, distribución de prioridades y tasa HITL
  /speckit-implement
  ```

---

## 🛡️ Reglas de Oro para Todo el Equipo

1. **Constitución de MediFlow Obligatoria**:
   - Todo cambio debe pasar **100% de pruebas en verde** (`pytest -q`) antes de considerar la tarea terminada.
   - Si tienes dudas sobre un parámetro o regla clínica: **PREGUNTA SIEMPRE** antes de asumir.
2. **Pruebas en Scalar**:
   - Cada nuevo endpoint debe probarse inmediatamente en **`http://localhost:8000/scalar`** con los tokens de prueba.
3. **Cero Secretos en el Repositorio**:
   - Revisa la [Guía Oficial de Seguridad](../GUIA_SECRETOS_Y_VARIABLES_ENTORNO.md) antes de cada commit.

## Backlog de mejoras futuras

- **BD-04 — Entrega automatizada de credenciales de desarrollo (propuesta diferida, 2026-10-07)**: evaluar generación criptográficamente aleatoria de claves únicamente para médicos nuevos y entrega única mediante un mecanismo privado, fuera del repositorio y sin secretos en logs. Referencia: [backlog BD-04, issue #27](https://github.com/No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/issues/27).
  - **Pendiente de revisión de seguridad y aprobación explícita**: evaluar gestor de secretos frente a archivo local, permisos/ACL, persistencia en Docker, recuperación/eliminación y consistencia ante fallos; conservar `hash_password`, idempotencia y prohibición de rotar claves existentes. Cualquier excepción sobre contraseñas en claro o archivos requiere revisar previamente los requisitos SDD afectados.
  - **Sin implementación ni cambio de alcance actual**: BD-04 mantiene las cuatro contraseñas introducidas de forma oculta y el soporte existente de variables de entorno. Esta nota no autoriza TXT, generación automática, cambios de código/spec ni carga en `mediflow_dev`; no constituye aceptación de T036–T039.
