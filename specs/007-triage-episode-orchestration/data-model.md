# Data Model: Orquestación de Triaje y Episodios Clínicos

**Feature**: `007-triage-episode-orchestration`
**Date**: 2026-10-10

## 1. Entidades y Tablas Relacionales

### `episodios_clinicos` (Tabla existente)

Representa la unidad de atención hospitalaria para un paciente.

| Campo | Tipo SQL | Restricción | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PK, DEFAULT gen_random_uuid()` | Identificador único del episodio |
| `codigo_episodio` | `VARCHAR(50)` | `UNIQUE, NOT NULL` | Formato clínico: `EP-YYYYMMDD-XXXX` |
| `paciente_id` | `UUID` | `FK -> pacientes(id), NOT NULL` | Paciente que recibe la atención |
| `operador_ingreso_id` | `UUID` | `FK -> usuarios(id), NULL` | Operador/médico que inicia el registro |
| `medico_general_id` | `UUID` | `FK -> usuarios(id), NULL` | Médico general asignado |
| `medico_especialista_id` | `UUID` | `FK -> usuarios(id), NULL` | Especialista derivado |
| `especialidad_requerida` | `VARCHAR(100)` | `NULL` | Especialidad sugerida o solicitada |
| `estado_atencion` | `VARCHAR(50)` | `NOT NULL, DEFAULT 'ingresado'` | Estado del ciclo asistencial |
| `nivel_prioridad` | `VARCHAR(20)` | `NOT NULL, DEFAULT 'Rutina'` | `Urgente`, `Rutina`, `Ambiguo` |
| `motivo_consulta` | `TEXT` | `NULL` | Motivo de ingreso o diagnóstico preliminar |
| `diagnostico_general` | `TEXT` | `NULL` | Conclusión de atención general |
| `diagnostico_especialista`| `TEXT` | `NULL` | Conclusión de especialista |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Fecha de apertura |
| `updated_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Última actualización |

#### Estados de Atención (`estado_atencion`)
- **Activos**: `'ingresado'`, `'evaluacion_general'`, `'derivado_especialista'`, `'en_atencion_especialista'`, `'auditoria_coordinacion'`.
- **Finalizados**: `'atendido'`, `'cerrado'`.

---

### `documentos_triaje` (Tabla existente — columna `episodio_id`)

Almacena el resultado del procesamiento del documento por el agente autónomo.

| Campo | Tipo SQL | Restricción | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PK` | Identificador interno |
| `documento_id` | `VARCHAR(100)` | `UNIQUE, NOT NULL` | Identificador único del documento |
| `episodio_id` | `UUID` | `FK -> episodios_clinicos(id), NULL` | **Episodio vinculado al documento** |
| `paciente_id` | `UUID` | `FK -> pacientes(id), NULL` | Paciente asociado |
| `usuario_registro_id` | `UUID` | `FK -> usuarios(id), NULL` | Usuario que registró/subió el archivo |
| `prioridad_ia` | `VARCHAR(20)` | `NOT NULL` | Prioridad inferida |
| `score_confianza` | `NUMERIC(4,3)` | `NOT NULL` | Confianza de la extracción |
| `destino_principal` | `VARCHAR(50)` | `NOT NULL` | Destino clínico sugerido |
| `metadata` | `JSONB` | `DEFAULT '{}'` | Metadatos que incluyen `episodio_id`, `codigo_episodio` |

---

### `trazabilidad_eventos` (Tabla existente)

Bitácora inmutable de eventos clínicos.

| Campo | Tipo SQL | Restricción | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | `PK` | Identificador único del evento |
| `episodio_id` | `UUID` | `FK -> episodios_clinicos(id), NULL` | Episodio relacionado |
| `documento_id` | `UUID` | `FK -> documentos_triaje(id), NULL` | Documento de triaje relacionado |
| `usuario_id` | `UUID` | `FK -> usuarios(id), NULL` | Autor del evento |
| `evento` | `VARCHAR(50)` | `NOT NULL` | `'DOCUMENTO_ASOCIADO_A_EPISODIO'` |
| `descripcion` | `TEXT` | `NOT NULL` | Resumen del evento |
| `metadata` | `JSONB` | `DEFAULT '{}'` | Datos de contexto (código episodio, novedad) |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Timestamp inmutable |

---

## 2. Modelos de Intercambio y Estado (Python)

### Metadatos en `AgentState.metadata`
```python
{
    "asociacion_paciente": "asociado",  # 'asociado' | 'conflicto' | 'sin_coincidencia'
    "paciente_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "episodio_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "codigo_episodio": "EP-20261010-AB12",
    "episodio_nuevo": True,             # True si se creó, False si ya existía activo
}
```
