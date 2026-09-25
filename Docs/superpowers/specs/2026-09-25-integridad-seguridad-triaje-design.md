# Diseño: integridad, seguridad y procesamiento documental de MediFlow

## Objetivo

Corregir la trazabilidad de las acciones clínicas, proteger los endpoints usados por la interfaz mediante sesiones Bearer y completar el ciclo de vida del documento sin cambiar que PostgreSQL sea la fuente de verdad ni que el modo de almacenamiento LOCAL/OCI sea exclusivamente manual.

## Alcance y entregas

La entrega se divide en tres incrementos que se pueden validar de forma independiente:

1. **Seguridad y trazabilidad.** Bearer para las acciones interactivas, identidad del auditor derivada de sesión, relaciones con `usuarios`, historial funcional y estados de documento completos.
2. **Procesamiento y asociación.** Extracción de texto resiliente para PDFs escaneados, procesamiento por páginas o fragmentos sin un corte fijo de 4.000 caracteres y asociación de pacientes por coincidencia única de DNI o historia clínica.
3. **Normalización gradual.** Separar ambigüedad de prioridad, ampliar el catálogo de documentos y convertir los módulos de interfaz JavaScript a TypeScript sin cambiar el comportamiento visible.

## Arquitectura de seguridad

La interfaz React usará el token entregado por `/api/v1/auth/login` para todos los endpoints operativos: pacientes, triaje, documentos, auditoría y configuración. El token se conservará junto con el usuario autenticado y cada cliente API construirá `Authorization: Bearer <token>`; no se expondrá `VITE_API_KEY` en el navegador.

FastAPI incorporará una dependencia única que valide el esquema Bearer, compruebe la sesión activa y entregue el usuario actual. Las rutas usadas por personas requerirán esa dependencia y verificarán el rol cuando proceda: auditoría HITL requerirá `AUDITOR` o `ADMINISTRADOR`; configuración requerirá `ADMINISTRADOR`. La API Key queda disponible solamente como dependencia separada para integraciones de servidor a servidor, sin ser un mecanismo alternativo silencioso para la UI.

El contrato de `DecisionAuditoriaRequest` no incluirá `auditor_id`. El endpoint toma el UUID desde `current_user["id"]`, lo persiste y lo devuelve como parte de la auditoría registrada.

## Modelo de datos y migración

Una migración Alembic incremental, reversible y con comentarios PostgreSQL hará lo siguiente:

- Amplía `status_documento_enum` con `recibido`, `procesando`, `rechazado` y `no_soportado`; conserva los estados existentes y hace que el valor por defecto de nuevos documentos sea `recibido`.
- Añade `documentos_triaje.usuario_registro_id UUID REFERENCES usuarios(id)` e índice para consultas por cargador.
- Convierte `auditorias_hitl.auditor_id` a UUID con FK a `usuarios(id)`. La migración debe fallar de forma explícita si los registros existentes no pueden mapearse de forma determinista a un usuario; no se inventarán identidades.
- Reemplaza `cola_procesamiento.asignado_a` por `asignado_a_usuario_id UUID REFERENCES usuarios(id)`; se conserva el comportamiento operacional de la tabla y se actualiza su comentario.
- Crea `historial_documento`, con UUID, FK de documento, usuario opcional, evento, estados anterior/nuevo, descripción, metadatos JSONB y fecha. Se añadirán índices por documento y fecha.

Los repositorios escribirán en una transacción el resultado del triaje, la cola y los eventos funcionales. Los eventos mínimos serán `DOCUMENTO_RECIBIDO`, `PROCESAMIENTO_INICIADO`, `PROCESAMIENTO_FINALIZADO`, `PENDIENTE_AUDITORIA`, `AUDITORIA_APROBADA`, `AUDITORIA_RECLASIFICADA`, `AUDITORIA_RECHAZADA` y `PACIENTE_ASOCIADO`.

El flujo HITL queda definido así: aprobar y reclasificar cierran en `procesado`; rechazar cierra en `rechazado`; nunca se usa `error` para una decisión humana válida. Los estados `error` y `no_soportado` solo describen fallos técnicos o formatos no admitidos.

## Procesamiento documental

El nodo de ingreso mantendrá PyMuPDF como primera opción para PDF. Si el texto combinado no alcanza un umbral documentado de caracteres útiles, renderizará sus páginas para OCR con Tesseract. Las imágenes entran directamente al OCR. Si la extracción local continúa insuficiente y hay un proveedor multimodal configurado, se usará como fallback explícito; de lo contrario el documento se deriva a auditoría con una causa trazable, no se clasifica como texto válido.

La extracción preparará fragmentos con límites de caracteres y solapamiento, preservando límites de página. El LLM extraerá datos por fragmento y un consolidado final resolverá campos repetidos: conserva valores coincidentes, prioriza datos identificadores válidos y marca conflictos para auditoría humana. Los límites se configurarán internamente, sin truncar el documento con `[:4000]`.

Para pacientes, se extrae DNI/HC, se consulta PostgreSQL y solo se vincula cuando existe exactamente una coincidencia. Cero o múltiples coincidencias dejan `paciente_id` nulo y generan un evento para la vinculación manual. La vinculación manual existente permanece disponible.

## Normalización y compatibilidad

En el segundo incremento, `nivel_prioridad` quedará limitado a `Urgente` y `Rutina`; la ambigüedad se expresará con `requiere_auditoria_humana` y el motivo de enrutamiento. Como este cambio modifica contratos y datos existentes, se entregará con actualización coordinada de OpenAPI, tests y frontend.

El catálogo de clasificación aceptará: `RECETA_MEDICA`, `INFORME_LABORATORIO`, `INFORME_IMAGENES`, `ORDEN_PROCEDIMIENTO`, `EPICRISIS`, `INFORME_ALTA`, `CERTIFICADO_MEDICO`, `OTRO_CLINICO` y `NO_SOPORTADO`. La migración de `.jsx` a `.tsx` será mecánica por módulo, manteniendo las interfaces tipadas de la API como fuente de contrato.

## Errores y protección de datos

- Una sesión faltante, inválida o expirada retorna 401; un rol sin privilegio retorna 403.
- La configuración OCI sigue devolviendo 400 cuando faltan credenciales y ningún proceso altera `modo_almacenamiento` automáticamente.
- Las operaciones contra PostgreSQL no tendrán fallback de escritura a OCI: la indisponibilidad de la base será un error explícito para preservar la fuente única de verdad.
- La información de diagnóstico no incluirá tokens, contraseñas, API Keys ni contenido clínico completo en logs.

## Verificación

Cada cambio de comportamiento tendrá primero una prueba que falle. Se cubrirán: autenticación Bearer, rechazo de API Key desde la UI, identidad de auditor obtenida de sesión, autorización por rol, transición de estados, filas y FKs nuevas, historial funcional, PDF escaneado, fragmentación de texto y las tres ramas de asociación de paciente.

Al final de cada incremento se ejecutará `pytest`, `npm run build` y `alembic upgrade head` contra una base de pruebas aislada, nunca contra `mediflow_dev`.
