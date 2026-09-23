-- ============================================================================
-- MediFlow — Migración V001: Schema inicial
-- Base de datos: mediflow_dev
-- Motor: PostgreSQL 17
-- Descripción: Crea todas las tablas necesarias para el agente de triaje
--              clínico autónomo. Diseño orientado a consultas y auditoría.
-- ============================================================================

-- ── Extensiones ──────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUIDs
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Búsqueda por similitud de texto
CREATE EXTENSION IF NOT EXISTS "unaccent";       -- Búsqueda sin tildes

-- ── Tipos enumerados ─────────────────────────────────────────────────────────
CREATE TYPE tipo_archivo_enum AS ENUM ('PDF', 'IMAGEN', 'TEXTO', 'JSON');
CREATE TYPE nivel_prioridad_enum AS ENUM ('Urgente', 'Rutina', 'Ambiguo');
CREATE TYPE status_documento_enum AS ENUM ('procesado', 'error', 'pendiente_auditoria');
CREATE TYPE destino_enum AS ENUM (
    'Cola_Emergencia_Medica',
    'Cola_Rutina',
    'Cola_Auditoria_Humana'
);
CREATE TYPE status_oci_enum AS ENUM ('exito', 'error', 'pendiente');
CREATE TYPE decision_auditoria_enum AS ENUM ('aprobar', 'rechazar', 'reclasificar');

-- ============================================================================
-- TABLA PRINCIPAL: documentos_triaje
-- Almacena el resultado completo de cada documento procesado por el agente.
-- ============================================================================
CREATE TABLE IF NOT EXISTS documentos_triaje (
    -- ── Identificación ────────────────────────────────────────────────────────
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    documento_id                VARCHAR(255) UNIQUE NOT NULL,
    tipo_archivo                tipo_archivo_enum NOT NULL,
    canal_origen                VARCHAR(255) NOT NULL DEFAULT '',
    status                      status_documento_enum NOT NULL DEFAULT 'pendiente_auditoria',

    -- ── Texto procesado ───────────────────────────────────────────────────────
    texto_extraido              TEXT,

    -- ── Clasificación (Nodo 3: classification + Nodo 4: confidence) ──────────
    tipo_documento              VARCHAR(255),
    especialidad                VARCHAR(255),
    nivel_prioridad             nivel_prioridad_enum,
    score_confianza             FLOAT CHECK (score_confianza >= 0 AND score_confianza <= 1),

    -- ── Datos extraídos del documento (Nodo 2: extraction) ───────────────────
    paciente_nombre             VARCHAR(500),
    paciente_edad               SMALLINT CHECK (paciente_edad > 0 AND paciente_edad < 150),
    paciente_id_externo         VARCHAR(255),
    medico_nombre               VARCHAR(500),
    medico_matricula            VARCHAR(100),
    estudio_realizado           TEXT,
    diagnostico_principal       TEXT,
    cie10_sugerido              VARCHAR(20),
    hallazgos_clave             JSONB DEFAULT '[]'::JSONB,

    -- ── Decisión de enrutamiento (Nodo 5: routing) ───────────────────────────
    destino_principal           destino_enum,
    requiere_auditoria_humana   BOOLEAN NOT NULL DEFAULT FALSE,
    justificacion_enrutamiento  TEXT,
    notificacion_generada       JSONB,

    -- ── OCI Object Storage ────────────────────────────────────────────────────
    oci_bucket                  VARCHAR(255),
    oci_ruta_objeto             VARCHAR(1000),
    oci_status                  status_oci_enum DEFAULT 'pendiente',

    -- ── Metadatos del agente ──────────────────────────────────────────────────
    nodos_ejecutados            JSONB DEFAULT '[]'::JSONB,
    tiempo_procesamiento_ms     INTEGER,
    metadata                    JSONB DEFAULT '{}'::JSONB,
    error_mensaje               TEXT,

    -- ── Timestamps ───────────────────────────────────────────────────────────
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE documentos_triaje IS
    'Resultado completo del triaje de cada documento clínico procesado por el agente.';
COMMENT ON COLUMN documentos_triaje.documento_id IS
    'ID único del documento, proviene del sistema de origen.';
COMMENT ON COLUMN documentos_triaje.score_confianza IS
    'Score de confianza 0.0-1.0: <0.5=Ambiguo, 0.5-0.8=Rutina, >0.8=Urgente/Rutina';
COMMENT ON COLUMN documentos_triaje.hallazgos_clave IS
    'Array JSON de hallazgos clínicos clave detectados por el LLM.';

-- ============================================================================
-- TABLA: auditorias_hitl
-- Human-in-the-Loop: decisiones de auditores clínicos sobre documentos ambiguos.
-- ============================================================================
CREATE TABLE IF NOT EXISTS auditorias_hitl (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    documento_triaje_id         UUID NOT NULL REFERENCES documentos_triaje(id) ON DELETE CASCADE,
    documento_id                VARCHAR(255) NOT NULL,

    -- ── Decisión del auditor ──────────────────────────────────────────────────
    decision                    decision_auditoria_enum NOT NULL,
    auditor_id                  VARCHAR(255) NOT NULL,
    comentario                  TEXT,

    -- ── Reclasificación (si decision = 'reclasificar') ────────────────────────
    nueva_nivel_prioridad       nivel_prioridad_enum,
    nuevo_destino               destino_enum,
    nuevo_tipo_documento        VARCHAR(255),

    -- ── Timestamps ───────────────────────────────────────────────────────────
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE auditorias_hitl IS
    'Registro de decisiones de auditoría humana (Human-in-the-Loop) sobre documentos ambiguos.';

-- ============================================================================
-- TABLA: notificaciones
-- Alertas generadas para urgencias médicas.
-- ============================================================================
CREATE TABLE IF NOT EXISTS notificaciones (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    documento_triaje_id         UUID NOT NULL REFERENCES documentos_triaje(id) ON DELETE CASCADE,
    documento_id                VARCHAR(255) NOT NULL,

    canal                       VARCHAR(255) NOT NULL,
    mensaje                     TEXT NOT NULL,
    enviada                     BOOLEAN NOT NULL DEFAULT FALSE,
    error_envio                 TEXT,

    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    enviada_at                  TIMESTAMPTZ
);

COMMENT ON TABLE notificaciones IS
    'Alertas generadas automáticamente para casos urgentes (TEP, emergencias, etc.)';

-- ============================================================================
-- TABLA: cola_procesamiento
-- Vista lógica de las colas de triaje (materializada para consultas rápidas).
-- ============================================================================
CREATE TABLE IF NOT EXISTS cola_procesamiento (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    documento_id                VARCHAR(255) UNIQUE NOT NULL,
    destino                     destino_enum NOT NULL,
    nivel_prioridad             nivel_prioridad_enum,
    score_confianza             FLOAT,
    status                      status_documento_enum NOT NULL DEFAULT 'pendiente_auditoria',
    asignado_a                  VARCHAR(255),
    asignado_at                 TIMESTAMPTZ,
    resuelto_at                 TIMESTAMPTZ,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE cola_procesamiento IS
    'Cola de documentos pendientes por destino. Permite gestión de flujo de trabajo clínico.';

-- ============================================================================
-- ÍNDICES — Optimización de consultas frecuentes
-- ============================================================================

-- documentos_triaje
CREATE INDEX IF NOT EXISTS idx_dt_documento_id
    ON documentos_triaje(documento_id);
CREATE INDEX IF NOT EXISTS idx_dt_status
    ON documentos_triaje(status);
CREATE INDEX IF NOT EXISTS idx_dt_nivel_prioridad
    ON documentos_triaje(nivel_prioridad);
CREATE INDEX IF NOT EXISTS idx_dt_destino
    ON documentos_triaje(destino_principal);
CREATE INDEX IF NOT EXISTS idx_dt_requiere_auditoria
    ON documentos_triaje(requiere_auditoria_humana) WHERE requiere_auditoria_humana = TRUE;
CREATE INDEX IF NOT EXISTS idx_dt_created_at
    ON documentos_triaje(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_dt_canal_origen
    ON documentos_triaje(canal_origen);

-- Búsqueda de texto en diagnóstico y paciente
CREATE INDEX IF NOT EXISTS idx_dt_diagnostico_trgm
    ON documentos_triaje USING GIN (diagnostico_principal gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_dt_paciente_trgm
    ON documentos_triaje USING GIN (paciente_nombre gin_trgm_ops);

-- auditorias_hitl
CREATE INDEX IF NOT EXISTS idx_ahitl_documento_id
    ON auditorias_hitl(documento_id);
CREATE INDEX IF NOT EXISTS idx_ahitl_auditor
    ON auditorias_hitl(auditor_id);
CREATE INDEX IF NOT EXISTS idx_ahitl_created_at
    ON auditorias_hitl(created_at DESC);

-- notificaciones
CREATE INDEX IF NOT EXISTS idx_notif_enviada
    ON notificaciones(enviada) WHERE enviada = FALSE;
CREATE INDEX IF NOT EXISTS idx_notif_documento_id
    ON notificaciones(documento_id);

-- cola_procesamiento
CREATE INDEX IF NOT EXISTS idx_cola_destino_status
    ON cola_procesamiento(destino, status);

-- ============================================================================
-- FUNCIÓN Y TRIGGER: updated_at automático
-- ============================================================================
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_documentos_triaje
    BEFORE UPDATE ON documentos_triaje
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_updated_at();

-- ============================================================================
-- FUNCIÓN: sincronizar_cola
-- Inserta/actualiza automáticamente en cola_procesamiento cuando se crea
-- o actualiza un documento en documentos_triaje.
-- ============================================================================
CREATE OR REPLACE FUNCTION sincronizar_cola()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.destino_principal IS NOT NULL THEN
        INSERT INTO cola_procesamiento (
            documento_id,
            destino,
            nivel_prioridad,
            score_confianza,
            status
        )
        VALUES (
            NEW.documento_id,
            NEW.destino_principal,
            NEW.nivel_prioridad,
            NEW.score_confianza,
            NEW.status
        )
        ON CONFLICT (documento_id) DO UPDATE SET
            destino          = EXCLUDED.destino,
            nivel_prioridad  = EXCLUDED.nivel_prioridad,
            score_confianza  = EXCLUDED.score_confianza,
            status           = EXCLUDED.status;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_sincronizar_cola
    AFTER INSERT OR UPDATE ON documentos_triaje
    FOR EACH ROW
    EXECUTE FUNCTION sincronizar_cola();

-- ============================================================================
-- VISTAS — Consultas frecuentes del sistema
-- ============================================================================

-- Vista: documentos urgentes pendientes
CREATE OR REPLACE VIEW v_urgentes_pendientes AS
SELECT
    dt.documento_id,
    dt.tipo_documento,
    dt.paciente_nombre,
    dt.diagnostico_principal,
    dt.score_confianza,
    dt.canal_origen,
    dt.created_at,
    dt.tiempo_procesamiento_ms
FROM documentos_triaje dt
WHERE dt.nivel_prioridad = 'Urgente'
  AND dt.status = 'procesado'
ORDER BY dt.created_at DESC;

COMMENT ON VIEW v_urgentes_pendientes IS
    'Documentos urgentes procesados, ordenados por fecha de llegada.';

-- Vista: documentos en auditoría humana
CREATE OR REPLACE VIEW v_auditoria_pendiente AS
SELECT
    dt.documento_id,
    dt.tipo_documento,
    dt.paciente_nombre,
    dt.diagnostico_principal,
    dt.score_confianza,
    dt.nivel_prioridad,
    dt.justificacion_enrutamiento,
    dt.error_mensaje,
    dt.created_at
FROM documentos_triaje dt
WHERE dt.requiere_auditoria_humana = TRUE
  AND dt.status = 'pendiente_auditoria'
ORDER BY dt.created_at ASC;  -- FIFO: primero el más antiguo

COMMENT ON VIEW v_auditoria_pendiente IS
    'Cola HITL: documentos esperando revisión humana (FIFO).';

-- Vista: estadísticas del día
CREATE OR REPLACE VIEW v_estadisticas_hoy AS
SELECT
    COUNT(*) FILTER (WHERE status = 'procesado')               AS procesados_ok,
    COUNT(*) FILTER (WHERE status = 'pendiente_auditoria')     AS en_auditoria,
    COUNT(*) FILTER (WHERE status = 'error')                   AS errores,
    COUNT(*) FILTER (WHERE nivel_prioridad = 'Urgente')        AS urgentes,
    COUNT(*) FILTER (WHERE nivel_prioridad = 'Rutina')         AS rutina,
    COUNT(*) FILTER (WHERE nivel_prioridad = 'Ambiguo')        AS ambiguos,
    ROUND(AVG(score_confianza)::NUMERIC, 3)                    AS score_promedio,
    ROUND(AVG(tiempo_procesamiento_ms)::NUMERIC, 0)            AS tiempo_ms_promedio,
    COUNT(*)                                                   AS total
FROM documentos_triaje
WHERE created_at >= CURRENT_DATE;

COMMENT ON VIEW v_estadisticas_hoy IS
    'Estadísticas de triaje del día actual.';

-- ============================================================================
-- DATOS INICIALES — 3 casos de prueba del brief del proyecto
-- ============================================================================
INSERT INTO documentos_triaje (
    documento_id, tipo_archivo, canal_origen, status,
    texto_extraido,
    tipo_documento, nivel_prioridad, score_confianza,
    paciente_nombre, paciente_edad,
    diagnostico_principal, cie10_sugerido,
    hallazgos_clave,
    destino_principal, requiere_auditoria_humana,
    justificacion_enrutamiento,
    tiempo_procesamiento_ms
) VALUES
-- Caso 1: Rutina
(
    'DOC-SEED-2026-0001', 'TEXTO', 'Consulta_Externa', 'procesado',
    'LABORATORIO CENTRAL. Paciente: Ana García, 35 años. Hemograma completo. Resultados dentro de rangos normales.',
    'Analítica de Laboratorio', 'Rutina', 0.92,
    'Ana García', 35,
    'Hemograma normal', NULL,
    '["Resultados dentro de rangos normales"]',
    'Cola_Rutina', FALSE,
    'Documento procesado con alta confianza. Sin hallazgos urgentes.',
    850
),
-- Caso 2: Urgente (TEP Agudo)
(
    'DOC-SEED-2026-8942', 'TEXTO', 'Guardia_Emergencias', 'procesado',
    'HOSPITAL SANTA LUCIA - INFORME RADIOLOGICO. Paciente: Carlos Eduardo Mendes, 52 años. TEP agudo detectado.',
    'Informe de Estudio por Imagenes', 'Urgente', 0.99,
    'Carlos Eduardo Mendes', 52,
    'Tromboembolismo Pulmonar Agudo (TEP)', 'I26.9',
    '["Defecto de llenado en arteria pulmonar compatible con TEP agudo"]',
    'Cola_Emergencia_Medica', FALSE,
    'Hallazgo crítico de alta gravedad (TEP agudo) detectado en paciente sintomático.',
    1240
),
-- Caso 3: Ambiguo
(
    'DOC-SEED-2026-9999', 'TEXTO', 'Admision', 'pendiente_auditoria',
    '... texto ilegible ... px ... 45 ... mgr ??? firma ilegible',
    'Desconocido', 'Ambiguo', 0.22,
    NULL, NULL,
    NULL, NULL,
    '[]',
    'Cola_Auditoria_Humana', TRUE,
    'Score de confianza bajo (0.22). Texto ilegible o insuficiente.',
    320
)
ON CONFLICT (documento_id) DO NOTHING;

-- ============================================================================
-- FIN DE MIGRACIÓN V001
-- ============================================================================
SELECT 'MediFlow V001 migración completada.' AS resultado;
