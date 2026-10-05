# Feature Specification: Vista SQL v_episodios_detalle para Consulta Agregada de Episodios Clínicos

**Feature Branch**: `002-v-episodios-detalle` (desarrollado en rama de trabajo `dev-wilmer-gulcochia`)  
**Created**: 2026-10-01  
**Status**: Completed  
**Input**: Crear vista SQL `v_episodios_detalle` en PostgreSQL mediante migración Alembic para relacionar episodios, paciente y médico asignado  

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consulta Agregada de Episodios para Admisión y Triaje (Priority: P1)

Como personal médico, coordinador o servicio del backend de MediFlow, quiero consultar la vista `v_episodios_detalle` para obtener de forma unificada y atómica toda la información clínica de un episodio, los datos del paciente (incluyendo su edad calculada dinámicamente) y los profesionales de salud asignados sin requerir múltiples consultas `JOIN` repetitivas.

**Why this priority**: Es la base de datos relacional sobre la cual el repositorio `episode_repository.py` y los endpoints del módulo de triaje y admisión consumirán los datos unificados del ciclo de atención del paciente.

**Independent Test**: Puede validarse ejecutando la consulta `SELECT * FROM v_episodios_detalle WHERE episodio_id = ...` y verificando que retorne todas las columnas proyectadas tanto del episodio como del paciente y los usuarios asignados.

**Acceptance Scenarios**:
1. **Given** un episodio clínico registrado asociado a un paciente con fecha de nacimiento, **When** se consulta `v_episodios_detalle`, **Then** el campo `paciente_edad` refleja la edad exacta calculada en años en tiempo real mediante `EXTRACT(YEAR FROM age(CURRENT_DATE, p.fecha_nacimiento))::INT`.
2. **Given** un episodio clínico sin médico especialista asignado aún (`medico_especialista_id IS NULL`), **When** se consulta la vista mediante `LEFT JOIN`, **Then** la consulta retorna el registro con los campos del médico especialista en `NULL` sin descartar el episodio.
3. **Given** nombres y apellidos de pacientes y usuarios, **When** se proyectan en la vista, **Then** se entregan concatenados y limpios de espacios residuales (`TRIM(CONCAT(nombres, ' ', apellidos))`).

---

### User Story 2 - Validación DDL y Suite de Pruebas Offline (Priority: P2)

Como desarrollador y auditor de calidad, quiero que la migración de la vista cuente con tests unitarios automatizados que verifiquen la generación de SQL offline con Alembic para cumplir la Regla de Oro de MediFlow (cero mutación de la base de datos de desarrollo durante pruebas unitarias).

**Why this priority**: Garantiza la reproducibilidad y estabilidad de las migraciones en entornos CI/CD sin comprometer los datos de desarrollo.

**Independent Test**: Ejecutar `pytest backend/tests/test_episodios_db.py -v` y verificar 100% de aserciones en verde.

**Acceptance Scenarios**:
1. **Given** el comando `alembic upgrade head --sql`, **When** se inspecciona la salida SQL, **Then** contiene la sentencia `CREATE OR REPLACE VIEW v_episodios_detalle` y su respectivo `COMMENT ON VIEW`.

---

### User Story 3 - Migración Reversible y Gobernanza Alembic (Priority: P3)

Como administrador de base de datos, quiero que la migración cuente con soporte completo para `downgrade` y documentación de catálogo PostgreSQL (`COMMENT ON VIEW`).

**Why this priority**: Permite reversiones limpias y mantiene el catálogo de PostgreSQL documentado.

**Independent Test**: Verificar que `DOWNGRADE_STATEMENTS` ejecute `DROP VIEW IF EXISTS v_episodios_detalle CASCADE;`.

**Acceptance Scenarios**:
1. **Given** la necesidad de revertir la migración, **When** se ejecuta `alembic downgrade -1`, **Then** la vista `v_episodios_detalle` es eliminada de forma segura sin dejar bloqueos o inconsistencias.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La base de datos DEBE proporcionar la vista relacional `v_episodios_detalle`.
- **FR-002**: La vista DEBE incluir los campos principales de `episodios_clinicos`: `episodio_id`, `codigo_episodio`, `estado_atencion`, `nivel_prioridad`, `motivo_consulta`, `diagnostico_general`, `diagnostico_especialista`, `especialidad_requerida`, `created_at`, `updated_at`.
- **FR-003**: La vista DEBE proyectar los datos del paciente: `paciente_id`, `paciente_tipo_documento`, `paciente_numero_documento`, `paciente_historia_clinica`, `paciente_nombres`, `paciente_apellidos`, `paciente_nombre_completo`, `paciente_fecha_nacimiento`, `paciente_edad`, `paciente_genero`, `paciente_numero_telefono`, `paciente_correo`.
- **FR-004**: El cálculo de `paciente_edad` DEBE ser dinámico respecto a `CURRENT_DATE` y manejar valores nulos mediante `CASE WHEN p.fecha_nacimiento IS NOT NULL THEN EXTRACT(YEAR FROM age(CURRENT_DATE, p.fecha_nacimiento))::INT ELSE NULL END`.
- **FR-005**: La vista DEBE vincular mediante `LEFT JOIN` a:
  - `usuarios op ON e.operador_ingreso_id = op.id` (Operador de Admisión)
  - `usuarios mg ON e.medico_general_id = mg.id` (Médico General)
  - `usuarios me ON e.medico_especialista_id = me.id` (Médico Especialista)
- **FR-006**: La migración Alembic DEBE tener como revisión previa (`down_revision`) a `o8p808522kl4` (migración del modelo unificado hospitalario).
- **FR-007**: La migración DEBE incluir `COMMENT ON VIEW v_episodios_detalle IS '...'` documentando su propósito en PostgreSQL.
- **FR-008**: La migración DEBE soportar `downgrade()` seguro con `DROP VIEW IF EXISTS v_episodios_detalle CASCADE;`.

---

## Edge Cases

- **Pacientes sin fecha de nacimiento registrada**: La columna `paciente_edad` devuelve `NULL` sin provocar excepciones SQL.
- **Episodios con personal médico no asignado aún**: Las columnas de operador, médico general o especialista devuelven `NULL` sin omitir el registro del episodio (`LEFT JOIN`).
- **Nombres o apellidos con espacios en blanco adicionales**: La función `TRIM(CONCAT(...))` limpia espacios antes y después del nombre completo.
