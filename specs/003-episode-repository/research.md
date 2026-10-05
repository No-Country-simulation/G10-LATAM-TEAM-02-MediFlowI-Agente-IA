# Technical Research & Decisions: episode_repository

**Feature**: [spec.md](./spec.md) | **Date**: 2026-10-05

---

## 1. Patrón de Conexión y Pool con `asyncpg`

### Decisión
Reutilizar la función centralizada `get_db_pool()` de `backend/app/repositories/postgres_storage.py` con un helper local `_require_pool()` que arroje `DatabaseUnavailableError` cuando el pool de conexiones no esté inicializado.

### Justificación
- Mantiene la consistencia arquitectónica con `patient_repository.py` y `session_repository.py`.
- Previene ejecuciones silenciosas con bases de datos inactivas y protege contra fallos de concurrencia.

### Alternativas Consideradas
- Crear un nuevo pool independiente por repositorio: Descartado porque satura los límites de conexión de PostgreSQL.
- Usar SQLAlchemy ORM asíncrono: Descartado porque el backend de MediFlow utiliza consultas nativas optimizadas con `asyncpg` para máximo rendimiento y control directo de DDL/vistas.

---

## 2. Consulta Detallada: Tabla Base vs Vista SQL `v_episodios_detalle`

### Decisión
Utilizar `v_episodios_detalle` como fuente para todas las consultas de detalle (`get_episode_by_id`, `get_episode_by_code`) y para el listado enriquecido (`list_episodes`), mientras que las mutaciones (`INSERT`, `UPDATE`) se dirigen directamente a la tabla `episodios_clinicos`.

### Justificación
- La vista ya encapsula los `LEFT JOIN` con `pacientes` y `usuarios` (operador, médico general, especialista), así como el cálculo en tiempo real de `paciente_edad` y la concatenación limpia de nombres.
- Simplifica drásticamente el código Python y asegura que cualquier cambio en la proyección relacional esté gobernado por la base de datos.

---

## 3. Generación de Código Clínico de Episodio

### Decisión
Si el diccionario de entrada en `create_episode` no contiene un `codigo_episodio`, generar un código determinista con el formato `EP-{YYYYMMDD}-{HEX4}` (ej. `EP-20261005-A1B2`) utilizando la fecha actual y sufijo aleatorio seguro, garantizando la restricción `UNIQUE`.

### Justificación
- Facilita la ingesta rápida en admisión médica sin obligar al operador a construir un formato manual, al tiempo que permite especificar códigos existentes si provienen de sistemas externos.

---

## 4. Estrategia de Pruebas TDD (Regla de Oro de MediFlow)

### Decisión
Desarrollar una suite en `backend/tests/test_episode_repository.py` utilizando objetos simulados (`unittest.mock.AsyncMock`) que emulen las interfaces de `asyncpg.Pool` y `asyncpg.Connection` (`fetchrow`, `fetch`, `execute`).

### Justificación
- Permite ejecutar las pruebas de manera ultrarrápida en cualquier entorno (incluso sin Docker activo) sin mutar la base de datos `mediflow_dev`.
- Garantiza que la cobertura de código alcance el 100% de las ramas lógicas y manejo de excepciones.
