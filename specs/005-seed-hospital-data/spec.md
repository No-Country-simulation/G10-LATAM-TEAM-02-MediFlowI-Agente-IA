# Feature Specification: BD-04 — Datos semilla hospitalarios de desarrollo

**Feature Branch**: No se crea ni cambia una rama en esta fase.

**Created**: 2026-10-07

**Status**: Draft — listo para revisión del usuario; implementación no autorizada.

**Input**: User description: "Especifica solo mi Tarea 1.4 (BD-04): crear un script de datos semilla para desarrollo con 10 pacientes ficticios, 4 usuarios médicos de distintas especialidades y 5 documentos de triaje. Debe ser idempotente: ejecutarlo dos veces no debe duplicar sus registros. Las contraseñas deben usar app.core.security.hash_password y la edad debe calcularse desde fecha_nacimiento, sin guardar una edad fija. Revisa AGENTS.md, el plan de trabajo, el esquema real y el backlog antes de escribir la especificación. Hay tres puntos que debes aclarar conmigo, sin inventar respuestas: si también se deben crear episodios clínicos (solo aparecen en el commit sugerido), cuál será la cuarta especialidad y cómo tratar los colores Rojo/Amarillo/Verde frente a los valores existentes Urgente/Rutina/Ambiguo. Crea una carpeta de especificación nueva sin sobrescribir las existentes y actualiza la referencia de Spec Kit. Detente cuando el spec esté listo para que pueda revisarlo; todavía no implementes ni cargues datos en mediflow_dev."

## User Scenarios & Testing *(mandatory)*

### Momentos de validación

1. **Pruebas automáticas con PostgreSQL aislado**: La futura implementación se valida contra una instancia, base o esquema de pruebas PostgreSQL separado de `mediflow_dev`, con el esquema vigente. Se comprueban la carga 10/4/5, los roles y especialidades, las relaciones, las credenciales, la edad dinámica y dos ejecuciones consecutivas sin duplicados, además de los casos de carga parcial y conservación de datos ajenos. Las pruebas de persistencia e idempotencia requieren PostgreSQL real aislado; las pruebas con mocks no las sustituyen. Ninguna prueba automática carga o modifica `mediflow_dev`.
2. **Ejecución manual y comprobación visual en desarrollo**: Una vez terminado el script y superadas las verificaciones de calidad, el desarrollador podrá ejecutarlo manualmente en la base de desarrollo `mediflow_dev`, como indica el plan de trabajo, y verificar los pacientes y sus edades mediante `GET /api/v1/patients` en Scalar. Los médicos y documentos se comprueban por separado mediante sus consultas existentes. Esta aceptación manual posterior no sustituye las pruebas automáticas aisladas ni autoriza una carga durante `/speckit-specify`.

### User Story 1 - Preparar un conjunto ficticio de desarrollo (Priority: P1)

Como desarrollador de pruebas, quiero preparar manualmente un conjunto identificable de pacientes, médicos y documentos ficticios para consultar los datos y explorar el triaje con las herramientas existentes, sin introducir información de personas reales.

**Why this priority**: Es el objetivo de la Tarea 1.4; proporciona datos reproducibles sin ampliar el flujo clínico ni desarrollar otras tareas del backlog.

**Independent Test**: En pruebas automáticas con PostgreSQL aislado, con el esquema vigente y sin registros de esta semilla, ejecutar la futura carga y consultar sus registros identificados. Deben existir exactamente 10 pacientes, 4 usuarios médicos con rol `OPERADOR` y 5 registros ficticios de `documentos_triaje`, sin archivos físicos; no se exige que esos sean los totales de toda la base. La comprobación manual posterior en desarrollo se describe por separado en los escenarios 6–8.

**Acceptance Scenarios**:

1. **Given** PostgreSQL aislado con las migraciones vigentes y sin esta semilla, **When** la prueba automática ejecuta la futura carga, **Then** se crean 10 pacientes ficticios, 4 usuarios médicos con rol `OPERADOR` y especialidades distintas y 5 registros ficticios en `documentos_triaje`, sin crear episodios clínicos ni generar PDF, imágenes o cualquier otro archivo físico.
2. **Given** los cuatro usuarios semilla en PostgreSQL aislado, **When** la prueba automática consulta sus roles y especialidades, **Then** todos tienen rol `OPERADOR` y hay exactamente uno de Medicina General, uno de Cardiología, uno de Neumonología y uno de Traumatología; no se crea un rol `MEDICO`.
3. **Given** los cinco documentos semilla, **When** se consultan sus prioridades almacenadas en PostgreSQL, **Then** todos usan únicamente `Urgente`, `Rutina` o `Ambiguo`, y los tres valores están representados al menos una vez. Ningún documento guarda Rojo, Amarillo o Verde como prioridad ni como metadato de severidad de esta semilla.
4. **Given** datos existentes ajenos a BD-04, **When** se ejecuta la carga, **Then** no se eliminan ni sobrescriben esos datos y la preferencia de almacenamiento permanece intacta.
5. **Given** documentos semilla con las tres prioridades existentes, **When** se visualizan mediante los indicadores de prioridad ya existentes del frontend, **Then** `Urgente` se presenta en rojo, `Rutina` en verde y `Ambiguo` en amarillo/ámbar, sin almacenar los colores ni modificar el frontend. El amarillo/ámbar de `Ambiguo` expresa incertidumbre documental, no gravedad clínica intermedia.
6. **Given** el script terminado, las verificaciones de calidad superadas, la base de desarrollo `mediflow_dev` disponible, la lista documentada de los 10 números de documento semilla y una sesión válida, **When** el desarrollador ejecuta manualmente el script en desarrollo, abre `/scalar` del backend de desarrollo, autoriza su sesión Bearer y ejecuta `GET /api/v1/patients` sin filtro `search`, **Then** obtiene HTTP 200 y, dentro de `items`, verifica visualmente exactamente los 10 pacientes semilla por `numero_documento`, cada uno una sola vez, con su `fecha_nacimiento` y su `edad` calculada. Para cada uno compara `edad` con los años completos transcurridos desde `fecha_nacimiento` hasta la fecha de referencia vigente del backend, descontando un año si aún no ha ocurrido el cumpleaños. El campo `total` puede incluir otros pacientes y no debe confundirse con el conteo de la semilla. Esta consulta verifica exclusivamente los pacientes y sus edades; no verifica los 4 médicos ni los 5 documentos, ni demuestra por sí sola la ausencia de edad persistida, que se comprueba mediante FR-010 y la historia 3. Este escenario pertenece a la aceptación manual posterior a la implementación, no a la etapa actual de especificación.
7. **Given** la semilla cargada manualmente en desarrollo tras terminar el script, sus 4 documentos de identidad de usuario documentados y una sesión existente con rol `ADMINISTRADOR`, **When** el desarrollador autoriza esa sesión en Scalar y ejecuta por separado `GET /api/v1/users`, **Then** obtiene HTTP 200 y comprueba en el array de usuarios exactamente las 4 cuentas semilla por `documento_identidad`, sin identidades repetidas, todas con rol `OPERADOR` y con un valor de `especialidad_medica` distinto por cuenta: Medicina General, Cardiología, Neumonología y Traumatología. El rol `ADMINISTRADOR` corresponde a la cuenta que consulta, no a los médicos semilla; BD-04 no crea una cuenta administradora adicional. Los demás usuarios no se cuentan como semilla. No se usa `GET /api/v1/patients` como evidencia de existencia de médicos.
8. **Given** la semilla cargada manualmente en desarrollo tras terminar el script, sus 5 identificadores `documento_id` documentados y una sesión válida, **When** el desarrollador ejecuta en Scalar `GET /api/v1/documents/{documento_id}` para cada uno de los 5 identificadores, **Then** recibe cinco respuestas HTTP 200 cuyos `documento_id` coinciden con los solicitados, son distintos entre sí y cuyos valores de `clasificacion.nivel_prioridad` cubren `Urgente`, `Rutina` y `Ambiguo`. Se comprueban registros ficticios persistidos en PostgreSQL, no archivos PDF, imágenes ni descargas físicas. Puede consultar adicionalmente `GET /api/v1/documents`, pero su lista limitada y su `total` no sustituyen las cinco consultas por identidad ni prueban el total de documentos almacenados. No se usa `GET /api/v1/patients` como evidencia de existencia de documentos. La no duplicación después de repetir la carga se valida automáticamente con PostgreSQL aislado en la historia 2.

---

### User Story 2 - Repetir la carga sin duplicar registros (Priority: P1)

Como desarrollador de pruebas, quiero poder ejecutar nuevamente la semilla sin multiplicar pacientes, usuarios o documentos, incluso si una parte del conjunto ya existe.

**Why this priority**: La repetibilidad segura es un criterio explícito del usuario y del backlog BD-04.

**Independent Test**: Una prueba automática ejecuta dos veces la futura carga sobre el mismo PostgreSQL aislado y compara cantidades, identidades y relaciones de los registros semilla, sin borrar datos ni hacer rollback entre ambas ejecuciones. La limpieza o reversión del entorno de pruebas se realiza después de comprobar el resultado de la segunda ejecución; `mediflow_dev` no participa en esta prueba.

**Acceptance Scenarios**:

1. **Given** una primera carga completada en PostgreSQL aislado, **When** la prueba automática ejecuta la carga por segunda vez sin borrar ni revertir los registros de la primera, **Then** el conjunto mantiene exactamente 10 pacientes, 4 usuarios médicos con rol `OPERADOR` y 5 registros de `documentos_triaje`, con las mismas identidades y sin duplicados.
2. **Given** que solo existe parte del conjunto semilla y no hay conflictos con datos ajenos, **When** se ejecuta la carga, **Then** se completa el conjunto hasta 10/4/5, reutilizando las identidades existentes.
3. **Given** relaciones existentes entre documentos semilla y pacientes semilla, **When** se repite la carga, **Then** las relaciones siguen siendo válidas y no se generan pacientes de reemplazo.
4. **Given** un identificador reservado para la semilla ocupado por un registro ajeno o una historia clínica incompatible, **When** se detecta la colisión, **Then** se informa el conflicto sin convertir ese registro en dato semilla, borrarlo ni sobrescribirlo.

---

### User Story 3 - Consultar datos seguros y edades vigentes (Priority: P2)

Como desarrollador de pruebas, quiero que las cuentas ficticias usen el mecanismo de seguridad vigente y que la edad de los pacientes se obtenga de su fecha de nacimiento para evitar credenciales inseguras y edades desactualizadas.

**Why this priority**: Son restricciones obligatorias del usuario, de la Constitución y del esquema existente.

**Independent Test**: Mediante pruebas automáticas con PostgreSQL aislado, verificar las credenciales de las cuatro cuentas con el mecanismo existente, revisar que no hay contraseñas en claro persistidas y consultar la edad de un paciente antes y el día de su cumpleaños usando fechas controladas, sin modificar `mediflow_dev`.

**Acceptance Scenarios**:

1. **Given** cuatro contraseñas de desarrollo provistas de forma segura, **When** se crean las cuentas semilla, **Then** cada cuenta conserva un hash y su salt compatibles con la verificación vigente; no se guarda ni muestra la contraseña en claro en datos persistidos o salidas de la carga.
2. **Given** un paciente semilla con fecha de nacimiento conocida, **When** se consulta su edad antes de su cumpleaños y el día de su cumpleaños, **Then** la edad corresponde a los años cumplidos y aumenta en uno sin recargar la semilla ni actualizar una edad almacenada.
3. **Given** el campo legado de edad en los documentos, **When** se cargan los cinco documentos, **Then** la semilla no guarda allí una edad fija ni la replica como edad persistida dentro de sus metadatos o resultados; la fuente de la edad es la fecha de nacimiento del paciente.

### Edge Cases

- Base previamente poblada, incluso con documentos y usuarios creados por migraciones: los conteos 10/4/5 corresponden exclusivamente a esta nueva semilla; no se vacían tablas para lograr esos conteos.
- Conjunto parcialmente presente: se completa sin duplicar registros ya reconocidos como semilla.
- Colisión de documento de identidad, número de documento, historia clínica o identificador de documento con datos ajenos: se informa el conflicto sin sobreescritura destructiva ni vinculación por nombre.
- Fecha de nacimiento futura, inválida o ausente en un paciente semilla: no cumple el requisito de edad dinámica; la carga debe informar el dato inválido, no sustituirlo por una edad fija.
- Cambio de fecha de consulta, cumpleaños o nacimiento en año bisiesto: se respeta el cálculo vigente de años cumplidos, sin inventar una regla de edad alternativa.
- Base inaccesible o esquema requerido ausente: se informa el error y no se reporta una carga exitosa ni se aplica automáticamente una migración o un almacenamiento alternativo.
- Salt aleatorio en el mecanismo de contraseñas: la no duplicación se verifica por identidad de registros, no por exigir que una nueva llamada al hashing produzca bytes idénticos.
- Efectos de triggers existentes sobre la cola: no deben provocar duplicación de entradas correspondientes a los documentos semilla al repetir la carga.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: BD-04 DEBE proporcionar una carga manual de datos semilla exclusivamente para desarrollo, con un conjunto estable y reconocible de 10 pacientes ficticios, 4 usuarios médicos y 5 documentos de triaje.
- **FR-002**: Los 10 pacientes DEBEN tener identificación única, nombres y apellidos ficticios y una fecha de nacimiento válida que permita calcular su edad. Los datos de contacto, cuando se incluyan, DEBEN ser ficticios; no se reutiliza información clínica o identificativa real.
- **FR-003**: Los 4 usuarios médicos DEBEN tener rol `OPERADOR`, existente en el sistema, identidades distintas y una especialidad clínica no vacía, con exactamente uno por especialidad: `Medicina General`, `Cardiología`, `Neumonología` y `Traumatología`. Se DEBEN respetar los estados ya admitidos, sin crear un rol `MEDICO` ni ampliar permisos de auditoría.
- **FR-004**: Los 5 documentos DEBEN ser registros ficticios de `documentos_triaje` en PostgreSQL, tener identificadores estables y únicos, asociarse a pacientes del conjunto semilla mediante la relación existente y respetar campos obligatorios, restricciones y valores admitidos por el esquema vigente. La semilla NO DEBE generar PDF, imágenes ni ningún archivo físico, ni subir objetos a OCI. El conjunto DEBE representar `Urgente`, `Rutina` y `Ambiguo` al menos una vez cada uno; no se exige una distribución adicional entre los dos documentos restantes.
- **FR-005**: BD-04 NO DEBE crear ni modificar episodios clínicos. Los nuevos documentos semilla DEBEN dejar sin asignar su relación opcional con episodio. Tampoco se implementa la creación automática de episodios del servicio de triaje.
- **FR-006**: BD-04 DEBE guardar en PostgreSQL únicamente las prioridades existentes `Urgente/Rutina/Ambiguo`, sin modificar el enum ni añadir colores como datos persistidos de prioridad o severidad. Los colores se mencionan exclusivamente como presentación visual ya existente en el frontend: `Urgente` → rojo, `Rutina` → verde y `Ambiguo` → amarillo/ámbar. Esta correspondencia visual NO introduce una clasificación clínica nueva ni exige cambios de frontend; `Ambiguo` sigue significando incertidumbre documental o baja confianza, nunca gravedad intermedia.
- **FR-007**: Dos ejecuciones consecutivas sobre el mismo entorno DEBEN dejar exactamente un registro por identidad semilla y mantener el conjunto 10/4/5, sin regenerar identidades ni duplicar sus relaciones. Una carga parcial existente DEBE poder completarse sin borrar registros.
- **FR-008**: La carga DEBE distinguir sus registros de los ajenos, conservar datos preexistentes fuera de la semilla y comunicar colisiones de identidad incompatibles sin sobrescribir ni eliminar dichos datos.
- **FR-009**: Las contraseñas de las cuentas semilla DEBEN almacenarse exclusivamente mediante el mecanismo vigente de hashing y salt, cumplir la política de seguridad existente y poder verificarse con ella. NO DEBEN persistirse contraseñas en claro ni publicarse secretos en el repositorio o en salidas del script.
- **FR-010**: La edad DEBE calcularse en cada consulta desde `fecha_nacimiento` y la fecha de referencia de consulta, siguiendo el comportamiento vigente de años cumplidos. La semilla NO DEBE guardar una edad fija, incluida la columna legada `documentos_triaje.paciente_edad` o copias en metadatos/resultados, ni añadir una columna de edad a pacientes.
- **FR-011**: La carga NO DEBE alterar `configuracion_sistema` ni cambiar la elección manual `LOCAL/OCI`. La ausencia de conectividad NO autoriza persistencia clínica alternativa ni activación automática de OCI.
- **FR-012**: La futura ejecución DEBE estar documentada para el desarrollador, junto con las identidades estables de los 10 pacientes, 4 médicos y 5 documentos, cómo consultar cada conjunto mediante las herramientas existentes y cómo reconocer éxito, error o conflicto, sin exponer credenciales. La verificación manual en Scalar DEBE distinguir `GET /api/v1/patients` para pacientes y edades calculadas, `GET /api/v1/users` con rol `ADMINISTRADOR` para médicos y `GET /api/v1/documents/{documento_id}` para cada documento, siguiendo los escenarios 6–8 de la historia 1. Ningún conteo general o respuesta limitada se DEBE confundir con el conteo de registros semilla.
- **FR-013**: La futura validación DEBE separar dos momentos: **(a)** pruebas automáticas con PostgreSQL real aislado, sin mutar `mediflow_dev`, que cubran primera carga, segunda carga consecutiva sin duplicados, conjunto parcial, conservación de datos ajenos, roles y especialidades, integridad de relaciones, verificación de contraseñas, edad dinámica y ausencia de archivos físicos generados; **(b)** una vez terminado el script y superadas las verificaciones de calidad, ejecución manual por el desarrollador en `mediflow_dev` y comprobación visual de los 10 pacientes y sus edades mediante `GET /api/v1/patients` en Scalar, como exige el plan de trabajo, con consultas separadas para médicos y documentos. Documentar el segundo momento NO autoriza ejecutarlo durante `/speckit-specify`.

### Key Entities *(include if feature involves data)*

- **Paciente ficticio**: Persona sintética identificada de forma única, con nombres, apellidos y fecha de nacimiento; la edad es un dato calculado, no almacenado.
- **Usuario médico ficticio**: Cuenta de desarrollo con rol `OPERADOR`, identidad, especialidad clínica y credenciales protegidas; el perfil clínico no introduce un rol `MEDICO`.
- **Documento de triaje ficticio**: Registro único de `documentos_triaje` en PostgreSQL vinculado a un paciente semilla, con prioridad admitida y datos compatibles con el esquema vigente; no implica un PDF, imagen o archivo físico ni se asocia a un episodio creado por BD-04.
- **Conjunto semilla BD-04**: Colección identificable de 10/4/5 registros cuyos identificadores permiten reconocerlos entre ejecuciones y separarlos de registros ajenos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En un entorno válido sin esta semilla, una ejecución explícita deja consultables exactamente 10 pacientes ficticios, 4 usuarios médicos y 5 documentos del conjunto.
- **SC-002**: Después de dos ejecuciones consecutivas, se mantienen los conteos 10/4/5 y el 100% de las identidades y relaciones del conjunto, con cero registros duplicados.
- **SC-003**: El 100% de los usuarios semilla tiene rol `OPERADOR`, una de las cuatro especialidades acordadas, sin repeticiones, y credenciales verificables sin contraseñas en claro persistidas.
- **SC-004**: El 100% de los pacientes semilla tiene una fecha de nacimiento válida y una edad consultable correcta; el caso de cumpleaños demuestra el cambio de edad sin actualizar datos persistidos de edad.
- **SC-005**: Los cinco documentos almacenan solo las tres prioridades acordadas, con cobertura de las tres, cero colores persistidos como prioridad o severidad y cero episodios generados por la carga. Los indicadores visuales existentes distinguen `Urgente` en rojo, `Rutina` en verde y `Ambiguo` en amarillo/ámbar, conservando el significado de incertidumbre de este último.
- **SC-006**: Una carga repetida o con datos semilla parcialmente existentes conserva el 100% de los registros ajenos y mantiene sin cambios la preferencia de almacenamiento.
- **SC-007**: La semilla genera cero archivos físicos; los cinco documentos son exclusivamente registros ficticios consultables.
- **SC-008**: La aceptación futura cuenta con dos evidencias separadas: prueba automática aislada que demuestra dos cargas consecutivas sin duplicados y comprobación visual manual posterior en desarrollo que identifica los 10 pacientes y verifica sus edades calculadas. Ambas evidencias se obtienen después de la implementación, no durante esta especificación.

## Assumptions

### Decisiones confirmadas por el usuario (2026-10-07)

- **Q1 — Episodios**: «Sin episodios». La mención de episodios en el commit sugerido no amplía el alcance.
- **Q2 — Cuarta especialidad**: «Traumatología», junto con Medicina General, Cardiología y Neumonología del backlog.
- **Q3 — Prioridades y colores**: «Solo valores existentes», precisado posteriormente por el usuario: se guardan `Urgente/Rutina/Ambiguo` en PostgreSQL. Los colores solo describen la presentación existente del frontend: rojo para `Urgente`, verde para `Rutina` y amarillo/ámbar para `Ambiguo`. No se persisten colores ni se cambia el esquema o el frontend; `Ambiguo` representa incertidumbre, no gravedad intermedia.
- **Rol de los médicos**: Los cuatro usuarios semilla tendrán rol `OPERADOR`; las cuatro especialidades acordadas son distintas y no se crea un rol `MEDICO`.
- **Naturaleza de los documentos**: Los cinco documentos serán registros ficticios de `documentos_triaje` en PostgreSQL; no se generan PDF, imágenes ni archivos físicos.
- **Validación en dos momentos**: Primero pruebas automáticas con PostgreSQL aislado, incluida la reejecución sin duplicados; después, con el script terminado y verificado, ejecución manual en desarrollo y comprobación visual de pacientes en Scalar. Ninguna carga en desarrollo se ejecuta en la etapa actual.
- No se infieren reglas clínicas, diagnósticos, equivalencias de severidad ni umbrales nuevos. Los atributos opcionales no solicitados no se convierten en requisitos adicionales.

### Dependencias y restricciones explícitas

- Se requiere el esquema hospitalario vigente. PostgreSQL sigue siendo la fuente de verdad de los metadatos; no se depende de ejecutar el agente IA para sembrar registros.
- El artefacto futuro solicitado por el plan y el backlog es `backend/app/scripts/seed_hospital_data.py`, ejecutable manualmente como `python -m app.scripts.seed_hospital_data`. Esta ruta y comando son restricciones heredadas, no archivos ni comandos ejecutados en esta fase.
- Por petición expresa, el mecanismo obligatorio es `app.core.security.hash_password`, que retorna `(password_hash, salt)`; ambos corresponden a campos existentes de `usuarios`. No se sustituye por un algoritmo o helper inventado.
- Identidades únicas ya verificadas en migraciones: `pacientes.numero_documento`, `pacientes.historia_clinica` cuando se provea, `usuarios.documento_identidad` y `documentos_triaje.documento_id`. Los usuarios exigen documento de identidad de ocho cifras. La regla vigente para documentos exige UPSERT por `documento_id`; la política no autoriza sobrescribir datos ajenos ante colisiones.
- `pacientes` no tiene columna física de edad. El repositorio calcula la edad desde `fecha_nacimiento`. `documentos_triaje` sí conserva un campo legado nullable `paciente_edad`, que esta semilla no debe rellenar con una edad fija; eliminarlo globalmente queda fuera de BD-04.
- La relación `documentos_triaje.episodio_id` es opcional. Excluir episodios es compatible con el esquema actual.
- No se crean migraciones, endpoints, contratos nuevos, repositorios adicionales, funcionalidades de auditoría, métricas ni cambios de frontend como parte de esta especificación. La semilla no genera archivos físicos PDF/imagen ni de otro tipo, ni sube objetos a OCI.
- Las reglas de calidad del repositorio siguen vigentes para la implementación posterior: pruebas backend y frontend en verde, compilación limpia y validación de migraciones offline, sin mutar `mediflow_dev`. Validar documentos en esta fase no implica que BD-04 esté implementada ni que sus pruebas de aceptación ya hayan sido ejecutadas.
- Esta entrega solo crea la especificación y su checklist en una carpeta nueva y actualiza `.specify/feature.json`. No implementa el script, no ejecuta la semilla, no aplica migraciones y no carga datos en `mediflow_dev`; se detiene para revisión humana.
- Los escenarios manuales de Scalar son instrucciones de aceptación posteriores a terminar y verificar el script, para la base de desarrollo; las pruebas automáticas usan PostgreSQL aislado. Ninguno de esos momentos se ejecuta durante `/speckit-specify`. Esta revisión modifica solo `spec.md` y su checklist; no cambia la referencia de Spec Kit ni crea `plan.md`.

### Fuentes revisadas y trazabilidad

- [AGENTS.md](../../AGENTS.md): Regla de Oro, almacenamiento manual, identificadores únicos, UPSERT, consulta obligatoria y verificaciones sin mutar desarrollo.
- [Constitución 1.2.0](../../.specify/memory/constitution.md): edad dinámica, seguridad/RBAC, consulta obligatoria y aislamiento de pruebas.
- [Plan de trabajo, Tarea 1.4](../../plan%20de%20trabajo/PLAN_DE_TRABAJO_BACKEND_LANGGRAPH.md): objetivo 10/4/5, ruta del script y helper de contraseñas.
- [Backlog BD-04, issue #27](https://github.com/No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/issues/27), consultado el 2026-10-07: cantidades, tres especialidades enumeradas, edad dinámica, idempotencia y discrepancia del commit sugerido sobre episodios. El archivo local `Docs/backlog.md` mencionado por herramientas históricas no existe; se revisó la issue oficial, no se inventó contenido local.
- [Propuesta aprobada de BD](../../Docs/PROPUESTA_NUEVA_BASE_DE_DATOS.md): ficha de paciente, especialidad y significado de los perfiles existentes.
- Esquema del repositorio contrastado en migraciones [inicial](../../backend/alembic/versions/a3eb75cf454e_initial_schema.py), [usuarios](../../backend/alembic/versions/h1i202255de7_add_auth_and_user_management.py), [pacientes](../../backend/alembic/versions/i2j302266ef8_add_pacientes_table.py), [trazabilidad documental](../../backend/alembic/versions/k4l404288gh0_add_document_traceability.py) y [modelo unificado](../../backend/alembic/versions/o8p808522kl4_implement_unified_db_proposal.py). No se afirma haber inspeccionado ni modificado la instancia activa de desarrollo.
- [Contrato vigente de prioridades](../components/schemas.yaml), [repositorio de pacientes](../../backend/app/repositories/patient_repository.py), [seguridad](../../backend/app/core/security.py), [validación de usuarios](../../backend/app/api/v1/users.py) y [guía de secretos](../../GUIA_SECRETOS_Y_VARIABLES_ENTORNO.md): compatibilidad de prioridades, edad calculada y credenciales.
- [Indicador de prioridad existente del frontend](../../frontend/src/components/triage/PriorityBadge.tsx): presentación visual mediante rojo (`Urgente`), verde (`Rutina`) y amarillo/ámbar (`Ambiguo`), revisada en modo lectura para respaldar la precisión de Q3, sin modificar código.
- [Listado vigente de pacientes](../../backend/app/api/v1/patients.py), [listado de usuarios](../../backend/app/api/v1/users.py) y [consultas de documentos](../../backend/app/api/v1/documents.py): formas de respuesta, campos de identificación y permisos revisados en modo lectura para especificar la aceptación en Scalar sin atribuir al listado de pacientes la verificación de médicos o documentos.
