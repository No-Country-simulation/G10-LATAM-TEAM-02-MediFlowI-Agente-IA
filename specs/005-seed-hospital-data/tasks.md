---
description: "Tareas TDD de BD-04: semilla hospitalaria idempotente de desarrollo"
---

# Tasks: BD-04 — Semilla hospitalaria de desarrollo

**Input**: [spec.md](spec.md) y [plan.md](plan.md), con [research.md](research.md), [data-model.md](data-model.md), [contrato](contracts/seed-command-contract.md) y [quickstart.md](quickstart.md).

**Status: BD-04 completada y aceptada por el usuario; T001–T039 completadas.** T001–T035 cuentan con evidencia automática registrada al final: backend completo 229 pruebas pasando (90 BD-04), frontend 48 pruebas en 8 archivos y build sin errores TypeScript con Node 22.23.3/npm 10.9.9, comandos normales. **T036**: carga manual reportada por el usuario en `mediflow-backend-dev`, destino confirmado `postgres:5432/mediflow_dev`, creados 10/4/5 y código de salida 0; fecha de ejecución no comunicada y hora exacta no anotada. **T037**: captura/JSON real de Scalar (HTTP 200, total 10, diez DNI únicos) y corroboración PostgreSQL de fechas y edades con `CURRENT_DATE` en UTC, referencia `2026-10-08`. **T038**: HTTP 200 reportado y JSON de usuarios aportado por el usuario con ADMINISTRADOR existente, cuatro médicos OPERADOR/ACTIVO únicos y sus especialidades, junto con los cinco GET documentales HTTP 200 ya confirmados. **T039**: cobertura/evidencias consolidadas, sandbox propio detenido y credenciales temporales retiradas; cierre de cuatro sesiones (dos de M01 y dos del ADMINISTRADOR) y limpieza local confirmados por el usuario, seguido de su aceptación final explícita «si acepto». El agente no ejecutó la semilla ni cambió la lógica de edad o los campos opcionales. Sin commit, push o PR.

**Tests**: Obligatorios por petición del usuario y Constitución. Escribir pruebas antes de cada comportamiento de producción; comprobar RED, implementar lo mínimo y verificar GREEN. La falta de dependencias, un fallo de fixture, un error de colección o un skip no son evidencia RED del comportamiento ni evidencia GREEN de integración.

**Organization**: Setup → infraestructura aislada → US1 (P1, carga inicial) → US2 (P1, repetición segura) → US3 (P2, seguridad/edad) → gates y cierre manual. Las comprobaciones básicas de hash y ausencia de edad fija ya se incluyen en las pruebas de primera carga; US3 amplía su verificación. Nunca se entrega una carga intermedia con contraseñas en claro o edad estática.

## Format: `[ID] [P?] [Story] Description`

- Todos los elementos ejecutables usan `- [ ] Tnnn` (pendiente) o `- [x] Tnnn` (completado con evidencia), ruta concreta y etiqueta `[US1]`, `[US2]` o `[US3]` en fases de historia.
- `[P]` significa archivos distintos y sin dependencia mutua **después de cumplir los prerrequisitos de su fase**. Las escrituras en el mismo módulo o archivo de pruebas se serializan.
- Las casillas acreditan únicamente el trabajo de cada tarea respaldado por el registro final. Las comprobaciones automáticas están superadas; T036–T039 son exclusivamente manuales y reservadas al usuario. T036 se acredita con su reporte de carga, T037 con sus evidencias Scalar y la corroboración de lectura, y T038 con sus respuestas Scalar de usuarios/documentos. T039 acredita la consolidación, cierre del sandbox propio, confirmaciones de cierre de sesiones/limpieza y aceptación final explícita del usuario. No se sustituyen sus acciones manuales por ejecuciones automáticas del agente.

## Path Conventions

- Código implementado: `backend/app/scripts/seed_hospital_data.py`, con paquete `backend/app/scripts/__init__.py`.
- Pruebas implementadas: `backend/tests/test_seed_hospital_data.py` (unitarias/contrato), `backend/tests/test_seed_hospital_data_postgres.py` (fixtures e integración real).
- Marcador: `backend/pyproject.toml`; conservar las protecciones de `backend/tests/conftest.py`, sin reutilizar `repository_mock` como prueba de PostgreSQL real.
- Documentos/evidencias saneadas: `specs/005-seed-hospital-data/quickstart.md` y este `tasks.md`; nunca credenciales, tokens ni datos reales ajenos.
- No editar migraciones, OpenAPI, frontend, servicios del agente o reglas clínicas para resolver BD-04.

## Phase 1: Setup — preparación acotada

**Purpose**: Preparar herramientas y reglas de prueba sin añadir nuevas dependencias ni conectar a desarrollo.

- [x] T001 Preparar un entorno Python 3.12+ con las dependencias backend/dev ya declaradas en `backend/pyproject.toml` y `backend/uv.lock`; comprobar pytest, asyncpg, Alembic y disponibilidad de Docker/PostgreSQL 17 sin abrir `mediflow_dev`, y registrar bloqueos de entorno en `specs/005-seed-hospital-data/quickstart.md` antes de intentar la implementación.
- [x] T002 [P] Registrar `postgres_integration` en `backend/pyproject.toml` sin cambiar dependencias, `repository_mock` ni las guardias existentes de `backend/tests/conftest.py`; definir que `BD04_REQUIRE_POSTGRES=1` impide aprobar integración por skips.
- [x] T003 [P] Precisar en `specs/005-seed-hospital-data/quickstart.md` el sandbox desechable PostgreSQL 17 separado, endpoint esperado `127.0.0.1:55432`, usuario `bd04_test`, base `mediflow_bd04_test`, entradas secretas de test y propiedad/limpieza del recurso; no usar compose, volúmenes ni `.env` de desarrollo para tests.

**Checkpoint**: Entorno y contrato de integración disponibles; ningún comportamiento de semilla implementado todavía.

## Phase 2: Foundational — PostgreSQL aislado y fixture segura

**Purpose**: Obtener evidencia real de persistencia sin relajar la protección de desarrollo. Bloquea la implementación de historias.

- [x] T004 Escribir primero en `backend/tests/test_seed_hospital_data_postgres.py` pruebas de las guardias de la fixture: URL ausente/inválida, host/puerto/usuario/base inesperados, `mediflow_dev` declarado o efectivo, y esquema/search_path incorrecto deben impedir bootstrap, DML y teardown; exigir fallo, no skip, cuando `BD04_REQUIRE_POSTGRES=1`.
- [x] T005 Implementar las fixtures y helpers de prueba en `backend/tests/test_seed_hospital_data_postgres.py`: conexión asyncpg de alcance compatible con el event loop, variable `BD04_TEST_DATABASE_URL` sin fallback, verificación de URL y destino efectivo en cada conexión, generación Alembic head offline en subproceso con entorno explícito y aplicación íntegra del SQL en la misma conexión aislada validada; respetar BEGIN/COMMIT sin dividir por semicolons ni envolverlos en otra transacción; conservar baseline histórico y cerrar solo recursos propios.
- [x] T006 Ejecutar las pruebas de fixture de `backend/tests/test_seed_hospital_data_postgres.py` contra el sandbox separado y comprobar GREEN, revision Alembic/columnas/enums vigentes, aislamiento efectivo y teardown posterior a aserciones; mantener `DATABASE_URL` vacía en pytest y registrar evidencia saneada en `specs/005-seed-hospital-data/tasks.md`, sin aplicar migraciones online en desarrollo ni cambiar `backend/alembic/env.py`.

**Checkpoint**: La infraestructura real está en verde y no usa resultados mock. Cada escenario tiene sandbox limpio; ninguna limpieza puede intercalarse entre las dos cargas de la prueba de idempotencia.

## Phase 3: User Story 1 — Preparar un conjunto ficticio de desarrollo (Priority: P1)

**Goal**: Carga inicial consultable de 10 pacientes, 4 médicos OPERADOR y 5 registros documentales, segura por defecto y sin efectos físicos/clínicos adicionales.

**Independent Test**: Una ejecución en PostgreSQL aislado deja exactamente 10/4/5 registros **del manifiesto**, con FK válidas, cuatro especialidades, tres prioridades existentes, hashes verificables y fechas de nacimiento válidas; episodios/configuración/datos ajenos intactos y cero archivos. No exigir conteos globales de tabla 10/4/5.

### Tests for User Story 1 — primero

- [x] T007 [P] [US1] Escribir en `backend/tests/test_seed_hospital_data.py` pruebas unitarias del manifiesto y contrato CLI: identidades/UUIDv5 estables 10/4/5, DNI de ocho cifras, cuatro especialidades con OPERADOR, prioridades admitidas, fechas válidas/no futuras, ausencia de edad/colores persistidos, import/`--help` sin efectos, `--target` obligatorio, URLs/credenciales rechazadas sin filtración y modo development no interactivo/cancelado sin escrituras; usar dobles para probar el rechazo de desarrollo sin conectarse a él.
- [x] T008 [P] [US1] Escribir en `backend/tests/test_seed_hospital_data_postgres.py` la integración de primera carga con secretos efímeros: commit y lectura desde otra conexión, conteos BD-04 10/4/5, cuatro OPERADOR con Medicina General/Cardiología/Neumonología/Traumatología, FK de paciente, cobertura Urgente/Rutina/Ambiguo y comprobación básica con `verify_password` de hash/salt y edad consultada desde fecha_nacimiento.
- [x] T009 [US1] Añadir en `backend/tests/test_seed_hospital_data_postgres.py` snapshots de baseline y comprobaciones de ausencia de efectos: `paciente_edad`/`episodio_id` NULL solo en documentos BD-04, sin rutas/archivos/objetos nuevos, sin invocar IA/storage, sin episodios/notificaciones/auditorías/colas nuevas y sin cambiar `configuracion_sistema` ni datos ajenos; no alterar LOCAL/OCI para preparar el caso.
- [x] T010 [US1] Ejecutar T007–T009 con las fixtures ya verificadas y dejar evidencia RED del comportamiento esperado en `specs/005-seed-hospital-data/tasks.md` antes de escribir la carga; resolver problemas de entorno/colección sin introducir código de producción o desactivar pruebas para ocultar fallos.

### Implementation for User Story 1 — después de las pruebas

- [x] T011 [US1] Crear `backend/app/scripts/__init__.py` sin efectos y el manifiesto tipado e inmutable en `backend/app/scripts/seed_hospital_data.py`, con 10 pacientes ficticios/fecha_nacimiento, 4 médicos OPERADOR, 5 documentos `BD04-DOC-001`–`BD04-DOC-005`, UUIDv5 de namespace constante, claves naturales sintéticas ajenas a seeds históricos y metadata documental BD-04/v1; no generar archivos ni inventar diagnósticos/umbrales/colores clínicos.
- [x] T012 [US1] Implementar en `backend/app/scripts/seed_hospital_data.py` validación de manifiesto, fechas, entradas seguras `BD04_PASSWORD_M01`–`BD04_PASSWORD_M04` y política vigente; preparar hash/salt de nuevas cuentas exclusivamente con `app.core.security.hash_password`, sin contraseñas públicas/persistidas ni cambio de firmas de helpers existentes.
- [x] T013 [US1] Implementar la carga asíncrona con conexión explícita en `backend/app/scripts/seed_hospital_data.py`: consultas parametrizadas, una transacción por ejecución, inserción ordenada pacientes/usuarios/documentos sobre el esquema vigente, FK por identidad, documentos tipo JSON/default recibido/Admision y UPSERT por documento_id limitado a propiedad compatible; edad, episodio, destino y rutas físicas sin asignar, sin repositorio general de triaje ni escritura en configuración/sesiones.
- [x] T014 [US1] Implementar la CLI en `backend/app/scripts/seed_hospital_data.py` conforme a `specs/005-seed-hospital-data/contracts/seed-command-contract.md`: test usa exclusivamente URL del sandbox y development exige URL explícita/confirmación interactiva, verificar destino efectivo antes de DML, comprobar esquema sin migrarlo, cerrar conexión siempre y devolver códigos/cantidades saneadas sin URL secreta/hash/salt; no ejecutar el modo development al desarrollar esta tarea.
- [x] T015 [US1] Ejecutar y verificar GREEN de T007–T009 en los archivos `backend/tests/test_seed_hospital_data.py` y `backend/tests/test_seed_hospital_data_postgres.py`, y publicar en `specs/005-seed-hospital-data/quickstart.md` las identidades concretas del manifiesto sin secretos para reconocer los registros; no pasar a aceptación en desarrollo todavía.

**Checkpoint**: Primera carga probada de forma independiente. Es un incremento de pruebas, no el cierre de BD-04: faltan reejecución y comprobaciones ampliadas de seguridad/edad.

## Phase 4: User Story 2 — Repetir la carga sin duplicar registros (Priority: P1)

**Goal**: Reutilizar identidades propias, completar conjuntos parciales y rechazar conflictos con atomicidad, sin reset de credenciales.

**Independent Test**: En la misma base aislada, carga 1 + commit → lectura por conexión nueva → carga 2 + commit, sin rollback, recreación o limpieza entre ambas. Comparar 10/4/5, UUID, claves, FK y credenciales; filas ajenas y configuración permanecen intactas.

### Tests for User Story 2 — primero

- [x] T016 [P] [US2] Escribir en `backend/tests/test_seed_hospital_data_postgres.py` la prueba de dos ejecuciones consecutivas reales: commit de cada carga, comprobación desde otra conexión y comparación del conjunto 10/4/5/UUID/FK/hash/salt/estado/baseline; prohibir explícitamente rollback, truncado, recreación y limpieza entre ambas, y contar solo identidades BD-04.
- [x] T017 [P] [US2] Escribir en `backend/tests/test_seed_hospital_data.py` pruebas de reconocimiento/reutilización por UUID y clave natural y metadata documental, respuesta del UPSERT sin cambio, conteos creados/reutilizados y preservación de credenciales/estado aunque la segunda entrada de password difiera o falte para una cuenta ya propia; no reconocer propiedad por nombre ni por salt.
- [x] T018 [US2] Añadir en `backend/tests/test_seed_hospital_data_postgres.py` escenarios separados de conjunto parcial propio y colisiones UUID/número de documento/HC/DNI/documento_id/metadata ajena; forzar conflicto tardío para demostrar rollback completo de esa ejecución sin tocar cargas previas ni apropiarse de filas ajenas.
- [x] T019 [US2] Añadir en `backend/tests/test_seed_hospital_data_postgres.py` dos subprocesos independientes de `python -m app.scripts.seed_hospital_data --target test` sobre el mismo sandbox, más dos cargas concurrentes para verificar la serialización transaccional prevista y ausencia de duplicados/efectos extra; cada proceso debe validar su destino, sin usar el modo development.
- [x] T020 [US2] Ejecutar T016–T019 y registrar RED de los comportamientos faltantes en `specs/005-seed-hospital-data/tasks.md` antes de modificar la carga; si alguna prueba ya pasa por implementación correcta de US1, conservarla sin fabricar una regresión y documentar qué ampliación requiere implementación.

### Implementation for User Story 2

- [x] T021 [US2] Completar en `backend/app/scripts/seed_hospital_data.py` reutilización/completado parcial por propiedad compatible, detección de todos los conflictos, conservación de UUID/FK/created_at/credenciales/estado y UPSERT documental sin actualización efectiva cuando coincide; resolver su resultado por consulta de identidad si no retorna fila, sin borrar ni sobrescribir datos ajenos.
- [x] T022 [US2] Añadir o completar en `backend/app/scripts/seed_hospital_data.py` el bloqueo asesor transaccional BD-04 estable y la atomicidad de la unidad de carga ante conflicto/error, garantizando cierre/rollback de esta ejecución y salida no cero sin éxito parcial ni cambios de configuración, sin mantener una transacción exterior que oculte commits en las pruebas.
- [x] T023 [US2] Ejecutar T016–T019 con PostgreSQL real aislado y confirmar GREEN, incluida doble carga vía función y vía subprocesos y preservación de snapshots; registrar las evidencias sin secretos en `specs/005-seed-hospital-data/tasks.md`, con teardown únicamente después de verificar la segunda ejecución.

**Checkpoint**: Idempotencia y conservación demostradas con datos confirmados, no mediante mocks ni dos primeras cargas separadas por rollback.

## Phase 5: User Story 3 — Consultar datos seguros y edades vigentes (Priority: P2)

**Goal**: Ampliar evidencia de seguridad de las cuatro cuentas y de edad calculada en PostgreSQL, sin sustituir los mecanismos vigentes.

**Independent Test**: Verificar hashes/salts persistidos con el helper existente, rechazo de passwords incorrectas y ausencia de secretos; consultar una misma fila antes y el día de cumpleaños con referencia SQL controlada, sin reseeding ni cambios de fecha de nacimiento/edad.

### Tests for User Story 3 — primero

- [x] T024 [P] [US3] Escribir en `backend/tests/test_seed_hospital_data.py` pruebas ampliadas de política de contraseñas, llamada al helper `app.core.security.hash_password` solo para nuevas cuentas, entradas faltantes/inválidas y saneamiento de errores/salidas; comprobar que password/hash/salt/URL completa no se filtran y que import/ayuda no crean credenciales o sesiones.
- [x] T025 [P] [US3] Escribir en `backend/tests/test_seed_hospital_data_postgres.py` verificaciones de las cuatro credenciales persistidas con `verify_password`, password incorrecta, salt aleatorio, ausencia de texto plano en columnas/JSON/salida y preservación de credenciales/estado en reejecución y cuentas parciales existentes; no comparar hashes recién salados como criterio de identidad.
- [x] T026 [US3] Escribir en `backend/tests/test_seed_hospital_data_postgres.py` pruebas reales de edad desde `backend/app/repositories/patient_repository.py`: inyectar pool del sandbox sin mockear filas, comprobar query vigente CURRENT_DATE y usar fecha de referencia controlada solo en la proyección SQL de test para antes/día de cumpleaños y febrero 29, siguiendo `age` de PostgreSQL; misma fila/DOB intacta, sin columna física edad de paciente ni edad fija en documentos/JSON BD-04.
- [x] T027 [US3] Ejecutar T024–T026 y documentar RED de casos todavía no cubiertos en `specs/005-seed-hospital-data/tasks.md`; preservar los ya satisfechos, sin congelar solo Python para simular fecha PostgreSQL ni cambiar el repositorio o esquema para fabricar el resultado.

### Implementation for User Story 3

- [x] T028 [US3] Ajustar únicamente `backend/app/scripts/seed_hospital_data.py` para cerrar los casos de seguridad fallidos: política vigente y secretos requeridos para cuentas nuevas, hash/salt del helper existente, preservación de credenciales/estado en cuentas propias y saneamiento de errores/salidas sin crear sesiones o administradores.
- [x] T029 [US3] Ajustar únicamente `backend/app/scripts/seed_hospital_data.py` para cerrar casos fallidos de fechas/edad: DOB válida y no futura, sin edad persistida en columna/documentos/metadata/resultados; reutilizar el cálculo dinámico existente sin añadir columna, migración, regla de cumpleaños o cambios a `backend/app/repositories/patient_repository.py`.
- [x] T030 [US3] Ejecutar las pruebas completas de `backend/tests/test_seed_hospital_data.py` y `backend/tests/test_seed_hospital_data_postgres.py` con `BD04_REQUIRE_POSTGRES=1` y comprobar GREEN de US1/US2/US3 sin skips de integración; registrar evidencia saneada en `specs/005-seed-hospital-data/tasks.md` antes de pasar al cierre.

**Checkpoint**: Las tres historias están verificadas. PostgreSQL aislado acredita persistencia/idempotencia/edad; falta completar las puertas globales y la aceptación manual autorizada.

## Phase 6: Polish & Cross-Cutting Concerns — gates y cierre manual

**Purpose**: Preparar evidencia final y dejar la única carga de desarrollo al final, por acción humana, después de todos los gates. No ejecutar esta fase durante la generación de tareas.

- [x] T031 Revisar y sincronizar `specs/005-seed-hospital-data/quickstart.md` y `specs/005-seed-hospital-data/contracts/seed-command-contract.md` con la implementación verificada: flags/variables, manifiesto, comandos seguros, códigos de salida, guardias de destino, fases automática/manual y consultas separadas; sin publicar secretos ni ampliar el alcance aprobado.
- [x] T032 Refactorizar y revisar tipado/SQL parametrizado/manejo de conexión de `backend/app/scripts/seed_hospital_data.py` con sus pruebas en verde, sin nuevos servicios/dependencias/migraciones, edades fijas, archivos físicos, episodios, reglas clínicas o cambios de API/frontend; conservar las protecciones de `backend/tests/conftest.py`.
- [x] T033 Ejecutar toda la suite backend de `backend/pyproject.toml` mediante `python -m pytest`, con integración PostgreSQL exigida y sandbox protegido, comprobando 100% de pruebas en verde y ausencia de mutaciones de desarrollo; registrar resultado en `specs/005-seed-hospital-data/tasks.md` y bloquear el cierre manual ante fallo/skip de integración o warning no justificado.
- [x] T034 Ejecutar `npm test` (vitest run) y `npm run build` definidos en `frontend/package.json`, con todas las pruebas en verde y cero errores TypeScript, sin modificar código frontend para BD-04; registrar resultados en `specs/005-seed-hospital-data/tasks.md` y tratar dependencias ausentes como bloqueo, no éxito.
- [x] T035 Ejecutar `python -m alembic upgrade head --sql` usando `backend/alembic.ini` y URL explícita de prueba exclusivamente offline, verificar salida sin errores y correspondencia con head, y registrar evidencia en `specs/005-seed-hospital-data/tasks.md`; no aplicar migraciones ni cambiar `backend/alembic/env.py`, desarrollo o almacenamiento.
- [x] T036 Una vez completadas T030–T035 y obtenido permiso humano explícito para el destino, el desarrollador debe ejecutar **manualmente** el script terminado `backend/app/scripts/seed_hospital_data.py` mediante `python -m app.scripts.seed_hospital_data --target development`, revisar el destino saneado y confirmar `mediflow_dev`; registrar resultado 10/4/5 en `specs/005-seed-hospital-data/quickstart.md`, sin resets, migraciones, cambios de LOCAL/OCI ni ejecución automática por el agente.
- [x] T037 Después de T036, el desarrollador debe verificar visualmente en Scalar `GET /api/v1/patients` sin search, HTTP 200 y exactamente los 10 pacientes por numero_documento dentro de items con fecha_nacimiento/edad correctas a la fecha del backend; no confundir total general con conteo semilla ni atribuirle médicos/documentos, y registrar evidencia saneada en `specs/005-seed-hospital-data/quickstart.md`.
- [x] T038 Después de T036, el desarrollador debe comprobar por separado en Scalar `GET /api/v1/users` con sesión ADMINISTRADOR existente para las cuatro cuentas OPERADOR/especialidades y cinco `GET /api/v1/documents/{documento_id}` para IDs/prioridades, sin crear cuentas privilegiadas o descargar archivos inexistentes; registrar evidencia saneada en `specs/005-seed-hospital-data/quickstart.md` sin interpretar Ambiguo como gravedad intermedia.
- [x] T039 Consolidar evidencias automáticas y manuales en `specs/005-seed-hospital-data/tasks.md` y `specs/005-seed-hospital-data/quickstart.md`, comprobar cobertura FR-001–013/SC-001–008, cerrar solo el sandbox propio y retirar secretos de las terminales; no marcar BD-04 completada si faltan gates o aceptación humana y no borrar datos clínicos de desarrollo.

**Checkpoint**: Cierre de BD-04 solo con pruebas aisladas, gates globales y aceptación manual documentada. Si la persona responsable no autoriza la carga, T036–T039 permanecen pendientes; no se sustituye esa autorización por casillas marcadas automáticamente.

## Dependencies & Execution Order

### Phase Dependencies

- T001 → T002/T003 (archivos distintos) → T004 → T005 → T006.
- Fundación T006 → US1 T007/T008 → T009 → T010 (RED) → T011 → T012 → T013 → T014 → T015 (GREEN).
- US1 T015 → US2 T016/T017 → T018 → T019 → T020 (RED) → T021 → T022 → T023 (GREEN).
- US1 T015 habilita las pruebas independientes de US3; para ejecutar el orden principal del documento, completar US2 T023 antes de T024/T025 → T026 → T027 (RED) → T028 → T029 → T030 (GREEN global de historias).
- T030 → T031 → T032 → T033 → T034 → T035 → **permiso humano explícito** → T036 → T037/T038 (consultas manuales, serializar el registro en quickstart.md) → T039.

### User Story Dependencies

- **US1 (P1)**: depende únicamente de infraestructura de test; se verifica por primera carga real aislada.
- **US2 (P1)**: reutiliza el loader/manifiesto de US1; su evidencia independiente es la doble carga, conjuntos parciales y conflictos. No requiere ejecutar US3 ni consultas manuales.
- **US3 (P2)**: reutiliza loader/manifiesto de US1; seguridad y cumpleaños se comprueban independientemente en sandbox. Se secuencia después de US2 porque ambos editan el mismo módulo/archivo de integración y el cierre requiere todas las historias.
- No crear implementaciones redundantes para hacer historias artificialmente independientes; cada una tiene criterios verificables propios sobre el componente compartido.

### Within Each User Story

- Pruebas del comportamiento → evidencia RED → implementación mínima → GREEN → refactor sin regresiones.
- Si una nueva prueba ya pasa, conservarla y no introducir un fallo artificial. La primera carga nunca almacena passwords en claro o edades fijas para posponer su corrección a US3.
- No llamar servicios de triaje ni mocks de resultados para acreditar integración. Dos cargas con rollback intermedio no satisfacen FR-007.
- Los marcadores `[USn]` describen propiedad de la tarea; las comprobaciones manuales de US1 se difieren deliberadamente al cierre transversal por FR-013 y la petición del usuario.

### Parallel Opportunities

- T002 y T003, una vez terminado T001: pyproject.toml frente a quickstart.md.
- T007/T008: pruebas unitarias frente a pruebas PostgreSQL US1, después de la fixture segura T006.
- T016/T017: integración de idempotencia frente a pruebas unitarias de propiedad/reutilización, después de US1.
- T024/T025: unitarias de credenciales frente a integración real de credenciales, tras prerrequisitos.
- No paralelizar T008/T009, T016/T018/T019 o T025/T026: editan el mismo archivo. Tampoco las implementaciones US1/US2/US3: comparten seed_hospital_data.py. No ejecutar en paralelo escenarios que compartan una base sin aislamiento propio.

## Parallel Example: User Story 1

Después de T006, redactar T007 en `backend/tests/test_seed_hospital_data.py` y T008 en `backend/tests/test_seed_hospital_data_postgres.py` en paralelo. Integrar ambos antes de T009/T010; no escribir la carga mientras no haya evidencia RED válida.

## Parallel Example: User Story 2

Después de T015, redactar T016 en el archivo PostgreSQL y T017 en el archivo unitario en paralelo. T018/T019 continúan serialmente sobre el archivo PostgreSQL antes de T020–T022.

## Parallel Example: User Story 3

Tras sus prerrequisitos, redactar T024 en el archivo unitario y T025 en el archivo PostgreSQL en paralelo. T026 comparte el segundo archivo y va después; todas las modificaciones del módulo de carga son seriales.

## Implementation Strategy

### MVP First — primera carga US1, solo en sandbox

Completar setup/fundación y US1 para demostrar la carga 10/4/5 en PostgreSQL aislado, con hash y sin edad fija. Es un incremento mínimo demostrable, **no** BD-04 terminada ni permiso de carga en desarrollo: idempotencia y edad/seguridad ampliadas siguen siendo obligatorias.

### Incremental Delivery

US1 carga inicial segura → US2 doble carga real/propiedad/atomicidad → US3 verificación ampliada de credenciales/edad → gates backend/frontend/SQL offline → permiso humano y cierre manual Scalar. Conservar evidencia de cada checkpoint sin ejecutar etapas no autorizadas.

### Parallel Team Strategy

Paralelizar únicamente la redacción de pruebas o documentos en los pares indicados. Un responsable serializa el módulo de carga y otro puede revisar las aserciones reales del sandbox. No se asignan nuevas tareas clínicas, nuevos roles de equipo ni trabajo fuera de BD-04.

## Notes

- **Resumen**: 39 tareas: setup 3, fundamento 3, US1 9, US2 8, US3 7, cierre transversal 9. Cuatro pares paralelizables explícitos; 24 tareas etiquetadas por historia y 15 compartidas/cierre.
- **Trazabilidad**: FR-001–006 → T007–T015; FR-007–008 → T016–T023; FR-009–010 → T008/T012 y T024–T030; FR-011 → T009/T013/T018/T023; FR-012–013 → T002–T006/T014/T019/T031–T039. SC-001–008 cubiertos por las tres pruebas independientes y el cierre manual.
- Los roles OPERADOR, especialidades y prioridades son los ya aprobados; sin episodios/archivos/esquema nuevo. Los colores solo describen presentación visual existente, no datos clínicos persistidos.
- No se alteran pruebas existentes para forzar aprobación. Los bloqueos de dependencias ya registrados requieren resolver entorno en T001; no acreditan una implementación correcta.
- No existe `.specify/extensions.yml` al generar este documento; no hay hooks previos/posteriores que ejecutar.
- La autorización posterior del usuario para `/speckit-implement` permite únicamente implementación y pruebas aisladas. Prohíbe cargar development y reserva Scalar al usuario.

## Registro de ejecución — 2026-10-07

### Trabajo efectuado y verificado localmente (sin aceptación global)

- **T001–T003**: entorno Python 3.13.2 mediante uv y lock vigente, extras dev/sdd (jsonschema necesario para suite global); marcador registrado, conftest intacto. Docker sin daemon: alternativa nativa PostgreSQL 17 separada autorizada por research §5. Clúster recién creado en temporal OpenCode, solo loopback 55432, base `mediflow_bd04_test`, usuario `bd04_test`, SCRAM y credenciales aleatorias no publicadas. Sin tocar el servicio, puerto o datos de desarrollo.
- **T004–T006**: guardias de URL/valores efectivos/missing-required y fixture offline completas. Primer intento previo a helpers: 14 fallos de helpers ausentes; no se interpreta como RED clínico. Tras implementar fixture y corregir encoding UTF-8 del subproceso: **15 pruebas pasando**, bootstrap real revision p9q909633lm5 y baseline histórico 4 usuarios/3 documentos conservado. Reset solo en sandbox propio autorizado y entre escenarios, nunca entre cargas consecutivas.
- **T007–T015**: pruebas escritas antes del comportamiento, scaffold sin conexión y RED **14 fallos / 15 pasando**, incluyendo fallo de carga sobre fixture ya verificada. Implementación inicial segura → **29 pruebas pasando**. Manifiesto/documentos/credenciales reales documentados sin secretos en quickstart.
- **T016–T023**: primero pruebas de propiedad, dos commits, parcial, nueve variantes de colisiones, subprocesos y concurrencia: RED **14 fallos / 29 pasando**. Implementación de propiedad/UPSERT sin update efectivo/lock transaccional → **43 pasando**. Lectura por conexión distinta, igualdad de snapshots completos después de segunda y tercera carga; no limpieza/rollback intermedio. Dos CLI independientes también dejan 10/4/5. Parcial completa 9/3/4 reutilizando 1/1/1, sin reactivar/resetear la cuenta propia.
- **T024–T030**: políticas, hash solo en cuatro cuentas nuevas, salt aleatorio, verify_password correcto/incorrecto, secretos/salidas saneados, guardias efectivas, cierre de conexión, schema mismatch, transacción exterior y query real del repositorio con pool aislado. Cumpleaños y febrero 29 controlados solo en SQL de test sobre DOB intacta. Las nuevas pruebas ya pasaban sobre US1/US2: **64 pasando**, sin inventar RED ni modificar repositorio/esquema/reglas de edad. T028/T029 revisadas; no requirieron nueva corrección de comportamiento.
- **T031–T032**: documentación sincronizada, módulo/SQL parametrizado/transacción/propiedad revisados. `ruff check` sobre script/pruebas: **pasa**. `mypy app/scripts/seed_hospital_data.py`: **sin errores**. No se añadieron dependencias, cambios de API, migraciones o frontend. El checker de formato detectó diferencias cosméticas; no es una puerta superada ni se declara que lo sea.
- **T033**: primer intento global bloqueado por jsonschema del extra sdd ausente; se instaló el extra ya declarado sin tocar lock. Primera reejecución completa: **203 passed**, 186.39 s. Revisión final añadió dos pruebas para comprobar rechazo de Target forjado/development no confirmado **antes de conectar**, incluso al invocar run_command directamente: RED **2 fallos**, luego GREEN **31 unitarias / 66 BD-04**. Última suite global con integración exigida y sandbox autorizado: **205 passed, 0 failures, 0 errors, 0 warnings, sin skips**, 127.39 s. Ruff y mypy reejecutados tras esa mejora también pasan. Validación local del backend completada; no acredita frontend ni aceptación humana.
- **T035**: `python -m alembic upgrade head --sql`, URL de prueba explícita y UTF-8: **exit 0**, SQL BEGIN/COMMIT hasta `p9q909633lm5`. También aplicado íntegro únicamente en la fixture aislada; no migración online/desarrollo.

### Gate frontend superado — T034

- Primer `npm test`: jsdom ausente; primer `npm run build`: tipos jest-dom ausentes. Se instalaron únicamente dependencias declaradas con `npm install --ignore-scripts --package-lock=false`; sin modificar package.json, lock ni código frontend. npm informó incompatibilidad de engine de jsdom 29.1.1 con Node 22.12.0, además de 7 avisos de auditoría (2 moderate/5 high); no se ejecutó audit fix.
- **Histórico, ya superado**: con Node 22.12.0, los controles normales fallaron con `ReferenceError: module is not defined` en `frontend/tailwind.config.js:2`; el diagnóstico con `NODE_OPTIONS=--no-experimental-require-module` permitió el build pero Vitest falló con 8 errores de workers `ERR_REQUIRE_ESM` en una dependencia de jsdom. Estos intentos no acreditaron T034 y no se corrigió código frontend.
- **Evidencia final de T034**: Node portable **22.23.3** desde nodejs.org, SHA-256 oficial verificado, npm **10.9.9**, únicamente en los procesos de control. `NODE_OPTIONS` ausente, sin flags de compatibilidad ni cambios de configuración. Desde `frontend/`, **`npm test`: 8 archivos / 48 pruebas pasando**, 19.74 s; **`npm run build`: exit 0, cero errores TypeScript**, 6.88 s. El aviso de tiempos de plugins del build y la sugerencia de rendimiento de entornos Vitest son informativos, no fallos.
- Comparación SHA-256 de **287 archivos intactos**, sin archivos nuevos no ignorados; solo artefactos normales de build/cache ignorados. Node global quedó en 22.12.0 y npm 10.9.0: para reproducir el gate aprobado, seleccionar **Node 22.23.3/npm 10.9.9** en la terminal o usar la distribución portable. No se necesitan cambios de frontend ni un PR correctivo para acreditar T034 con ese entorno.

### Aceptación manual — T036–T039 completadas; BD-04 aceptada

- **T036**: completada con el reporte explícito del usuario: ejecución manual dentro de `mediflow-backend-dev`, destino mostrado y confirmado `postgres:5432/mediflow_dev`, resultado `{"total":[10,4,5],"created":[10,4,5],"reused":[0,0,0]}` y código de salida **0**. **Fecha de ejecución no comunicada; hora exacta no anotada por el usuario**. No se infiere un timestamp a partir del chat, de la fecha del documento o de timestamps de la base. La fuente es el resultado real comunicado por el desarrollador, no una nueva ejecución ni una comprobación Scalar del agente; no acredita T037–T039.
- **T037**: completada por conformidad expresa del usuario, con captura de Scalar mostrando `GET /api/v1/patients`, **200 OK** y `total: 10`, más JSON completo con DNI `99040001`–`99040010` exactamente una vez. Las diez fechas coinciden con el manifiesto de quickstart y las edades observadas, en ese orden, son **36, 26, 51, 41, 66, 30, 16, 46, 21, 70**. La revisión previa de PostgreSQL fue de solo lectura: `TimeZone = UTC`, `CURRENT_DATE = 2026-10-08`, 10/10 fechas y edades correctas; instante de esa consulta `2026-10-08T04:23:01.109843+00:00`, cuando en Lima la fecha era `2026-10-07`. El repositorio calcula `EXTRACT(YEAR FROM age(CURRENT_DATE, fecha_nacimiento))::INT`; el spec US1.6/FR-010 usa la referencia vigente del backend, sin exigir Lima. Por ello 36 para DOB `1990-10-08` cumple; con referencia `2026-10-07` daría 35. No se cambia la lógica ni se fija una edad. `created_at` del JSON es timestamp de registro/transacción, no hora exacta reconstruida del comando T036. Género/sexo/teléfonos/correo permanecen NULL válidos según data-model y esquema; no se rellenaron.
- **T038**: completada por petición expresa del usuario después de su comprobación en Scalar. `GET /api/v1/users` devolvió **HTTP 200**, según su reporte, usando la cuenta ADMINISTRADOR existente de DNI `12345678`. El array aportado tiene ocho usuarios en total: cada uno de los cuatro DNI BD-04 aparece una vez, todos OPERADOR/ACTIVO, con Medicina General (`99041001`), Cardiología (`99041002`), Neumonología (`99041003`) y Traumatología (`99041004`). Los otros cuatro son baseline ajeno y no se contabilizan como semilla ni se reproducen sus datos personales. No se creó otra cuenta ni se cambiaron contraseñas/roles. La fuente HTTP es la observación del usuario, no una petición del agente; no se inventa fecha/hora de consulta. La inspección anterior de fuentes/dependencias desplegadas y la consulta SQL de solo lectura se mantienen como corroboración separada, no como sustituto de Scalar. M01 no está autorizado para `/users`; no se necesita comprobar su 403 para completar T038.
  - **Parte documental verificada por el usuario**: cinco consultas individuales en Scalar, cuerpos JSON aportados y confirmación explícita posterior «Los cinco documentos devolvieron HTTP 200 en Scalar, con los IDs y prioridades que ya compartí». BD04-DOC-001/200/Urgente; BD04-DOC-002/200/Rutina; BD04-DOC-003/200/Ambiguo; BD04-DOC-004/200/Rutina; BD04-DOC-005/200/Urgente. No se infirieron códigos HTTP a partir de los cuerpos ni se inventó fecha/hora de consulta.
  - **Estado inicial, no triaje ejecutado**: la lectura PostgreSQL previa confirmó status recibido, nodos_ejecutados=[] y destino_principal=NULL en los cinco documentos, metadata BD-04/v1 y cero filas de esos IDs en cola_procesamiento. `Cola_Rutina` en las respuestas es exclusivamente el fallback del formateador `documents.py:101`, no un destino persistido ni una decisión clínica Urgente/Ambiguo → Rutina. Es compatible con el modelo que deja destino NULL y no ejecuta la orquestación; no se cambiaron reglas, estados o datos.
  - **Evidencia saneada**: se conserva solo el extracto de los cuatro médicos en quickstart. El comando compartido incluía un token Bearer; no se copia a archivos, salidas o comandos. Su exposición no invalida los resultados observados de T038, pero requiere revocación de esa sesión y limpieza antes del cierre T039. El agente no utilizó el token ni revocó sesiones por su cuenta.
- **T039**: completada con la aceptación final explícita del usuario **«si acepto»**, en respuesta a la solicitud de aceptación de BD-04 después de su confirmación de limpieza. Evidencias automáticas y manuales consolidadas, con cobertura revisada abajo. El clúster nativo propio fue detenido con pg_ctl después de la última suite y se retiraron sus archivos de credenciales temporales; su directorio de datos sintéticos permanece detenido en el temporal aprobado, sin borrar datos clínicos del usuario. El usuario confirmó que cerró las cuatro sesiones usadas durante la verificación: **dos de M01 y dos del ADMINISTRADOR**, y posteriormente que **completó la limpieza** de secretos locales solicitada. Se registran únicamente sus confirmaciones, sin tokens ni credenciales y sin atribuir códigos HTTP, mensajes, método o fecha/hora no comunicados; el agente no comprobó ni modificó sesiones en PostgreSQL ni verificó la limpieza local. No se afirma que limpiar copias locales elimine el contenido ya compartido en el chat. El cierre se basa en la aceptación posterior expresa, no en inferirla de la limpieza. **BD-04 queda completada y aceptada, sin publicación Git.**

No hay hooks before/after: `.specify/extensions.yml` no existe. Las 39 casillas completadas se respaldan en este registro: T001–T035 por evidencia automática, T036 por el reporte manual del usuario, T037 por captura/JSON Scalar y corroboración de lectura, T038 por usuarios/documentos observados y confirmados por el usuario, y T039 por consolidación/cierre técnico y aceptación final explícita tras sus confirmaciones de cierre de sesiones/limpieza. T027–T029 fueron satisfechas por comportamientos ya implementados y pruebas en verde, sin fabricar fallos ni correcciones adicionales. No quedan tareas pendientes de BD-04. Esta actualización documental no repite pruebas ni autoriza reejecutar desarrollo, usar el token expuesto, commit, push o crear el PR.

### Revisión de cobertura para T039 — basada en evidencia ya obtenida

- **FR-001–002 / SC-001**: manifiesto y primera carga aislada T007–T015, carga manual T036 y pacientes T037: 10/4/5 identidades sintéticas reconocibles; DOB válidas y contactos opcionales NULL.
- **FR-003 / SC-003**: roles/especialidades T008 y credenciales T024–T030; Scalar T038 confirma cuatro OPERADOR/ACTIVO, una cuenta por especialidad. Scalar no demuestra hashing: esa parte se acredita en PostgreSQL aislado.
- **FR-004–006 / SC-005 y SC-007**: T008–T009/T013 y cinco GET de T038: documentos únicos con relaciones, tres prioridades permitidas, sin episodios ni archivos físicos. Colores solo presentación existente revisada en el spec, sin nueva evidencia visual de frontend ni nuevas reglas clínicas.
- **FR-007–008 / SC-002 y SC-006**: T016–T023 y suite final: dos cargas con commits sobre el mismo sandbox, snapshots/UUID/FK/credenciales intactos, conjunto parcial, conflictos y conservación de ajenos. No se repitió la semilla de desarrollo para acreditar idempotencia.
- **FR-009**: T008/T012/T024–T030, helper hash_password y entradas ocultas verificadas. No se almacenan contraseñas en claro en BD-04. El token compartido pertenece a una sesión manual de la aplicación, no a la semilla; el usuario confirma el cierre de sus cuatro sesiones de verificación y que completó la limpieza de secretos locales.
- **FR-010 / SC-004**: T026 y suite final prueban edad dinámica/cumpleaños/29 de febrero sin edad persistida; T037 corrobora DOB/edades con CURRENT_DATE en UTC.
- **FR-011 / SC-006**: snapshots de configuración T009/T018/T023 y suite final, sin cambio automático LOCAL/OCI.
- **FR-012–013 / SC-008**: contrato/quickstart, gates finales T030–T035 y evidencia manual T036–T038 separada de integración aislada. No faltan resultados Scalar; el cierre de sesiones y la limpieza de secretos están confirmados por el usuario. T039 se completa con su aceptación humana explícita posterior.

### Revisión documental para preparar el PR — anterior al ajuste de CLI

- Solo se actualizaron `tasks.md` y `quickstart.md`: evidencia final Node/npm, eliminación del bloqueo vigente de T034 y estados respaldados por pruebas previas. No se repitieron pruebas; backend/frontend permanecen sin cambios frente a los controles ya aprobados, verificado mediante SHA-256.
- Revisado el conjunto completo de **13 archivos**: un cambio versionado (`backend/pyproject.toml`, solo marcador) y 12 nuevos (script/paquete, dos pruebas y ocho documentos de esta feature). Sin cambios de frontend, API, migraciones o archivos fuera de BD-04; el repositorio no incluye los temporales de PostgreSQL o Node.
- Revisión de secretos por lectura y búsqueda de indicadores de claves privadas/tokens/JWT: **sin secretos reales detectados**. Las URL con credenciales literales están solo en mocks/pruebas sintéticas de rechazo y saneamiento; las contraseñas de integración se generan de forma efímera. No hay `.env`, credenciales reales, logs, bases de datos o artefactos de build en el conjunto a entregar.
- `git diff --check`: sin errores. Para los 12 archivos nuevos, `git diff --no-index --check` contra NUL tampoco reportó errores de whitespace; su exit 1 indica diferencias, no un fallo de whitespace. Avisos LF/CRLF únicamente informativos.
- 35 tareas completadas y cuatro pendientes comprobadas; enlaces locales y bloques de código de los documentos válidos. Sin staging, commit, push, creación de PR, carga en `mediflow_dev` ni Scalar. El usuario recibe título/descripción de PR para copiar y conserva la aceptación final T036–T039.

### Simplificación manual de CLI autorizada — fase anterior al reporte de T036

- **Compatibilidad**: spec aprobado FR-009/FR-012/FR-013 permite recibir claves de forma segura y documentar una ejecución manual simple; no exige que las claves lleguen exclusivamente por variables. Se conserva el spec sin alterar requisitos. El contrato de CLI y quickstart ahora documentan prompts ocultos para cuentas nuevas y el alias Docker de URL; no cambian API/OpenAPI, frontend o migraciones.
- **Implementación acotada**: `parse_target` normaliza únicamente en development `postgresql+asyncpg://` a `postgresql://`, manteniendo base permitida, rechazo de query/fragment y confirmación humana. `run_command` conserva su firma y valida destino efectivo/esquema antes del preflight de usuarios por SELECT. `development_passwords` verifica propiedad antes de pedir claves, conserva variables ya suministradas y solicita con `getpass` solo las ausentes para cuentas nuevas. No introduce claves en el entorno ni archivos. `GetPassWarning` aborta antes de fallback visible; claves inválidas/EOF/Ctrl+C no inician la carga y se cierra la conexión. El loader conserva hash_password, bloqueo asesor, revalidación de propiedad, transacción, UPSERT y commits idempotentes.
- **TDD y backend**: base previa **205 passed**, 208.36 s, en PostgreSQL 17 nativo recién aprovisionado exclusivamente para test. RED unitario limpio **14 failed / 39 passed**, 4.48 s, antes de producción; las dos pruebas PostgreSQL nuevas también detectaron el helper ausente. Un error inicial de la prueba fue corregido como problema del harness, no evidencia de comportamiento. GREEN BD-04 **90 passed**, 44.89 s (53 unitarias/contrato y 37 del archivo PostgreSQL, incluidos sus controles). Verificación final global **229 passed**, 259.00 s, sin fallos, errores, warnings o skips; `BD04_REQUIRE_POSTGRES=1`, `BD04_TEST_SANDBOX_OWNED=1`, DATABASE_URL vacía en pytest y conexión dedicada `127.0.0.1:55432/mediflow_bd04_test`.
- **Evidencia real aislada**: recogida de cuatro claves mediante doble de getpass no modifica ningún snapshot; primera carga con commit crea 10/4/5 y verifica hashes existentes. Segunda carga sin claves no pide ninguna, reutiliza 10/4/5 y conserva el snapshot completo leído desde otra conexión, sin limpieza intermedia. Conjunto parcial pide solo claves faltantes y conserva hash/salt/estado de la cuenta propia existente. Los escenarios anteriores de colisiones, rollback, concurrencia, dos CLI, edades y ausencia de efectos permanecen en verde.
- **Terminal Linux real, carga simulada**: comprobación adicional dentro del backend existente, Python 3.11.16, con pseudoterminal y conexión/loader explícitamente mockeados. Confirmación y cuatro prompts reales: eco desactivado durante los cuatro, ninguna contraseña en la transcripción, exit 0 y cierre de conexión simulado. **Cero conexiones reales y cero cargas**; esto no acredita T036. Los problemas de captura/encoding de los runners auxiliares se corrigieron únicamente en temporales y no se contaron como aceptación.
- **Gates finales**: Ruff del script y dos archivos de pruebas pasa; `mypy app/scripts/seed_hospital_data.py` sin errores. `python -m alembic upgrade head --sql` exit 0, BEGIN/COMMIT y head `p9q909633lm5`, sin migración online. Frontend normal con Node **22.23.3/npm 10.9.9**, sin NODE_OPTIONS: `npm test` **48 pruebas / 8 archivos**, 24.36 s; `npm run build` exit 0, cero errores TypeScript, Vite 19.36 s. Mensajes de rendimiento de Vitest y PLUGIN_TIMINGS son informativos; no se modificó configuración para silenciarlos.
- **Alcance/cierre técnico**: solo script, sus dos archivos de pruebas, contrato, tasks y quickstart cambiaron frente a la base de esta revisión. SHA-256 confirma intactos frontend, API, migraciones, dependencias y conftest. El nuevo sandbox propio se detuvo y se retiraron metadatos/contraseñas temporales; sus datos sintéticos quedan detenidos en el temporal aprobado. No se reconstruyó/recreó ningún contenedor, aplicó migración de desarrollo, cargó mediflow_dev, abrió Scalar, hizo commit/push o creó PR. **Estado al cerrar esa fase, antes del reporte manual: T036–T039 pendientes**.

El estado pendiente descrito en las dos revisiones históricas anteriores corresponde a esas fases, antes del reporte manual. El estado vigente está en Status y en «Aceptación manual»: T001–T039 completadas y BD-04 aceptada por el usuario. Al registrar T036 solo se actualizaron este documento y quickstart, sin nuevos tests, consultas de base, ejecuciones de semilla o modificaciones de código/frontend. Para revisar T037 y permisos de T038 solo se inspeccionaron fuentes y consultó PostgreSQL en lectura; al registrar T037–T039 solo se modifican estos dos documentos, sin cambios de código/spec/API/frontend/permisos/datos ni commit/push/PR.
