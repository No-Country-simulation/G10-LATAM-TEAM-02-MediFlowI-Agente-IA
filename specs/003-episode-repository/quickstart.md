# Quickstart & Validation Guide: episode_repository

**Feature**: [spec.md](./spec.md) | **Date**: 2026-10-05

---

## 1. Prerrequisitos
- Entorno virtual de Python activo en `backend/.venv`.
- Dependencias `pytest`, `pytest-asyncio`, `asyncpg`, `structlog` instaladas.

---

## 2. Ejecución de Pruebas Unitarias TDD

Para validar el repositorio sin depender de un servidor PostgreSQL externo ni mutar datos:

```bash
pytest backend/tests/test_episode_repository.py -v
```

### Escenarios Verificados por la Suite:
1. `test_create_episode_success`: Inserción correcta con auto-generación de código `EP-YYYYMMDD-XXXX`.
2. `test_create_episode_database_error`: Manejo de fallo en pool arrojando `DatabaseUnavailableError`.
3. `test_get_episode_by_id_found`: Búsqueda exitosa mapeando columnas de `v_episodios_detalle`.
4. `test_get_episode_by_id_not_found`: Retorno `None` cuando el episodio no existe.
5. `test_get_episode_by_code`: Búsqueda por código de episodio clínico.
6. `test_update_episode_status_valid`: Transición de estado (`ingresado` -> `en_triaje`).
7. `test_update_episode_status_invalid_state`: Rechazo con `ValueError` ante estados inexistentes.
8. `test_assign_doctor_general_and_specialist`: Asignación adecuada según rol y especialidad.
9. `test_list_episodes_with_filters`: Listado con filtros combinados (`estado`, `nivel_prioridad`, `paciente_id`).

---

## 3. Validación de No-Regresión

```bash
pytest backend/tests/test_episode_repository.py backend/tests/test_episodios_db.py backend/tests/test_migrations.py -v
```
