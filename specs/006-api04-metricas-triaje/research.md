# Research — API-04 (#35)

**Fecha**: 2026-10-10. **Método**: investigación documental/estática, con contraste de fuentes del repositorio y documentación PostgreSQL 17. No conexión a BD, suites, benchmark, instalación, migraciones, regeneración o implementación. La skill solicitó investigación delegada: se realizó una revisión de solo lectura de esquema/seguridad/consulta; consolidada aquí. Las decisiones técnicas son **propuestas para revisión**, no nuevas aprobaciones funcionales ni resultados medidos.

**Estado documental vigente 2026-10-11**: **29/29 tareas acreditadas**, incluidas T022–T029, según ejecución y cierre en `tasks.md`. P04 conserva comprobación práctica PostgreSQL aislado/sesión real, tiempos observados y Scalar manual, «sin retrasos perceptibles» sin SLA numérico; no demuestra rendimiento bajo carga ni en VM de producción. El benchmark/perfil anterior, incluida revisión de 4 GB, queda como antecedente sustituido. R01–R08 y B01/B02/V01/D01/G07 conservan la investigación/propuestas y el estado **histórico** del plan: sus referencias a endpoint inexistente, verificaciones futuras o pendientes no describen el estado aceptado actual. No se presume disponibilidad física futura.

## Fuentes y jerarquía de evidencia

- **Aprobado**: [spec.md](spec.md), FR-001–017/SC-001–009, Q1–Q6/P01–P06 con revisión práctica P04 vigente. Población, colores, HITL, sesiones, tiempo, vacíos/redondeo, contrato sin UI y frescura/coherencia intactos; benchmark/perfil sustituido explícitamente, no dispensas de integración ni puertas. Checklist completo no es evidencia de suites.
- **Obligatorio del repositorio**: `AGENTS.md:10–23,29–47`; `.specify/memory/constitution.md:15–41,47–59,66–98`. TDD, PostgreSQL, solo control manual LOCAL/OCI, contrato generado, preservación de desarrollo y puertas de calidad no se dispensan.
- **Antecedente**: tarea 3.4 en `plan de trabajo/PLAN_DE_TRABAJO_BACKEND_LANGGRAPH.md`, sección Tarea 3.4: asyncpg/documentos/coordinación/router/Scalar/test, pacientes y nodos difieren de decisiones aprobadas. Spec F01 contiene el contraste actualizado de issue #35, separado de la investigación histórica de plan.
- **Hechos**: archivos y migraciones citados abajo. Presencia estática no prueba aplicación Alembic, tablas físicas, población, permisos o servicio PostgreSQL disponible.

## R01 — Recorrido y separación mínima

**Decision (propuesta)**: router nuevo `metrics.py`, repositorio lector nuevo `metrics_repository.py`, registro en main y respuesta mediante modelos generados; sin servicio extra, cliente productivo frontend ni nuevas abstracciones de pool.

**Rationale**: el requisito pide un agregado sin orquestación/IA. El repositorio específico sigue el lector existente de pacientes (`backend/app/repositories/patient_repository.py:27–37,65–75`), separa persistencia y HTTP, y hace posible probar exactamente el SQL. Router/main siguen `backend/app/main.py:14–17,107–116`. El lector mapeará una fila agregada a `MetricsResponse`, no reutilizará el formateador de documentos que sustituye prioridad/tiempo nulos (`backend/app/api/v1/documents.py:86,125`). FR-001/007/008/014; SC-004/005/007.

**Alternatives considered**: todo SQL en router (mezcla persistencia/HTTP); servicio nuevo (sin responsabilidad distinta que justifique archivo); ampliar repositorio de persistencia del triaje (acopla lectura con productores fuera de alcance); ORM (no satisface la restricción asyncpg solicitada). No componentes sin necesidad.

## R02 — Autenticación y 401/503 intactos

**Decision (propuesta)**: `Depends(require_current_user)`, sin `require_roles`, API key alternativa o bypass de sesión. Reutilizar lectura de sesiones existente y handler DB.

**Rationale**: `backend/app/core/security.py:69–92` devuelve 401 sin Bearer/usuario verificable y 503 textual si la validación falla con RuntimeError. `session_repository.py:34–62` exige token hash vigente/no revocado y usuario ACTIVO; no registra escritura de “último acceso”. `require_roles` agrega 403 (`security.py:95–106`), improcedente para Q5. Todo rol con sesión válida/activa entra, incluidos los cinco aprobados; no otorgar permisos de auditoría, usuarios o configuración. El handler `backend/app/main.py:77–91` conserva 503 estructurado `POSTGRESQL_NO_DISPONIBLE` después de autenticar. `ErrorResponse` admite detalle textual/estructurado (`specs/components/schemas.yaml:367–376`). FR-006/007/012; SC-004.

**Alternatives considered**: restringir al administrador/coordinador (reabre Q5); usar X-API-Key (no sesión aprobada); convertir fallo de fuente a 401 (confunde indisponibilidad con invalidez); capturar HTTPException en router y sustituir errores (altera contrato aprobado). Se mantienen ambos 503 distintos, sin inventar un error nuevo.

## R03 — Pool global y consulta solo lectura

**Decision (propuesta)**: reutilizar `get_db_pool` global; pool ausente/adquisición/lectura fallida -> `DatabaseUnavailableError` y handler existente. Una adquisición por cálculo, liberada en todos los caminos. No ping extra ni consultas a configuración.

**Rationale**: `backend/app/repositories/postgres_storage.py:42–63` crea/reutiliza pool asyncpg (1–10 conexiones), convierte URLs y devuelve None al fallar; no configura explícitamente aislamiento/timeout. El pool de instancia de `PostgresStorageRepository.inicializar` (`:109–134`) es otra cosa: no crear uno por petición de métricas. `patient_repository.py:27–37,65–75` aporta patrón de pool requerido y traducción de fallos. Limitar captura de excepciones a frontera PostgreSQL/control de transacción, con mensaje saneado sin SQL/credenciales; no ocultar errores de autenticación ni simulando indicadores. No hay fallback de archivos/memoria ni cambio LOCAL/OCI. FR-007/008; SC-004/007.

**Alternatives considered**: conexión/pool nuevo por request (overhead y patrón innecesario); instancia de storage que consulta modo (efectos/acoplamiento innecesarios); memoria ante fallo (viola fuente única). No se modifica seguridad ni infraestructura de conexión existente.

## R04 — Identidad y deduplicación mediante EXISTS

**Decision (propuesta)**: cohorte sobre documentos con EXISTS de final; evidencia H como OR de bandera y tres EXISTS, cada uno por UUID interno y listas exactas. Un único agregado sin joins expansivos.

**Rationale**: `a3eb75cf454e_initial_schema.py:30–32,65–76` distingue UUID PK de identificador externo UNIQUE y FK legacy. `o8p808522kl4_implement_unified_db_proposal.py:66–80` usa UUID nullable en coordinación; `k4l404288gh0_add_document_traceability.py:39–48` usa UUID obligatorio en historial. Las fuentes admiten repetición. EXISTS conserva una fila por documento y las FK canónicas; COUNT base equivale a documentos externos distintos. La columna texto legacy no se utiliza como respaldo de un UUID mal asociado. No normalizar decisiones ni inventar severidad. Fórmulas/predicados en [data-model.md](data-model.md). FR-002–005/011/016; SC-001/002/003.

**Alternatives considered**: joins crudos y COUNT(DISTINCT) parcial (SUM/AVG/divisores aún pueden inflarse); SUM(DISTINCT tiempo) (elimina tiempos iguales de documentos distintos); relacionar por paciente/episodio (unidad/vínculos incorrectos); solo bandera/coordinación (pierde histórico legacy permitido); Ambiguo=HITL automático (reabre P06). Conjuntos UUID deduplicados unidos al final podrían ser equivalentes, pero no son necesarios como diseño inicial y requieren la misma evidencia de corrección.

## R05 — Snapshot nuevo, coherente y fresco sin caché

**Decision (propuesta)**: transacción nueva READ COMMITTED READ ONLY por petición y **una sentencia SELECT** que obtiene los tres indicadores. No caché de resultados, vistas persistidas/materializadas o refresco.

**Rationale**: SELECT sin escrituras ni bloqueos FOR UPDATE ve un snapshot de datos confirmados al inicio de la sentencia; CTE/subconsultas comparten esa vista. Fuente: [PostgreSQL 17 §13.2.1](https://www.postgresql.org/docs/17/transaction-iso.html#XACT-READ-COMMITTED), consultada 2026-10-10. Aislamiento explícito evita depender del default externo, no configura el pool global. BEGIN/COMMIT son controles adicionales; hay un único fetchrow de cálculo. Petición posterior a COMMIT usa un snapshot nuevo; cambios durante petición pueden incluirse o no, coherentemente. La autenticación es anterior/separada y no integra los tres indicadores. FR-017; SC-009.

**Alternatives considered**: tres consultas bajo READ COMMITTED (snapshots pueden divergir); tres bajo REPEATABLE READ (coherentes si transacción nueva, pero innecesarias); un SELECT autocommit (menor coste, pero aislamiento efectivo no está fijado en código); SERIALIZABLE (complejidad sin necesidad); TTL/materialización (necesita invalidación inmediata adicional); `v_estadisticas_hoy` (`a3eb75cf454e_initial_schema.py:174–186`) filtra un día/cohorte distintos.

**Límite aprobado**: productor de resultados/historial no tiene transacción envolvente (`postgres_storage.py:220–372`); API-04 no modifica productores ni promete atomicidad de sus escrituras. Vista coherente puede incluir parcialidades ya confirmadas según Q4. Prueba aislada hará transición atómica controlada, no corregirá el productor.

## R06 — Aritmética exacta y frontera JSON

**Decision (propuesta)**: SUM original en numeric y COUNT, guardas de población vacía, cociente entero numeric para cuantización final half-up no negativa; publicar números JSON después de cuantizar, conservando None. Detalle/formulación demostrable en [data-model.md](data-model.md).

**Rationale**: tiempo es integer nullable (`a3eb75cf454e_initial_schema.py:58`). La fórmula racional con `div` evita overflow al castear antes de multiplicar, división entera accidental, redondeo bancario de Python y aproximación previa a una fracción periódica. Cuantizar S/T milisegundos es exactamente redondear el resultado final en segundos a tres decimales. asyncpg numeric se adapta como Decimal, pero Pydantic Decimal puede producir strings: la frontera deberá entregar números al schema generado `number | null`, comprobando JSON real. 1/3 HITL=33.33; 1000/2333 ms=1.667; cero no se transforma en null y null nunca se convierte en cero. FR-001/013/014; SC-003/005/008.

**Alternatives considered**: float + round Python (empate hacia par/inexactitud); ROUND numeric tras promedio/división (válido para casos ordinarios, pero mantiene precisión decimal intermedia; el cociente entero explicita exactitud); Decimal.serializado como texto (viola contrato); redondear cada tiempo antes del promedio (altera resultado). No ampliar el contrato con denominadores ni datos individuales.

## R07 — BD-03 disponible estáticamente; cero dependencias o DDL adicionales

**Decision (propuesta)**: apoyarse en esquema actual y cuatro fuentes aprobadas, sin dependencia obligatoria API-02 ni carga BD-04; verificar aplicación/lectura posteriormente en sandbox. Cero migraciones/índices nuevos.

**Rationale (investigación histórica del plan)**: audit_repository/AuditRepository y tests correspondientes acreditan repositorio/dobles; migración `o8p808522kl4_implement_unified_db_proposal.py` define coordinación/trazabilidad y test_migrations verifica SQL offline. Resolución de documents.py escribe legacy; no se promete población de coordinación por presencia de repositorio. Cierre issue/merge previamente contrastado: spec «Dependencia BD-03 y factibilidad», no líneas antiguas; no se verificó live de nuevo en esta investigación.

Los índices declarados se detallan en data-model: coordinación/historial por UUID, legacy por texto externo; no se encontró índice legacy de UUID. Registrar tiempos prácticos, no concluir rendimiento por índices/pool ni extrapolar a carga/producción. Ante retraso perceptible, conservar evidencia y consultar antes de ampliar alcance; cualquier nuevo DDL requiere autorización separada. FR-005/009/015; SC-002/006/007.

**Alternatives considered**: implementar productores/coordinación/API-02 o instrumentar nodos para métricas (fuera de alcance); sembrar BD-04 como prerrequisito (no es cohorte procesada); añadir índices anticipadamente (no hay evidencia que justifique ampliar esquema). No usar `trazabilidad_eventos` como nueva evidencia: no fue aprobada.

## R08 — Contrato modular y prueba TypeScript sin dashboard

**Decision (propuesta)**: contrato de feature [metrics.openapi.yaml](contracts/metrics.openapi.yaml); posteriormente integrarlo al OpenAPI modular y regenerar con herramienta real. Una prueba de consumo en `frontend/src/api/metrics.contract.test.ts`, usando `MetricsResponse` generado y `apiRequest` existente, fuera de pantallas.

**Rationale**: `specs/openapi.yaml:8–10,43–79,80–155` es fuente global modular OAS 3.1, con Bearer; `specs/components/responses.yaml:20–25,38–43` ya documenta 401/503. Futuro schemas nullable requerido y additionalProperties false en raíz/colores. `infrastructure/scripts/generate.py:14–82,85–95` bundlea/valida, usa datamodel-code-generator Pydantic v2 con strict-nullable y openapi-typescript, compila salidas y controla deriva. Herramientas Node reales no se descargan implícitamente (`sdd.py:13–19,37–83`). `Makefile:49–56,128–130` expone validate/generate/check. Se generarán modelos.py, types.ts e index.ts; init.py es salida existente del pipeline, normalmente sin cambios. No modificar generador ni generados manualmente.

Conformidad backend puede extender `backend/tests/test_openapi_contract.py:18–37` (bundle y Draft202012Validator), validando también el modelo generado. La prueba TS cubrirá normal, cero, vacío y no vacío sin tiempo; tipos number/null obligatorios y manejo explícito sin reemplazar null. `tsconfig.app.json:17–27` incluye src, strict/noEmit; `frontend/package.json:8–10` compila/build y Vitest. `backend/tests/test_sdd_pipeline.py:19–45` demuestra patrón real de generación y chequeo TS, no un resultado ejecutado ahora. El genérico de `httpClient.ts:35–57` no valida JSON en runtime: separar conformidad del endpoint de consumo TS.

**Alternatives considered**: tipos duplicados manuales (deriva); adaptar DashboardSummary (fuera de P03); cliente productivo metrics no usado (archivo sin necesidad); convertir null a 0 para UI (altera P01); usar únicamente Vitest sin compilación (no acredita tipado). Dashboard sigue usando su summary (`Dashboard.tsx:8,19–28`, `documentsApi.ts:109–132`); no cambios visuales o conexión.

## R09 — Evidencia aislada y aceptación práctica P04

**Decision (sin nuevo código en esta revisión)**: conservar unitarias con dobles e integración/COMMIT en módulo PostgreSQL aislado; reutilizar fixtures y API/sesiones reales existentes para comprobación práctica. Registrar tiempos monotónicos de cuerpo completo y verificar manualmente Scalar; sin harness de carga nuevo, SLA numérico o volumen fijo. Ejecución futura/evidencia en [quickstart.md](quickstart.md).

**Rationale**: mocks no prueban SQL/FKs/snapshot; `conftest.py:7–14,19–37,52–100` desactiva DATABASE_URL y simula sesiones (no incluye SUPERVISOR). Añadir parametrización local de todos los roles, sin tocar fixture global. Para sesión real, API de sandbox en proceso separado con entorno explícito, fuera del mock; integración debe fallar si se exige y falta sandbox. Patrón de guardas efectivas en `test_seed_hospital_data_postgres.py:59–119`, sin reutilizar sus resets/semilla/BD. `httpx` ya existe en `backend/pyproject.toml:29,53`.

P04 vigente conserva PostgreSQL 17 aislado y sesión real; registrar entorno/recursos/versiones/configuración como contexto, fixtures/oráculo y cada petición efectuada (tiempo, estado, cuerpo sintético, validación, error). Scalar añade valoración manual «sin retrasos perceptibles». No RAM/CPU/SSD obligatorios, VM compartida, fixture 1000/300/200/8000, calentamiento, 500 muestras, cinco clientes, umbral 500 ms ni timeout 5 s de aceptación. No prueba carga/VM de producción; FR-017/SC-009 y guardas intactas. Analyze precede a futura ejecución autorizada; T022–T024 reorientadas a sandbox/fixtures/comprobación, no benchmark. La extracción SSD incompleta no es bloqueo de entrega; se preserva como intento histórico, sin nueva autorización de recursos por esta revisión.

**Alternatives considered**: desarrollo (prohibido), mocks como aceptación real (insuficientes), mantener benchmark como bloqueo (sustituido por usuario; no exigido por issue/tarea), inventar otro SLA (no autorizado), inferir capacidad productiva desde observaciones locales (no demostrado), descartar errores/reintentar ocultándolos (inadmisible). Timeouts operativos que use una herramienta se documentan como configuración, nunca nuevo SLA de aceptación.

**Decisión histórica sustituida**: perfil inicial 4 CPU/8 GB disponibles/SSD, después límite conjunto VM de 4 GB y PostgreSQL/backend juntos con monitorización; fixture 1000/300/200/8000, 20 calentamientos/500 medidas/cinco clientes, ≥475 ≤500 ms/timeout 5 s. No se ejecutó ni acredita rendimiento. Se conserva completo en Clarifications/decisiones históricas de spec y §6 histórico de quickstart; intentos/bloqueos en tasks y evidencia externa, sin borrarlos ni aceptarlos retroactivamente.

## Antecedente histórico — fallos previos, aceptación futura y estado documental del plan

V01/D01/G07 registran lo que estaba pendiente durante plan, no pendientes actuales: la implementación, Scalar y las puertas posteriores acreditaron 29/29 en `tasks.md`. Se conserva el contenido histórico, sin borrar fallos ni sustituir evidencia empírica por documentación.

### B01 — Backend bcrypt

**Estado histórico**: pytest no inició por bcrypt durante specify; spec «Antecedente histórico — verificaciones de specify/clarify» y checklist «Evidencia histórica de specify», punto Backend. No se corrigió en plan; bcrypt sí estaba declarado en backend/pyproject.toml. T001–T021 registran suites posteriores; no es bloqueo actual inferido.

**Comprobación que distingue causas**: registrar executable/version Python, pip show/import bcrypt en el mismo intérprete de pytest y repetir en entorno limpio preparado según manifiesto, fuera de esta tarea. Si ese entorno importa y pytest inicia, comparar entorno anterior; si falla con dependencias presentes/conformes, conservar reproducción del repositorio. Import correcto no equivale a suite verde. No instalar o corregir como entregable API-04.

### B02 — Frontend Tailwind

**Estado histórico**: npm test/build fallaron por `ReferenceError: module is not defined` con Node v22.12.0; spec «Antecedente histórico — verificaciones de specify/clarify» y checklist «Evidencia histórica de specify», punto Frontend. Investigación ESM/CommonJS de aquella revisión, no nueva reproducción. T001–T021 contienen resultados posteriores, sin reparar frontend en API-04.

**Comprobación que distingue causas**: registrar Node/herramientas/configuración y reproducir test/build en entorno limpio compatible con manifiestos/lockfiles, sin editar archivos. Mismo error allí respalda problema de configuración del repositorio; éxito obliga a comparar diferencias de entorno. No eliminar suite, cambiar Tailwind o incluir reparación funcional en API-04.

### V01 — Verificaciones futuras API-04, no fallos previos

- Integración PostgreSQL, Scalar con sesión real, coherencia/frescura, contrato/consumo y P04 se ejecutarán cuando exista implementación comprobable. Su ejecución pendiente no constituye fallo observado ni defecto de completitud documental; **no es requisito previo para generar tasks.md**. Criterios y diseño de validación permanecen íntegros en plan/quickstart, FR-009/010/015/017 y SC-001–009.
- PostgreSQL live, recursos P04, head aplicado, credenciales de sesión real y rendimiento no se comprobaron durante plan. Son prerrequisitos/evidencia de esas ejecuciones futuras, no disponibilidad certificada ni impedimentos documentales al desglose.
- Alembic offline históricamente correcto: spec «Antecedente histórico — verificaciones de specify/clarify» y checklist «Evidencia histórica de specify», punto Alembic. backend/alembic/env.py distingue offline/online; ese antecedente no acredita puerta final ni esquema live.

### D01 — Completitud y coherencia del diseño documental

- Plan, research, data-model, contrato propuesto y quickstart contienen el diseño y validación futura necesarios; sin contradicción nueva que exija modificar Q/P/FR/SC ni incógnitas funcionales que impidan desglosar. Spec/decisiones/diseño técnico no se modifican en esta revisión. La completitud documental no prueba comportamiento implementado ni supera una puerta empírica.
- **Sin impedimento específico para generar tasks.md**, bajo autorización separada. La skill exige plan.md/spec.md y consulta artefactos de diseño (`.agents/skills/speckit-tasks/SKILL.md:59–74`); no pruebas del endpoint ni benchmark previos. El script distingue plan para tasks de plan+tasks para implementación (`.specify/scripts/powershell/check-prerequisites.ps1:42–47,90–110`). Solo se leyeron estas reglas, no se ejecutaron skill/scripts.

### G07 — Puertas de ejecución/cierre intactas, no acreditadas

- **Antes de comenzar implementación**: conservar las verificaciones de `AGENTS.md:16–20`; B01/B02 pendientes impiden acreditar baseline verde. No iniciar código productivo ni reparar entorno en esta revisión. TDD sigue obligatorio (Constitución `:16–19`); no se exige aceptación del endpoint inexistente para redactar su trabajo pendiente.
- **Para finalizar funcionalidad/marcar tareas completadas**: `AGENTS.md:17–20` y Constitución `:16–20,68–86` mantienen pytest/Vitest/build/Alembic y preservación de desarrollo; además, aceptación específica API-04 contra implementación. No excluir pruebas, dispensar warnings ni cerrar tareas con fallos. Tampoco se certifica el cierre formal del plan a partir de su completitud documental.
- **Para desglosar**: no hay regla de las citadas que exija haber ejecutado la aceptación futura antes de escribir tasks.md. Generar tareas no comienza implementación, no marca ninguna completada y no supera puertas de calidad. B01/B02 deben quedar visibles como bloqueos de ejecución/cierre, separados de V01 y D01.

## Diferencias aceptadas con plan y backlog

- **Documentos**, no pacientes: Q1/FR-002. Dos documentos del mismo paciente cuentan dos.
- **Colores de presentación**, no severidad clínica: Q2/FR-003. Ambiguo es incertidumbre, no gravedad intermedia.
- **Promedio del tiempo persistido**, no promedio por nodo/última respuesta IA ni latencia HTTP: Q6/FR-013. No existe instrumentación por nodo acreditada y UPSERT conserva tiempo/nodos (`postgres_storage.py:250–261`; medición `agent/graph.py:121–140`).
- **Compatibilidad de contrato/consumo tipado**, no integración del dashboard: P03/FR-010/SC-008.
- **Aceptación práctica de «sin retrasos perceptibles»**, sin SLA numérico: P04/FR-015/SC-006 con PostgreSQL aislado/sesión real, tiempos observados y Scalar. No demuestra carga ni VM de producción; benchmark previo sustituido, no ejecutado. Frescura/coherencia FR-017/SC-009 intactas.
