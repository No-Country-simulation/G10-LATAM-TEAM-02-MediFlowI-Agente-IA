"""add_database_comments

Revision ID: g9h001143cd6
Revises: f8g990032bc5
Create Date: 2026-09-24 22:23:00

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'g9h001143cd6'
down_revision: Union[str, Sequence[str], None] = 'f8g990032bc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Añade comentarios descriptivos a todas las tablas y columnas en PostgreSQL."""
    # 1. documentos_triaje
    op.execute("COMMENT ON TABLE documentos_triaje IS 'Resultado completo del triaje de cada documento clinico procesado por el agente autonomo.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.id IS 'Identificador unico (UUID) del registro de triaje.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.documento_id IS 'ID unico de negocio del documento (ej. DOC-776123).'")
    op.execute("COMMENT ON COLUMN documentos_triaje.tipo_archivo IS 'Formato de entrada del archivo (PDF, IMAGEN, TEXTO, JSON).'")
    op.execute("COMMENT ON COLUMN documentos_triaje.canal_origen IS 'Canal o sistema emisor del documento (ej. Guardia_Emergencias).'")
    op.execute("COMMENT ON COLUMN documentos_triaje.status IS 'Estado del procesado (procesado, error, pendiente_auditoria).'")
    op.execute("COMMENT ON COLUMN documentos_triaje.texto_extraido IS 'Texto completo extraido del informe medico.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.tipo_documento IS 'Clasificacion del tipo de documento clinico (ej. Angio-TAC, Laboratorio).'")
    op.execute("COMMENT ON COLUMN documentos_triaje.especialidad IS 'Especialidad medica relacionada.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.nivel_prioridad IS 'Nivel de urgencia determinado por el agente (Urgente, Rutina, Ambiguo).'")
    op.execute("COMMENT ON COLUMN documentos_triaje.score_confianza IS 'Score de confianza de la clasificacion entre 0.0 y 1.0.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.paciente_nombre IS 'Nombre del paciente extraido del documento.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.paciente_edad IS 'Edad del paciente en anos.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.paciente_id_externo IS 'DNI, Historia Clinica o identificador externo del paciente.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.medico_nombre IS 'Nombre del medico solicitante.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.medico_matricula IS 'Matricula o registro profesional del medico.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.estudio_realizado IS 'Nombre del estudio o prueba medica analizada.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.diagnostico_principal IS 'Diagnostico o impresion clinica principal.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.cie10_sugerido IS 'Codigo CIE-10 sugerido por el modelo de IA.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.hallazgos_clave IS 'Array de hallazgos clinicos relevantes en formato JSONB.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.destino_principal IS 'Cola de destino asignada por enrutamiento.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.requiere_auditoria_humana IS 'Indica si requiere intervencion medica (Human-in-the-Loop).'")
    op.execute("COMMENT ON COLUMN documentos_triaje.justificacion_enrutamiento IS 'Explicacion del razonamiento del agente para la decision.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.notificacion_generada IS 'Objeto JSONB con el detalle de la alerta de urgencia generada.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.storage_provider IS 'Proveedor de almacenamiento activo (LOCAL u OCI).'")
    op.execute("COMMENT ON COLUMN documentos_triaje.archivo_original IS 'Ruta o Key del archivo original guardado.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.resultado_json IS 'Ruta o Key del JSON de resultado guardado.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.nombre_original IS 'Nombre del archivo original enviado por el cliente.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.oci_bucket IS 'Nombre del bucket de Oracle Cloud Object Storage.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.oci_ruta_objeto IS 'Ruta/Key del objeto guardado en OCI.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.oci_status IS 'Estado del almacenamiento en OCI (exito, error, pendiente).'")
    op.execute("COMMENT ON COLUMN documentos_triaje.nodos_ejecutados IS 'Secuencia de nodos ejecutados en el grafo de LangGraph.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.tiempo_procesamiento_ms IS 'Tiempo de procesamiento del triaje en milisegundos.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.metadata IS 'Metadatos contextuales adicionales del proceso.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.error_mensaje IS 'Mensaje de error en caso de fallo durante la ejecucion.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.created_at IS 'Fecha y hora de creacion del registro.'")
    op.execute("COMMENT ON COLUMN documentos_triaje.updated_at IS 'Fecha y hora de ultima modificacion del registro.'")

    # 2. auditorias_hitl
    op.execute("COMMENT ON TABLE auditorias_hitl IS 'Registro de decisiones de auditoria humana (Human-in-the-Loop) sobre documentos ambiguos.'")
    op.execute("COMMENT ON COLUMN auditorias_hitl.id IS 'Identificador unico (UUID) de la auditoria.'")
    op.execute("COMMENT ON COLUMN auditorias_hitl.documento_triaje_id IS 'Referencia FK al documento en la tabla documentos_triaje.'")
    op.execute("COMMENT ON COLUMN auditorias_hitl.documento_id IS 'ID de negocio del documento auditado.'")
    op.execute("COMMENT ON COLUMN auditorias_hitl.decision IS 'Decision del auditor medico (aprobar, rechazar, reclasificar).'")
    op.execute("COMMENT ON COLUMN auditorias_hitl.auditor_id IS 'Identificador o usuario del medico auditor.'")
    op.execute("COMMENT ON COLUMN auditorias_hitl.comentario IS 'Justificacion u observaciones registradas por el auditor.'")
    op.execute("COMMENT ON COLUMN auditorias_hitl.nueva_nivel_prioridad IS 'Nueva prioridad asignada si fue reclasificado.'")
    op.execute("COMMENT ON COLUMN auditorias_hitl.nuevo_destino IS 'Nuevo destino asignado si fue reclasificado.'")
    op.execute("COMMENT ON COLUMN auditorias_hitl.nuevo_tipo_documento IS 'Nuevo tipo de documento si fue corregido por el auditor.'")
    op.execute("COMMENT ON COLUMN auditorias_hitl.created_at IS 'Fecha y hora de la auditoria.'")

    # 3. configuracion_sistema
    op.execute("COMMENT ON TABLE configuracion_sistema IS 'Almacena la configuracion global persistente del sistema.'")
    op.execute("COMMENT ON COLUMN configuracion_sistema.clave IS 'Clave identificadora del parametro (ej. modo_almacenamiento).'")
    op.execute("COMMENT ON COLUMN configuracion_sistema.valor IS 'Valor configurado activo (ej. LOCAL u OCI).'")
    op.execute("COMMENT ON COLUMN configuracion_sistema.descripcion IS 'Descripcion del proposito del parametro.'")
    op.execute("COMMENT ON COLUMN configuracion_sistema.updated_at IS 'Fecha y hora del ultimo cambio de configuracion.'")

    # 4. notificaciones
    op.execute("COMMENT ON TABLE notificaciones IS 'Alertas generadas automaticamente para casos de urgencia medica.'")
    op.execute("COMMENT ON COLUMN notificaciones.id IS 'Identificador unico (UUID) de la notificacion.'")
    op.execute("COMMENT ON COLUMN notificaciones.documento_triaje_id IS 'Referencia FK al documento en documentos_triaje.'")
    op.execute("COMMENT ON COLUMN notificaciones.documento_id IS 'ID de negocio del documento.'")
    op.execute("COMMENT ON COLUMN notificaciones.canal IS 'Canal de alerta asignado (ej. Guardia_Emergencias).'")
    op.execute("COMMENT ON COLUMN notificaciones.mensaje IS 'Mensaje de la alerta clinica.'")
    op.execute("COMMENT ON COLUMN notificaciones.enviada IS 'Flag de confirmacion de envio.'")
    op.execute("COMMENT ON COLUMN notificaciones.error_envio IS 'Detalle del fallo si el envio no fue exitoso.'")
    op.execute("COMMENT ON COLUMN notificaciones.created_at IS 'Fecha y hora de generacion de la alerta.'")
    op.execute("COMMENT ON COLUMN notificaciones.enviada_at IS 'Fecha y hora de confirmacion del envio.'")

    # 5. cola_procesamiento
    op.execute("COMMENT ON TABLE cola_procesamiento IS 'Vista logica materializada para el control de la cola de triaje clinico.'")
    op.execute("COMMENT ON COLUMN cola_procesamiento.id IS 'Identificador unico (UUID) en la cola.'")
    op.execute("COMMENT ON COLUMN cola_procesamiento.documento_id IS 'ID unico de negocio del documento.'")
    op.execute("COMMENT ON COLUMN cola_procesamiento.destino IS 'Cola de destino clinico (Emergencia, Rutina, Auditoria).'")
    op.execute("COMMENT ON COLUMN cola_procesamiento.nivel_prioridad IS 'Nivel de prioridad del documento.'")
    op.execute("COMMENT ON COLUMN cola_procesamiento.score_confianza IS 'Score de confianza asignado.'")
    op.execute("COMMENT ON COLUMN cola_procesamiento.status IS 'Estado del documento en la cola de trabajo.'")
    op.execute("COMMENT ON COLUMN cola_procesamiento.asignado_a IS 'Usuario o medico a quien fue asignado el documento.'")
    op.execute("COMMENT ON COLUMN cola_procesamiento.asignado_at IS 'Fecha y hora de asignacion.'")
    op.execute("COMMENT ON COLUMN cola_procesamiento.resuelto_at IS 'Fecha y hora de resolucion del elemento.'")
    op.execute("COMMENT ON COLUMN cola_procesamiento.created_at IS 'Fecha y hora de ingreso a la cola.'")


def downgrade() -> None:
    """Elimina los comentarios de las tablas y columnas."""
    pass
