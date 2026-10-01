# Requirements Checklist: Vista SQL v_episodios_detalle para Consulta Agregada

**Purpose**: Verificación de completitud y calidad para la creación de la vista relacional `v_episodios_detalle` en PostgreSQL  
**Created**: 2026-10-01  
**Feature**: [spec.md](../spec.md)  

---

## 🗄️ Esquema y Estructura SQL

- [x] CHK001 Sentencia `CREATE OR REPLACE VIEW v_episodios_detalle AS SELECT ...` definida correctamente.
- [x] CHK002 Inclusión de columnas identificadoras de `episodios_clinicos` (`id AS episodio_id`, `codigo_episodio`, `estado_atencion`, `nivel_prioridad`).
- [x] CHK003 Inclusión de campos clínicos diagnósticos (`motivo_consulta`, `diagnostico_general`, `diagnostico_especialista`, `especialidad_requerida`).
- [x] CHK004 Inclusión de timestamps de trazabilidad (`created_at`, `updated_at`).
- [x] CHK005 Inclusión de datos del paciente (`id AS paciente_id`, `tipo_documento`, `numero_documento`, `historia_clinica`, `genero`, `numero_telefono`, `correo`).
- [x] CHK006 Cálculo dinámico de la edad del paciente en años en tiempo real: `EXTRACT(YEAR FROM age(CURRENT_DATE, p.fecha_nacimiento))::INT`.
- [x] CHK007 Manejo seguro de nulos en fecha de nacimiento mediante condicional `CASE WHEN ... END AS paciente_edad`.
- [x] CHK008 Concatenación limpia de nombres y apellidos: `TRIM(CONCAT(p.nombres, ' ', p.apellidos)) AS paciente_nombre_completo`.

---

## 👥 Relaciones y Joins

- [x] CHK009 Relación `LEFT JOIN pacientes p ON e.paciente_id = p.id`.
- [x] CHK010 Relación `LEFT JOIN usuarios op ON e.operador_ingreso_id = op.id` para el operador de admisión.
- [x] CHK011 Relación `LEFT JOIN usuarios mg ON e.medico_general_id = mg.id` con nombre y `especialidad_medica`.
- [x] CHK012 Relación `LEFT JOIN usuarios me ON e.medico_especialista_id = me.id` con nombre y `especialidad_medica`.

---

## 🔄 Gobernanza de Base de Datos y Alembic

- [x] CHK013 Migración de Alembic creada con ID de revisión único (`p9q909633lm5`).
- [x] CHK014 `down_revision` encadenada a `o8p808522kl4`.
- [x] CHK015 Sentencia `COMMENT ON VIEW v_episodios_detalle` incluida para documentación en PostgreSQL.
- [x] CHK016 Sentencia `DROP VIEW IF EXISTS v_episodios_detalle CASCADE;` en `downgrade()`.

---

## 🧪 Pruebas Automatizadas (Regla de Oro de MediFlow)

- [x] CHK017 Test de DDL offline `test_upgrade_sql_creates_v_episodios_detalle_view` implementado.
- [x] CHK018 Test de columnas y cálculo de edad `test_vista_sql_contains_required_fields_and_dynamic_age` implementado.
- [x] CHK019 Ejecución de pruebas con 100% en verde sin mutar la base de datos de desarrollo.
- [x] CHK020 Verificación de cero regresiones junto a `test_migrations.py`.
