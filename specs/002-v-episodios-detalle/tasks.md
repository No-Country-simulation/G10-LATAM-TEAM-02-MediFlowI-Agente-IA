# Tasks: Vista SQL v_episodios_detalle para Consulta Agregada de Episodios Clínicos

**Input**: `specs/002-v-episodios-detalle/spec.md`  
**Feature Branch**: `002-v-episodios-detalle` (en rama de trabajo `dev-wilmer-gulcochia`)  
**Status**: Completed (100% Tests Passed)  

---

## Phase 1: Setup & Prerrequisitos

- [x] `TASK-001`: Verificar que el entorno de desarrollo y la base de datos PostgreSQL `mediflow_dev` estén operativos en Docker (`make db` o servicio local).
- [x] `TASK-002`: Confirmar que la última migración de Alembic previa sea `o8p808522kl4` (`python3 -m alembic current` o `alembic upgrade head --sql`).

---

## Phase 2: User Story 1 (Priority: P1) — Definición SQL de la Vista Agregada

- [x] `TASK-003`: Diseñar la consulta SQL `CREATE OR REPLACE VIEW v_episodios_detalle AS ...` con `LEFT JOIN` hacia:
  - `episodios_clinicos e`
  - `pacientes p ON e.paciente_id = p.id`
  - `usuarios op ON e.operador_ingreso_id = op.id`
  - `usuarios mg ON e.medico_general_id = mg.id`
  - `usuarios me ON e.medico_especialista_id = me.id`
- [x] `TASK-004`: Incorporar el cálculo dinámico de edad en la vista:
  `EXTRACT(YEAR FROM age(CURRENT_DATE, p.fecha_nacimiento))::INT AS paciente_edad`
- [x] `TASK-005`: Incorporar la concatenación de nombres completos:
  `TRIM(CONCAT(p.nombres, ' ', p.apellidos)) AS paciente_nombre_completo`
  `TRIM(CONCAT(mg.nombres, ' ', mg.apellidos)) AS medico_general_nombre`
  `TRIM(CONCAT(me.nombres, ' ', me.apellidos)) AS medico_especialista_nombre`
  `TRIM(CONCAT(op.nombres, ' ', op.apellidos)) AS operador_ingreso_nombre`

---

## Phase 3: User Story 2 (Priority: P2) — Suite de Pruebas Unitarias TDD

- [x] `TASK-006`: Crear archivo de pruebas `backend/tests/test_episodios_db.py`.
- [x] `TASK-007`: Implementar test unitario `test_vista_sql_contains_required_fields_and_dynamic_age` que valide la presencia de todas las columnas esperadas.
- [x] `TASK-008`: Implementar test unitario `test_upgrade_sql_creates_v_episodios_detalle_view` que valide la generación offline con Alembic.
- [x] `TASK-009`: Validar relaciones LEFT JOIN y sentencia de downgrade (`DROP VIEW IF EXISTS v_episodios_detalle CASCADE`).

---

## Phase 4: User Story 3 (Priority: P3) — Migración Alembic con Soporte Downgrade

- [x] `TASK-010`: Crear archivo de migración `backend/alembic/versions/p9q909633lm5_add_v_episodios_detalle_view.py` con `down_revision = 'o8p808522kl4'`.
- [x] `TASK-011`: Definir `UPGRADE_STATEMENTS` con el `CREATE VIEW` y `COMMENT ON VIEW v_episodios_detalle IS 'Vista agregada de consulta clínica...'`.
- [x] `TASK-012`: Definir `DOWNGRADE_STATEMENTS` con `DROP VIEW IF EXISTS v_episodios_detalle CASCADE;`.

---

## Phase 5: Verificación y Calidad (Regla de Oro de MediFlow)

- [x] `TASK-013`: Validar la migración offline: `alembic upgrade head --sql`.
- [x] `TASK-014`: Ejecutar suite de pruebas: `pytest backend/tests/test_episodios_db.py -v`.
- [x] `TASK-015`: Ejecutar suite general de backend para asegurar cero regresiones: `pytest backend/tests/test_episodios_db.py backend/tests/test_migrations.py -v`.
- [x] `TASK-016`: Registrar el progreso y dejar listo para el commit atómico y Pull Request.
