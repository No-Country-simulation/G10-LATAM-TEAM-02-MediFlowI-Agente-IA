# Data Model: BD-04 — Semilla hospitalaria

**Fuente**: [Especificación aprobada](spec.md). Diseño sobre tablas existentes; sin DDL, migraciones o cambios de enum.

## Manifiesto estable de la semilla

- Versión lógica: `BD-04/v1`; 10 posiciones de paciente `P01`–`P10`, 4 de usuario `M01`–`M04` y 5 de documento `D01`–`D05`.
- El futuro módulo conservará un manifiesto tipado e inmutable con identidades, atributos ficticios y relaciones. No se usa la fecha de ejecución, aleatoriedad ni el nombre como identidad.
- UUID determinista para cada fila mediante UUIDv5, con un namespace constante exclusivo de BD-04 y nombres de entidad/posición/version. No se modifica la generación global de UUID de las tablas existentes.
- `numero_documento`, `historia_clinica` cuando se provea y `documento_identidad` serán valores sintéticos estables documentados junto con el manifiesto, no los identificadores iniciales de usuarios/documentos introducidos por migraciones. Los DNI de usuario tienen ocho cifras.
- Los documentos tienen `documento_id` legibles y estables `BD04-DOC-001`–`BD04-DOC-005` y UUID internos deterministas. `metadata` contiene solo la marca `seed_source: BD-04` y `seed_version: 1`, sin colores ni edad.
- Los valores concretos de nombres, números de identidad y fechas de nacimiento se fijarán como fixtures sintéticas en la implementación y se documentarán antes de cualquier carga. No constituyen reglas clínicas nuevas ni datos obtenidos de personas reales.
- Reconocimiento de propiedad: para pacientes/usuarios, UUID esperado **y** clave natural esperada; para documentos, además marca de semilla en `metadata`. La coincidencia de nombre o de una sola clave no autoriza apropiarse de una fila ajena. Una discrepancia se informa como conflicto y revierte la carga.

## Pacientes — 10 filas en `pacientes`

- `id`: UUID determinista del manifiesto.
- `tipo_documento`, `numero_documento`: identificación sintética conforme al esquema; clave única por número.
- `historia_clinica`: opcional; si se incluye, única, estable y comprobada también en la detección de conflictos.
- `nombres`, `apellidos`: etiquetas ficticias inequívocas de paciente semilla.
- `fecha_nacimiento`: `DATE` obligatoria en esta semilla, válida y no futura.
- `genero`, `sexo`, contactos: opcionales; si se suministran, respetar valores y compatibilidad vigentes, sin ampliar catálogos ni usar contactos reales. No es necesario rellenarlos para aumentar el alcance de BD-04.
- `created_at`, `updated_at`: gestionados por PostgreSQL; no identifican la semilla.
- **Edad**: no es una columna de pacientes. Se conserva la expresión existente del repositorio `EXTRACT(YEAR FROM age(CURRENT_DATE, fecha_nacimiento))::INT`. La fecha de consulta puede cambiar el resultado sin actualizar la fila.

## Usuarios médicos — 4 filas en `usuarios`

- `id`, `documento_identidad`: UUID y DNI sintéticos estables, distintos entre sí y de las cuentas existentes.
- `nombres`, `apellidos`: etiquetas ficticias de usuario médico semilla.
- `rol`: siempre `OPERADOR`; nunca `MEDICO`, `ADMINISTRADOR` ni `COORDINADOR` para estas cuentas.
- `especialidad_medica`: `M01` Medicina General; `M02` Cardiología; `M03` Neumonología; `M04` Traumatología.
- `estado`: utilizar el default vigente `ACTIVO` al crear cuentas nuevas; no reactivar una cuenta existente modificada por el usuario.
- `password_hash`, `salt`: resultado de `app.core.security.hash_password` para una contraseña recibida de forma segura, validada con la política vigente (12 caracteres, mayúscula, minúscula, número y símbolo). Nunca se fijan hashes/salts públicos ni claves predeterminadas en código.
- Reejecución: conserva el hash, salt y estado existentes; no vuelve a hashear ni restablece contraseñas. La identidad no depende de un salt aleatorio.
- La sesión administradora para consultar `/users` debe existir fuera de esta semilla. No se crea una quinta cuenta.

## Documentos — 5 filas en `documentos_triaje`

- `id`, `documento_id`: identidades estables del manifiesto con las restricciones únicas existentes.
- `tipo_archivo`: `JSON`, valor existente que describe el registro sintético, no la creación de un archivo JSON físico.
- `canal_origen`: default vigente `Admision`.
- `status`: default vigente `recibido`; no se afirma que estos documentos hayan pasado por el agente o por una auditoría real.
- `paciente_id`: FK a uno de los pacientes semilla, resuelta por identidad explícita, nunca por nombre.
- `nivel_prioridad`: fixture sintética con cobertura de `Urgente`, `Rutina` y `Ambiguo` al menos una vez. No se define una equivalencia clínica de severidad ni se exige distribución adicional.
- `paciente_nombre`, `paciente_id_externo`: pueden derivarse del paciente del manifiesto para legibilidad; sin una copia estática de edad.
- `metadata`: marca de propiedad de BD-04; no contiene edad, colores ni diagnósticos inventados.
- `episodio_id`, `paciente_edad`: `NULL`; no hay episodios ni edad persistida.
- `archivo_original`, `resultado_json`, rutas/buckets OCI: no se asignan rutas a objetos inexistentes. No se genera ni sube ningún archivo.
- Campos de diagnóstico, CIE-10, score, estudio y decisión de enrutamiento: no se inventan para completar la semilla; conservar `NULL`/defaults admitidos. `destino_principal` permanece `NULL`, sin ejecutar la orquestación clínica.
- No se llama a `triage_service`, LangGraph ni al adaptador de almacenamiento. No se crean auditorías o notificaciones que aparenten procesamiento real.

## Relaciones, restricciones y reejecución

- Inserción ordenada: pacientes, usuarios y documentos, en una única transacción de la carga. Los documentos apuntan a pacientes existentes del mismo manifiesto.
- Pacientes: reutilizar una fila propia compatible, insertar la ausente y abortar si hay conflicto de UUID, número de documento o historia clínica.
- Usuarios: mismo criterio por UUID y documento de identidad; conservar credenciales, no escribir en sesiones ni cambiar permisos.
- Documentos: `ON CONFLICT (documento_id) DO UPDATE`, limitado a una fila comprobada como propia y compatible. No sustituir UUID/FK, edad, episodio, credenciales o datos de filas ajenas. El diseño conserva los valores existentes compatibles, sin actualización efectiva cuando el contenido ya coincide; una incompatibilidad se trata como conflicto, no como autorización de borrado.
- Resolver el resultado del UPSERT sin cambio mediante consulta por identidad cuando no retorna una fila; no confundirlo con creación fallida.
- `created_at` se conserva. El requisito de idempotencia compara conteos, UUID y relaciones, no exige comparar timestamps afectados por triggers si hubo una actualización real.
- El trigger de cola existente solo actúa si hay destino; con `destino_principal NULL` no se espera crear entradas nuevas. Las pruebas verifican que no aparecen duplicados ni efectos inesperados.
- Prohibidos `DELETE`, truncado, reinicio de tablas, modificaciones de `configuracion_sistema`, migraciones automáticas o escrituras en episodios.

## Estados fuera del alcance

No hay transiciones clínicas nuevas. La semilla prepara registros sintéticos consultables; no implementa ingesta, clasificación, auditoría, derivación, asignación médica ni cierre de episodios.
