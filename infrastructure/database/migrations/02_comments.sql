-- ============================================================================
-- MediFlow — Comentarios PostgreSQL (Dictionary Comments)
-- Base de datos: mediflow_dev
-- Motor: PostgreSQL 17
-- Descripción: Agrega comentarios descriptivos a todas las tablas y columnas.
-- ============================================================================

-- ── 1. TABLA: documentos_triaje ─────────────────────────────────────────────
COMMENT ON TABLE documentos_triaje IS 'Resultado completo del triaje de cada documento clínico procesado por el agente autónomo.';
COMMENT ON COLUMN documentos_triaje.id IS 'Identificador único (UUID) del registro de triaje.';
COMMENT ON COLUMN documentos_triaje.documento_id IS 'ID único de negocio del documento (ej. DOC-776123).';
COMMENT ON COLUMN documentos_triaje.tipo_archivo IS 'Formato de entrada del archivo (PDF, IMAGEN, TEXTO, JSON).';
COMMENT ON COLUMN documentos_triaje.canal_origen IS 'Canal o sistema emisor del documento (ej. Guardia_Emergencias).';
COMMENT ON COLUMN documentos_triaje.status IS 'Estado del procesado (procesado, error, pendiente_auditoria).';
COMMENT ON COLUMN documentos_triaje.texto_extraido IS 'Texto completo extraído del informe médico.';
COMMENT ON COLUMN documentos_triaje.tipo_documento IS 'Clasificación del tipo de documento clínico (ej. Angio-TAC, Laboratorio).';
COMMENT ON COLUMN documentos_triaje.especialidad IS 'Especialidad médica relacionada.';
COMMENT ON COLUMN documentos_triaje.nivel_prioridad IS 'Nivel de urgencia determinado por el agente (Urgente, Rutina, Ambiguo).';
COMMENT ON COLUMN documentos_triaje.score_confianza IS 'Score de confianza de la clasificación entre 0.0 y 1.0.';
COMMENT ON COLUMN documentos_triaje.paciente_nombre IS 'Nombre del paciente extraído del documento.';
COMMENT ON COLUMN documentos_triaje.paciente_edad IS 'Edad del paciente en años.';
COMMENT ON COLUMN documentos_triaje.paciente_id_externo IS 'DNI, Historia Clínica o identificador externo del paciente.';
COMMENT ON COLUMN documentos_triaje.medico_nombre IS 'Nombre del médico solicitante.';
COMMENT ON COLUMN documentos_triaje.medico_matricula IS 'Matrícula o registro profesional del médico.';
COMMENT ON COLUMN documentos_triaje.estudio_realizado IS 'Nombre del estudio o prueba médica analizada.';
COMMENT ON COLUMN documentos_triaje.diagnostico_principal IS 'Diagnóstico o impresión clínica principal.';
COMMENT ON COLUMN documentos_triaje.cie10_sugerido IS 'Código CIE-10 sugerido por el modelo de IA.';
COMMENT ON COLUMN documentos_triaje.hallazgos_clave IS 'Array de hallazgos clínicos relevantes en formato JSONB.';
COMMENT ON COLUMN documentos_triaje.destino_principal IS 'Cola de destino asignada por enrutamiento.';
COMMENT ON COLUMN documentos_triaje.requiere_auditoria_humana IS 'Indica si requiere intervención médica (Human-in-the-Loop).';
COMMENT ON COLUMN documentos_triaje.justificacion_enrutamiento IS 'Explicación del razonamiento del agente para la decisión.';
COMMENT ON COLUMN documentos_triaje.notificacion_generada IS 'Objeto JSONB con el detalle de la alerta de urgencia generada.';
COMMENT ON COLUMN documentos_triaje.storage_provider IS 'Proveedor de almacenamiento activo (LOCAL u OCI).';
COMMENT ON COLUMN documentos_triaje.archivo_original IS 'Ruta o Key del archivo original guardado.';
COMMENT ON COLUMN documentos_triaje.resultado_json IS 'Ruta o Key del JSON de resultado guardado.';
COMMENT ON COLUMN documentos_triaje.nombre_original IS 'Nombre del archivo original enviado por el cliente.';
COMMENT ON COLUMN documentos_triaje.oci_bucket IS 'Nombre del bucket de Oracle Cloud Object Storage.';
COMMENT ON COLUMN documentos_triaje.oci_ruta_objeto IS 'Ruta/Key del objeto guardado en OCI.';
COMMENT ON COLUMN documentos_triaje.oci_status IS 'Estado del almacenamiento en OCI (exito, error, pendiente).';
COMMENT ON COLUMN documentos_triaje.nodos_ejecutados IS 'Secuencia de nodos ejecutados en el grafo de LangGraph.';
COMMENT ON COLUMN documentos_triaje.tiempo_procesamiento_ms IS 'Tiempo de procesamiento del triaje en milisegundos.';
COMMENT ON COLUMN documentos_triaje.metadata IS 'Metadatos contextuales adicionales del proceso.';
COMMENT ON COLUMN documentos_triaje.error_mensaje IS 'Mensaje de error en caso de fallo durante la ejecución.';
COMMENT ON COLUMN documentos_triaje.created_at IS 'Fecha y hora de creación del registro.';
COMMENT ON COLUMN documentos_triaje.updated_at IS 'Fecha y hora de última modificación del registro.';

-- ── 2. TABLA: auditorias_hitl ────────────────────────────────────────────────
COMMENT ON TABLE auditorias_hitl IS 'Registro de decisiones de auditoría humana (Human-in-the-Loop) sobre documentos ambiguos.';
COMMENT ON COLUMN auditorias_hitl.id IS 'Identificador único (UUID) de la auditoría.';
COMMENT ON COLUMN auditorias_hitl.documento_triaje_id IS 'Referencia FK al documento en la tabla documentos_triaje.';
COMMENT ON COLUMN auditorias_hitl.documento_id IS 'ID de negocio del documento auditado.';
COMMENT ON COLUMN auditorias_hitl.decision IS 'Decisión del auditor médico (aprobar, rechazar, reclasificar).';
COMMENT ON COLUMN auditorias_hitl.auditor_id IS 'Identificador o usuario del médico auditor.';
COMMENT ON COLUMN auditorias_hitl.comentario IS 'Justificación u observaciones registradas por el auditor.';
COMMENT ON COLUMN auditorias_hitl.nueva_nivel_prioridad IS 'Nueva prioridad asignada si fue reclasificado.';
COMMENT ON COLUMN auditorias_hitl.nuevo_destino IS 'Nuevo destino asignado si fue reclasificado.';
COMMENT ON COLUMN auditorias_hitl.nuevo_tipo_documento IS 'Nuevo tipo de documento si fue corregido por el auditor.';
COMMENT ON COLUMN auditorias_hitl.created_at IS 'Fecha y hora de la auditoría.';

-- ── 3. TABLA: configuracion_sistema ──────────────────────────────────────────
COMMENT ON TABLE configuracion_sistema IS 'Almacena la configuración global persistente del sistema.';
COMMENT ON COLUMN configuracion_sistema.clave IS 'Clave identificadora del parámetro (ej. modo_almacenamiento).';
COMMENT ON COLUMN configuracion_sistema.valor IS 'Valor configurado activo (ej. LOCAL u OCI).';
COMMENT ON COLUMN configuracion_sistema.descripcion IS 'Descripción del propósito del parámetro.';
COMMENT ON COLUMN configuracion_sistema.updated_at IS 'Fecha y hora del último cambio de configuración.';

-- ── 4. TABLA: notificaciones ─────────────────────────────────────────────────
COMMENT ON TABLE notificaciones IS 'Alertas generadas automáticamente para casos de urgencia médica.';
COMMENT ON COLUMN notificaciones.id IS 'Identificador único (UUID) de la notificación.';
COMMENT ON COLUMN notificaciones.documento_triaje_id IS 'Referencia FK al documento en documentos_triaje.';
COMMENT ON COLUMN notificaciones.documento_id IS 'ID de negocio del documento.';
COMMENT ON COLUMN notificaciones.canal IS 'Canal de alerta asignado (ej. Guardia_Emergencias).';
COMMENT ON COLUMN notificaciones.mensaje IS 'Mensaje de la alerta clínica.';
COMMENT ON COLUMN notificaciones.enviada IS 'Flag de confirmación de envío.';
COMMENT ON COLUMN notificaciones.error_envio IS 'Detalle del fallo si el envío no fue exitoso.';
COMMENT ON COLUMN notificaciones.created_at IS 'Fecha y hora de generación de la alerta.';
COMMENT ON COLUMN notificaciones.enviada_at IS 'Fecha y hora de confirmación del envío.';

-- ── 5. TABLA: cola_procesamiento ─────────────────────────────────────────────
COMMENT ON TABLE cola_procesamiento IS 'Vista lógica materializada para el control de la cola de triaje clínico.';
COMMENT ON COLUMN cola_procesamiento.id IS 'Identificador único (UUID) en la cola.';
COMMENT ON COLUMN cola_procesamiento.documento_id IS 'ID único de negocio del documento.';
COMMENT ON COLUMN cola_procesamiento.destino IS 'Cola de destino clínico (Emergencia, Rutina, Auditoría).';
COMMENT ON COLUMN cola_procesamiento.nivel_prioridad IS 'Nivel de prioridad del documento.';
COMMENT ON COLUMN cola_procesamiento.score_confianza IS 'Score de confianza asignado.';
COMMENT ON COLUMN cola_procesamiento.status IS 'Estado del documento en la cola de trabajo.';
COMMENT ON COLUMN cola_procesamiento.asignado_a IS 'Usuario o médico a quien fue asignado el documento.';
COMMENT ON COLUMN cola_procesamiento.asignado_at IS 'Fecha y hora de asignación.';
COMMENT ON COLUMN cola_procesamiento.resuelto_at IS 'Fecha y hora de resolución del elemento.';
COMMENT ON COLUMN cola_procesamiento.created_at IS 'Fecha y hora de ingreso a la cola.';
