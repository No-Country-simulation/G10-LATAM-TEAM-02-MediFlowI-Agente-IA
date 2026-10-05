# Contract: episode_repository Python Interface

**Module**: `backend/app/repositories/episode_repository.py`  
**Feature**: [spec.md](../spec.md)

---

## 1. Métodos Expuestos

### `create_episode(data: dict[str, Any]) -> dict[str, Any]`
Crea un nuevo episodio clínico en la tabla `episodios_clinicos`.

- **Parámetros**:
  - `data['paciente_id']`: `UUID | str` (Obligatorio)
  - `data['operador_ingreso_id']`: `UUID | str` (Opcional)
  - `data['codigo_episodio']`: `str` (Opcional; si no se provee, se auto-genera)
  - `data['motivo_consulta']`: `str` (Opcional)
  - `data['nivel_prioridad']`: `str` (Opcional, default `'Rutina'`)
  - `data['especialidad_requerida']`: `str` (Opcional)
  - `data['estado_atencion']`: `str` (Opcional, default `'ingresado'`)
- **Retorna**: `dict[str, Any]` con el registro insertado (incluye `id`, `codigo_episodio`, `created_at`).
- **Excepciones**: `DatabaseUnavailableError` si PostgreSQL no responde o falla la inserción.

---

### `get_episode_by_id(episode_id: UUID | str) -> dict[str, Any] | None`
Consulta la vista `v_episodios_detalle` para obtener el detalle consolidado del episodio.

- **Parámetros**: `episode_id` (`UUID` o `str` válido).
- **Retorna**: `dict[str, Any]` con todos los datos clínicos, paciente con edad calculada y profesionales, o `None` si no existe.
- **Excepciones**: `DatabaseUnavailableError`.

---

### `get_episode_by_code(codigo_episodio: str) -> dict[str, Any] | None`
Consulta la vista `v_episodios_detalle` por el código clínico único.

- **Parámetros**: `codigo_episodio` (`str`).
- **Retorna**: `dict[str, Any]` o `None`.
- **Excepciones**: `DatabaseUnavailableError`.

---

### `update_episode_status(episode_id: UUID | str, nuevo_estado: str) -> bool`
Actualiza el estado de atención de un episodio y actualiza `updated_at`.

- **Parámetros**:
  - `episode_id`: `UUID | str`.
  - `nuevo_estado`: `str` (`ingresado`, `en_triaje`, `atendido`, `derivado`, `cerrado`).
- **Retorna**: `True` si el registro fue encontrado y actualizado, `False` si no existía.
- **Excepciones**: `DatabaseUnavailableError`, `ValueError` si el estado no es válido.

---

### `assign_doctor(episode_id: UUID | str, medico_id: UUID | str, rol: str, especialidad: str | None = None) -> bool`
Asigna un médico general o especialista al episodio.

- **Parámetros**:
  - `episode_id`: `UUID | str`.
  - `medico_id`: `UUID | str`.
  - `rol`: `str` (`'general'` o `'especialista'`).
  - `especialidad`: `str | None`.
- **Retorna**: `True` si se asignó exitosamente, `False` si no se encontró el episodio.
- **Excepciones**: `DatabaseUnavailableError`.

---

### `list_episodes(estado: str | None = None, nivel_prioridad: str | None = None, paciente_id: UUID | str | None = None, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]`
Lista episodios desde `v_episodios_detalle` aplicando filtros opcionales.

- **Parámetros**:
  - `estado`: Filtro por `estado_atencion`.
  - `nivel_prioridad`: Filtro por `nivel_prioridad`.
  - `paciente_id`: Filtro por paciente específico.
  - `limit`: Límite de paginación (default 50).
  - `offset`: Desplazamiento (default 0).
- **Retorna**: `list[dict[str, Any]]` ordenado por `created_at DESC`.
- **Excepciones**: `DatabaseUnavailableError`.
