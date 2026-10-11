# Implementation Plan: API-04 (#35) — Métricas hospitalarias de triaje

**Branch**: `dev-krystopher` (conservada) | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-api04-metricas-triaje/spec.md` y autorización explícita de investigación/diseño, sin tasks/implement.

**Status**: Aceptado — **29/29 tareas acreditadas**; [tasks.md](tasks.md) es el registro de ejecución, puertas y cierre. P04 práctica vigente: PostgreSQL aislado/sesión real, tiempos observados y Scalar manual, «sin retrasos perceptibles» sin SLA numérico; sin benchmark/recursos fijos ni demostración de rendimiento bajo carga o en la VM de producción. Las fases, propuestas, fallos, endpoint ausente y pendientes descritos en este plan son antecedentes históricos, no pendientes actuales. La evidencia fechada no presume disponibilidad futura del entorno.

**Preparación comprobada**: `.specify/feature.json:2` apuntaba a esta feature antes de ejecutar `setup-plan.ps1 -Json`. El script copió la plantilla efectiva `.specify/templates/plan-template.md`, sin alterar rama ni documentos previos (`setup-plan.ps1:36–56`). Su JSON devolvió FEATURE_SPEC/IMPL_PLAN/SPECS_DIR de esta carpeta y BRANCH=`006-api04-metricas-triaje`; este último es el identificador de feature fallback (`common.ps1:215–224`), **no un cambio de rama Git**. La rama Git observada es `dev-krystopher`. No existe `.specify/extensions.yml` en las revisiones previa/posterior; no hay hooks que ejecutar. No se ejecutan otras etapas, commit, push o PR.

## Summary

Diseñar `GET /api/v1/metrics` autenticado, de solo lectura, con tres raíces exactas: distribución por colores de presentación, porcentaje histórico HITL y promedio del tiempo persistido admisible en segundos. Conservar Q1–Q6/P01–P06 sin reabrir reglas.

Propuesta: router delgado y repositorio específico que reutiliza pool global asyncpg; una transacción nueva READ COMMITTED READ ONLY ejecuta una sentencia agregada con EXISTS sobre documentos/coordinación más legacy/historial. Deduplicación estructural por documento, snapshot común, sin caché de resultados, redondeo final exacto y errores existentes. Contrato propuesto local y validación posterior de generación/consumo TypeScript sin dashboard. Investigación y alternativas en [research.md](research.md); datos/fórmulas en [data-model.md](data-model.md); ejecución futura en [quickstart.md](quickstart.md).

### Trazabilidad y diferencias aceptadas

- **Decisiones aprobadas**: [spec.md](spec.md), por IDs FR-001–017/SC-001–009 y sección Clarifications, no por líneas desplazables. C FR-011, H FR-016, promedio FR-013, null/cero/redondeo FR-014, acceso FR-006/012, contrato FR-010 y aceptación práctica/frescura FR-015/017. El endpoint no inventa reglas clínicas.
- **Hechos comprobados**: esquema/identidades en `backend/alembic/versions/a3eb75cf454e_initial_schema.py:30–76`, `k4l404288gh0_add_document_traceability.py:39–48` y `o8p808522kl4_implement_unified_db_proposal.py:66–80` (mismo directorio); seguridad en `backend/app/core/security.py:69–106`, sesiones en `backend/app/repositories/session_repository.py:34–62`, pool en `postgres_storage.py:42–63` (mismo directorio); handler/main en `backend/app/main.py:77–91,107–116`. Inspección de archivos, no de instancia física.
- **Propuestas técnicas**: R01–R09 de research (archivos, EXISTS, transacción, aritmética, contrato/harness), sujetas a revisión. No convertirlas en nuevas aprobaciones Q/P.
- Tarea 3.4 (`plan de trabajo/PLAN_DE_TRABAJO_BACKEND_LANGGRAPH.md`, sección Tarea 3.4) dice pacientes/promedio de nodos; issue #35 dice severidad/tiempo de respuesta (spec F01). Se mantienen documentos, colores de presentación/Ambiguo=incertidumbre y promedio persistido anterior/sintético, no nodos/última ejecución/latencia HTTP.
- P03 significa contrato apto y consumo tipado, no integración visual; P04 vigente es comprobación práctica con tiempos observados/Scalar, no SLA numérico ni benchmark. Issue #35 reconsultada vía API pública y tarea 3.4 local no fijan recursos/volumen/clientes/umbral; diferencias completas en spec F01. Dashboard conserva `DashboardSummary` (`frontend/src/pages/Dashboard.tsx:8,19–28`, `frontend/src/api/documentsApi.ts:13–19,109–132`).

## Technical Context

**Language/Version**: validación backend propuesta Python **3.12+**, conforme Constitución `:47`; repositorio permite >=3.11 y usa targets 3.11 (`backend/pyproject.toml:6,68,91`, `infrastructure/scripts/generate.py:34–35`), sin modificarlos. Frontend TypeScript estricto; herramientas contractuales Node >=22 (`package.json:5`). No se certifican versiones efectivamente instaladas.

**Primary Dependencies**: FastAPI/Pydantic v2/asyncpg (`backend/pyproject.toml:10,18,31`), httpx/pytest/pytest-asyncio/jsonschema y generador ya declarados (`:29,41–54`); datamodel-code-generator y openapi-typescript mediante `infrastructure/scripts/generate.py:14–82`. Sin nuevas dependencias. LangGraph existe, pero no participa en leer métricas.

**Storage**: PostgreSQL, fuente única; cuatro tablas existentes de lectura. PostgreSQL **17 aislado real** para integración/P04; sin migraciones nuevas ni conexión a desarrollo durante plan/pruebas. No fallback LOCAL/OCI.

**Testing**: futuro TDD; pytest unitarias/endpoints/contrato y PostgreSQL aislado, Vitest + compilación TypeScript/build, generación/check/Spectral, Alembic offline, P04 y Scalar con sesión real. Nada de ello fue ejecutado en plan; chequeos documentales no sustituyen suites.

**Target Platform**: backend web existente y PostgreSQL 17 real aislado, API local de sandbox con entorno explícito y sesión real. Registrar SO/recursos/versiones/configuración efectivos como contexto, sin mínimo/perfil de RAM/CPU/disco ni obligación de VM conjunta limitada. Guardas T002, propiedad e identidad antes de SQL intactas; no Compose normal ni desarrollo. No se afirma disponibilidad ni rendimiento de producción.

**Project Type**: aplicación web backend FastAPI y frontend TypeScript; API nueva sin pantallas.

**Performance Goals**: «sin retrasos perceptibles» verificado prácticamente con PostgreSQL aislado/sesión real y revisión manual Scalar; registrar tiempos completos observados y contexto. Sin SLA numérico, calentamiento/muestra/concurrencia/timeout de aceptación fijados ni fixture de carga. Fallos o respuestas incorrectas no son aceptación. No acredita rendimiento bajo carga ni en VM de producción.

**Constraints**: solo agregados autenticados para cualquier sesión activa; cohortes/evidencias exactas, sin fecha/paciente/episodio/nodos/origen adicionales; snapshot coherente y cambios confirmados antes de petición visibles en respuesta nueva; null distinto de cero; redondeo único final 2/3 decimales empate hacia arriba. No alterar dashboard, agente, persistencia, migraciones, BD-04, cuentas/roles/datos, configuración o dependencias; no instalación/migración online/semillas/hooks ajenos a etapa.

**Scale/Scope**: reutilizar fixtures funcionales aisladas existentes y oráculos independientes normal/cero/vacío/sin tiempos, sin volumen de carga obligatorio ni nuevo harness de benchmark. Un endpoint y archivos ya previstos; no nuevo código en esta revisión, no API-02/BD-04 como prerrequisito. Integración/COMMIT siguen intactos. T022 prepara sandbox seguro, T023 prepara escenarios reutilizando fixtures, T024 registra comprobación/tiempos, T025 verifica Scalar; T026–T028 puertas independientes del benchmark; T029 consolida solo tras toda aceptación vigente.

## Constitution Check

**Revisión vigente**: no excepción constitucional: siguen pytest completo con integración PostgreSQL API-04 exigida en sandbox, Vitest, TypeScript/build, Alembic offline, validación contractual y ausencia de mutaciones de desarrollo. Q1–Q6/P01/P03/P06 y FR-017 intactos. Los checks de Phase 0/1 que siguen son históricos; la revisión documental no acredita puertas finales ni reutiliza GREEN previo para cambios futuros.

*GATE: revisión previa a Phase 0 y repetida después de Phase 1. Conformidad de diseño no equivale a ejecución empírica.*

### Revisión previa

- **G01 — Fuente única/control manual/solo lectura: conforme en diseño.** `AGENTS.md:10–14`; Constitución `:28–32`. PostgreSQL obligatorio, no mutaciones ni fuente alternativa/configuración. FR-007/008; SC-007.
- **G02 — Consulta obligatoria: conforme en diseño.** AGENTS.md, Regla de Oro §4; Constitución II. Sin decisiones funcionales pendientes (spec, «Alcance y ausencia de supuestos aprobados por defecto»). Disponibilidad/rendimiento no se adivinan.
- **G03 — TDD/cero regresiones: estrategia conforme, ejecución pendiente.** Constitución `:15–20`. Pruebas antes/en paralelo a código, sin crear código ejecutable ahora. No desactivar tests/modificar conftest global para eludir fallos. Desarrollo preservado con dobles/sandbox y guardas efectivas.
- **G04 — RBAC/trazabilidad: conforme en diseño.** Constitución IV/V. Agregados no otorgan permisos de bandeja/dictámenes/resolución. Discrepancia preexistente AUDITOR (spec F09) no se amplía/corrige; trazabilidad/productores/datos intactos.
- **G05 — Tipos/contrato/arquitectura: conforme en diseño.** `AGENTS.md:38–47`; Constitución `:47–59`. Futuro contrato global primero, generados con pipeline real, API tipada, sin Any de dominio/modelos duplicados. Cinco nodos intactos; no pantalla/CSS que requiera cambio Tailwind.
- **G06 — Esquema/migraciones: conforme en diseño, gate empírico pendiente.** Constitución `:49`, `AGENTS.md:29–32`. No nuevo DDL, tablas, índices ni columnas; comentarios/UPSERT existentes intactos. Mantener Alembic offline obligatorio; éxito previo no prueba tablas live.
- **G07 — Resultado histórico del plan, no bloqueo vigente.** Fallos bcrypt/Tailwind de specify: spec «Antecedente histórico — verificaciones de specify/clarify» y checklist «Evidencia histórica de specify». Baseline/suites posteriores en tasks T001–T021 acreditan versiones concretas; puertas finales T026–T028 siguen pendientes. AGENTS.md Regla de Oro §3 y Constitución I/Test Quality Gates intactas; no cierre ni tareas sin evidencia vigente. La completitud documental no certifica puertas empíricas.

### Revisión posterior al diseño (Phase 1)

G01–G06 conservan conformidad **documental**: cuatro fuentes, UUID canónico/EXISTS, transacción READ ONLY/snapshot nuevo, contrato sin UI y fixtures protegidas. Research/data-model/contract/quickstart completos para el diseño, sin cambios productivos. **G07 permanece NO ACREDITADA**, sin excepciones constitucionales. Bcrypt/Tailwind son fallos previos abiertos; integración, Scalar, coherencia/frescura y P04 son aceptación futura que se ejecutará cuando exista implementación comprobable, no fallos observados ni condiciones previas para generar tasks.md. El diseño permite el desglose; comenzar implementación y certificar cierre son decisiones distintas sujetas a sus puertas, no autorizadas por generar tareas.

## Project Structure

### Documentation (this feature)

```text
specs/006-api04-metricas-triaje/
├── spec.md                         # existente, sin cambios
├── checklists/requirements.md      # existente, sin cambios
├── plan.md                         # plantilla efectiva completada
├── research.md                     # Phase 0: fundamentos/alternativas
├── data-model.md                   # Phase 1: datos existentes/reglas
├── quickstart.md                   # Phase 1: validación futura
└── contracts/metrics.openapi.yaml  # Phase 1: contrato local propuesto
```

No `tasks.md`: no se invoca tasks/implement. Necesidad de documentos de esta etapa: plan organiza diseño y revisión constitucional; research fundamenta FR-002/005/006/013/017 y riesgos; data-model precisa FR-002–005/011/013/014/016/017; contract satisface FR-001/003/010/014, SC-008; quickstart diseña evidencia FR-009/010/015/017 y SC-001–009. No cambia referencia activa ni artefactos previos.

### Source Code (repository root) — archivos previstos, no escritos ahora

```text
backend/app/api/v1/metrics.py
backend/app/repositories/metrics_repository.py
backend/app/main.py
backend/app/_generated/models.py
backend/tests/test_metrics_api.py
backend/tests/test_metrics_postgres.py
backend/tests/test_openapi_contract.py
specs/openapi.yaml
specs/paths/metrics.yaml
specs/components/schemas.yaml
frontend/src/_generated/api/types.ts
frontend/src/_generated/api/index.ts
frontend/src/api/metrics.contract.test.ts
```

**Structure Decision**: seguir router/repositorio/generados existentes. No servicio intermedio, módulo SQL separado, modelo manual, client frontend productivo, framework de benchmark, migración o pantalla: ninguno tiene responsabilidad necesaria adicional. Tests de conexión del repositorio caben junto a HTTP en test_metrics_api; escenarios BD real/fixture/P04 en test_metrics_postgres, sin esconder su naturaleza empírica.

### Función y trazabilidad de cada archivo previsto

- **Crear `backend/app/api/v1/metrics.py`**: router `/metrics`, Depends(require_current_user), MetricsResponse generado y lector; sin permisos de rol/reglas clínicas HTTP. FR-001/006/008/012, SC-004/005; ubicación exigida por tarea 3.4 paso 1 y spec «Restricciones de implementación posterior».
- **Crear `backend/app/repositories/metrics_repository.py`**: SQL constante cohorte/evidencia/agregado, pool global asyncpg, transacción nueva READ COMMITTED READ ONLY, guardas/redondeo final y mapping al modelo tipado. Ausencia/fallo DB ->excepción vigente, mensaje saneado. FR-002–005/007/011/013/014/016/017; SC-001–005/007/009.
- **Modificar `backend/app/main.py`**: solo importar/registrar router `/api/v1`, siguiendo `:14–17,107–116`; no modificar handler/auth/lifespan. FR-001/007/010; SC-004/008 y Scalar.
- **Modificar `specs/openapi.yaml`**: tag metrics, referencia `/metrics` y exposición de schemas nuevos para generadores, conservando Bearer/errores. FR-001/010, SC-008; SDD `specs/openapi.yaml:8–10`, `AGENTS.md:39`.
- **Crear `specs/paths/metrics.yaml`**: operación modular GET, documentación exacta población/colores/HITL/tiempo/vacíos/redondeo/vista coherente y 401/503 distintos, sin 403 por rol. FR-001/003/006/007/010–017; SC-004/005/008/009. Trasladar propuesta local, no otro contrato productivo divergente.
- **Modificar `specs/components/schemas.yaml`**: DistribucionPrioridadMetrics/MetricsResponse, campos requeridos/rangos/null y objetos cerrados. FR-001/010/014, SC-005/008. Reutilizar ErrorResponse/respuestas comunes sin modificarlas (`:367–376`, `specs/components/responses.yaml:20–25,38–43`); precisar fases de error en operación.
- **Regenerar `backend/app/_generated/models.py`**: salida Pydantic v2 coherente. FR-001/010/014, SC-008; Constitución `:48`. Sin edición manual/modelo metrics duplicado.
- **Regenerar `frontend/src/_generated/api/types.ts`**: componentes/operación number|null coherentes. FR-010/014, SC-008; Constitución `:54–55`.
- **Regenerar `frontend/src/_generated/api/index.ts`**: exportar MetricsResponse/distribución según pipeline, sin barrel manual. FR-010/014, SC-008; Constitución `:54–55`. `generate.py:64–70` también publica `backend/app/_generated/__init__.py`: salida existente constante, **sin cambio esperado** ni edición manual necesaria.
- **Crear `backend/tests/test_metrics_api.py`**: TDD de router/roles/errores/modelo/None/cero y repositorio con pool/conexión/transacción simulados; un fetchrow y liberación incluso fallo. FR-006–009/012/014; SC-004/005/007. SUPERVISOR parametrizado localmente, sin tocar TEST_SESSIONS global.
- **Crear `backend/tests/test_metrics_postgres.py`**: fixtures propias/guardas, SQL real del repositorio, relaciones/deduplicación/cálculos/inmutabilidad, COMMIT/coherencia y P04 con sesión real/muestras. FR-002–005/008/009/011/013–017; SC-001–007/009. Sin framework adicional/reutilización de BD-04 o desarrollo.
- **Modificar `backend/tests/test_openapi_contract.py`**: extender bundle/validator existente (`:18–37`) con metrics normal/cero/vacío/sin tiempos y 401/503, validar Pydantic generado. FR-001/006/007/010/014; SC-004/005/008. No eliminar tests existentes.
- **Crear `frontend/src/api/metrics.contract.test.ts`**: consumo del tipo generado con apiRequest/fetch simulado fuera del dashboard, ramas number/null y casos normales/cero/vacío/sin tiempos con asserts tipados. FR-010/014, SC-008; Constitución `:54–55`. Lo incluye tsconfig src/build, sin configuración/client nuevo.

No modificar seguridad, sesiones, postgres_storage, audit_repository, episodios, conftest, generador, dashboard, triage.api.ts o migraciones: se reutilizan sin necesidad concreta de cambios. No reparar bcrypt/Tailwind como entregables API-04.

## Diseño del recorrido completo de GET /api/v1/metrics

1. **Ruta**: main registra router con prefijo existente; GET sin body/filtros/paginación nuevos. Solo observación agregada.
2. **Autenticación**: require_current_user valida Bearer contra sesiones PostgreSQL/usuario ACTIVO (`backend/app/core/security.py:69–92`, `backend/app/repositories/session_repository.py:34–62`). Ausente o sesión verificablemente inválida/expirada/revocada/inactiva ->401; fallo al validar ->503 textual vigente. Cualquier sesión válida/activa pasa, sin require_roles/403 o ampliación de permisos. Si falla, no calcular métricas.
3. **Fuente**: lector usa get_db_pool global (`backend/app/repositories/postgres_storage.py:42–63`), no inicializa almacenamiento/consulta LOCAL/OCI. Pool None/adquisición/SQL/transacción fallidos ->DatabaseUnavailableError y handler main `:77–91` ->503 con detail.error=POSTGRESQL_NO_DISPONIBLE, sin 200 parcial/cero/fallback. Conexión siempre liberada.
4. **Snapshot/SQL**: transacción nueva READ COMMITTED READ ONLY, un fetchrow de la sentencia descrita en data-model. Base única por documento, EXISTS final, H por OR/EXISTS de fuentes exactas y agregado único. Indicadores comparten snapshot del SELECT, sin caché/locks de escritura. Petición posterior a COMMIT ve cambios; concurrentes pueden aparecer o no sin mezcla. Autenticación anterior/separada no forma parte del snapshot de indicadores. No promete atomicidad del productor/historial completo.
5. **Cálculo**: COUNT FILTER por colores/D/N/T; SUM numeric original temporal. Guardas D/T vacíos y cuantización racional numeric **final** (porcentaje 2 decimales/segundos 3, empate exacto hacia arriba); cast de operandos antes de operaciones evita overflow. Nunca nulo=0, AVG multiplicado por auditorías ni exposición de contadores internos. Fórmulas en data-model.
6. **Respuesta**: mapping a los dos schemas generados; int de colores y números JSON de indicadores ya cuantizados, None=null. Exactamente tres raíces/tres colores, sin padding obligatorio, strings, identidades o dictámenes. Response_model y tests probarán coincidencia. Sin escribir, llamar IA, procesar o generar auditoría por leerse. Dashboard permanece con DashboardSummary.

## Phase 0 — Research consolidada

[research.md](research.md) documenta R01–R09 con Decision/Rationale/Alternatives considered; separa fallos previos B01/B02, aceptación futura V01, estado documental D01 y puertas de ejecución/cierre G07. No decisiones funcionales pendientes ni incertidumbre que exija reabrir Q/P; propuestas no son código.

BD-03 comprobado **en repositorio/migraciones/tests mock/offline**: `backend/app/repositories/audit_repository.py:20–31,87–138`, migración `backend/alembic/versions/o8p808522kl4_implement_unified_db_proposal.py:66–95`, `backend/tests/test_audit_repository.py:120–158,185–241`, `backend/tests/test_migrations.py:66–83`. Búsqueda estática sin consumidores productivos encontrados; resolución vigente escribe legacy (`backend/app/api/v1/documents.py:217–254`). No se verificó instancia PostgreSQL, datos, permisos/head aplicado o infraestructura P04. API-02 no dependencia obligatoria; BD-04 no prerrequisito.

## Phase 1 — Model, contracts y validación diseñada

- [data-model.md](data-model.md): entidades existentes/UUIDs, C/D/H/N/T/S, EXISTS/cálculo exacto, coherencia/frescura/límites. **No implica crear tablas**.
- [contracts/metrics.openapi.yaml](contracts/metrics.openapi.yaml): OAS 3.1 propuesto, objetos cerrados/campos requeridos/nullable/ejemplos y errores vigentes por referencia. Sin modificar global/generados.
- [quickstart.md](quickstart.md): requisitos/guardas, órdenes futuras y resultados esperados, no implementación completa. Oráculo determinista propuesto dentro de P04 y conservación de muestras/entorno saneados.

**Revisión documental efectuada**: parseo YAML del contrato propuesto, comprobación de schemas de respuesta mediante Draft202012Validator, validación de sus cuatro ejemplos y existencia de referencia ErrorResponse correctos. Sin marcadores de plantilla pendientes ni tasks.md; rama/referencia activa conservadas, sin hooks registrados ni diferencias en archivos rastreados. Este chequeo estático **no** ejecuta endpoint, generadores/Spectral, suites, migraciones o benchmark, ni acredita conformidad de respuestas reales. Spec/checklist preexistentes no se editaron.

### Actualización posterior del contrato y herramientas reales

Primero trasladar propuesta a specs/openapi.yaml/path/schemas modular; después `infrastructure/scripts/validate_spec.py`, `generate.py`, `generate.py --check` (Makefile `:49–56,128–130`). Pipeline: bundle/Spectral, datamodel-code-generator Pydantic v2/strict-nullable, openapi-typescript y compilación antes de publicar (`generate.py:14–82`); check detecta deriva (`:85–95`). No instalación/regeneración/global durante plan; generados no se editan a mano. Si nulabilidad/required/JSON number no coinciden, falla puerta contractual; no ajustar requisitos para forzar generador.

P03: validar JSON real del endpoint contra OpenAPI/modelos y compilar/ejecutar consumo TS normal/cero/vacío/sin tiempos, rama `=== null` separada de número incluido 0; sin any/coerciones/`||0`/`??0`. `apiRequest<T>` no valida runtime (`frontend/src/api/httpClient.ts:35–57`): conformidad backend y consumo frontend son evidencias distintas. Vitest solo no sustituye TypeScript/build (`frontend/package.json:8–10`, `frontend/tsconfig.app.json:17–27`). Sin cambios de dashboard/cliente/pantalla.

### Estrategia de demostración, no ejecución en plan

- **Unitarias/TDD**: HTTP/dependencias/roles/401/ambos 503/modelo/null/cero, único fetchrow y transacción/liberación. Dobles no acreditan SQL real.
- **Integración aislada**: estados/cohorte/colores/nulls, pacientes compartidos/sin episodio, BD-04 antes/después elegible sin cargar semilla; fuentes independientes/seis formas coordinación/repetición/superposición/vínculos no pertinentes; tiempos/cero/negativos/anteriores/sintéticos/redondeo. Consulta productiva contra oráculo independiente, sin romper FKs ni tocar desarrollo.
- **Inmutabilidad**: snapshots clínicos/historial/auditorías/configuración y cero IA/storage. Preparación fixture separada de efecto endpoint; guardas URL/conexión efectiva/propiedad antes de DDL/DML; conftest global conserva DATABASE_URL vacío.
- **Contrato/consumo**: normal/cero/vacío/sin tiempos/errores, JSON Schema/Pydantic generado, number|null en TypeScript y build; claves/cálculos además de schema.
- **Frescura/coherencia**: transición separada con dos documentos y prioridad Urgente+dictamen en misma transacción; consultas concurrentes solo antes (Rojo0/tasa0) o después completo (Rojo1/tasa50/tiempo constante); petición iniciada tras COMMIT ve después. No modificar productor/escribir durante P04.
- **P04 práctico vigente**: analyze de esta revisión antes de retomar ejecución autorizada; T022 verifica sandbox propio/guardas/identidad/versiones y API/sesión real, sin perfil obligatorio. T023 reutiliza fixtures/oráculos; T024 registra cada llamada realizada, cuerpo completo/tiempo monotónico/estado/contrato/cálculo/error, sin SLA/muestra/concurrencia fijados. T025 añade valoración manual Scalar «sin retrasos perceptibles». Preservar todo intento, incluso fallido/incompleto, sin secretos ni reintentos para ocultar fallos; declarar que no demuestra carga ni VM de producción. No es necesario recuperar la extracción SSD incompleta para entregar el endpoint: es un intento histórico conservado, no prerrequisito vigente.
- **Scalar**: futura `/scalar` de API sandbox con sesión real, evidencia saneada sin tokens/passwords/datos clínicos; status/cuerpo/oráculo. `/docs` es Swagger, no Scalar (`backend/app/main.py:48,54–75`).
- **Puertas obligatorias, separadas por momento**: conservar pytest completo unitarias/E2E, Vitest run, npm run build y Alembic upgrade head --sql con URL de prueba según `AGENTS.md:16–20` antes de implementar/finalizar; durante implementación, TDD según Constitución `:16–19`. Para aceptar/finalizar API-04 se añade la evidencia de contrato/generation-check, integración, Scalar, coherencia y P04 sobre la implementación. Warnings no justificados/skips no acreditan éxito; desarrollo íntegro. Ninguna puerta se declara superada. La evidencia específica del endpoint aún inexistente no se exige para redactar tasks.md.

## Complexity Tracking

No excepción arquitectónica/constitucional solicitada. Archivos productivos/contrato/generados/tests tienen necesidad concreta, sin nuevos servicios/DDL/dependencias/UI. EXISTS y una sentencia evitan deduplicación complicada/snapshots múltiples. Transacción explícita añade protección de lectura sin alterar productores; coste no demostrado hasta P04.

**Clasificación, sin excepciones**:

- **Fallos previos de suites**: bcrypt/Tailwind abiertos; diagnóstico entorno/repositorio en research B01/B02. Impiden acreditar las puertas para comenzar implementación/cerrar, pero no impiden documentar el desglose. Su reparación no es deliverable funcional API-04.
- **Aceptación futura API-04**: integración, Scalar, coherencia/frescura, contrato/consumo y P04 están definidos para ejecución sobre la implementación; no ejecutados y no acreditados. Su ausencia actual no es un fallo del diseño ni prerrequisito de tasks.md.
- **Estado documental**: plan/research/data-model/contrato/quickstart completos y coherentes, sin decisiones funcionales abiertas ni componentes pendientes de definir para el desglose. Afirmar esto no marca tareas completadas ni certifica puertas empíricas. Alembic offline previo no equivale a migraciones aplicadas; no disponibilidad/rendimiento afirmados sin evidencia.

## Estado de cierre y siguiente etapa

**Los párrafos siguientes registran el cierre histórico de plan**. La continuación autorizada por el usuario tras limpieza/analyze se rige por las tareas vigentes T022–T029; no por ausencia histórica de tasks, bcrypt/Tailwind o benchmark. Recursos/ejecución/aceptación no se presumen.

**Desglose documental**: listo para generar tasks.md cuando el usuario lo autorice; no se identificó un impedimento específico. La skill de tasks requiere plan.md/spec.md y usa los demás artefactos de diseño (`.agents/skills/speckit-tasks/SKILL.md:59–74`); la comprobación de prerrequisitos distingue plan para tasks de plan+tasks para implementación (`.specify/scripts/powershell/check-prerequisites.ps1:42–47,90–110`). No exige benchmark ni pruebas aprobadas de un endpoint aún inexistente. Lectura de estas reglas únicamente: no se ejecutó la skill ni sus scripts.

**Comenzar implementación**: no autorizado en esta revisión; fallos previos bcrypt/Tailwind pendientes y puertas de `AGENTS.md:16–20` no acreditadas. El futuro desglose debe conservar este bloqueo de ejecución, TDD y preservación de desarrollo, sin convertir reparar el entorno en funcionalidad API-04.

**Finalizar funcionalidad o marcar tareas completadas**: requiere puertas empíricas completas (`AGENTS.md:17–20`, Constitución `:16–20,68–86`) y aceptación específica API-04 contra la implementación, incluida integración/Scalar/coherencia/P04. Completitud documental o generación de tareas no sustituye estas evidencias ni certifica cierre formal del plan. Ninguna puerta se declara superada.

**Detención de la revisión documental anterior (antecedente)**: se detuvo antes de implement. La autorización actual permite continuar desde T022 solo tras limpieza/analyze sin contradicciones, según tasks; no ampliar alcance, recuperar benchmark como requisito ni inferir aceptación. Decisiones/intentos preservados; cierre por aceptación práctica y todas las puertas, no perfil antiguo. Sin commits/push/PR.
