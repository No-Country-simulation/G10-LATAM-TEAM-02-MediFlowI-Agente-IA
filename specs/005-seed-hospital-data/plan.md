# Implementation Plan: BD-04 — Semilla hospitalaria de desarrollo

**Branch**: `dev-krystopher` (sin cambio de rama) | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: `specs/005-seed-hospital-data/spec.md`, aprobado explícitamente por el usuario al solicitar este plan. Spec Kit devuelve el contexto `005-seed-hospital-data`, no una rama Git creada por este comando.

**Status**: Diseño listo para revisión. Sin código, ejecución de semilla, cambios en `mediflow_dev` ni `tasks.md`. La etiqueta Draft histórica del spec no invalida la aprobación expresa; no se modifica ese documento.

## Summary

Diseñar solo el futuro módulo `backend/app/scripts/seed_hospital_data.py`: 10 pacientes ficticios, 4 médicos OPERADOR de Medicina General, Cardiología, Neumonología y Traumatología, y 5 registros ficticios de documentos_triaje. Sin episodios, archivos físicos, llamadas al agente, cambios de esquema o frontend.

Manifiesto estable, reconocimiento de propiedad, SQL parametrizado con asyncpg y una transacción por carga. Conservar identidades y credenciales al repetir; UPSERT por documento_id y rechazo de colisiones ajenas. Contraseñas de entradas seguras mediante `app.core.security.hash_password`; nunca edad persistida.

Dos momentos: primero pruebas automáticas con PostgreSQL real aislado, incluidas dos ejecuciones confirmadas sin limpieza intermedia; después, con el script terminado y verificado, ejecución manual en desarrollo y comprobación visual en Scalar. Este plan no autoriza ejecutar ese segundo momento ahora.

## Technical Context

**Language/Version**: Python 3.12+ conforme a la Constitución; el paquete backend declara mínimo 3.11. No se propone bajar el mínimo constitucional ni cambiar packaging por BD-04.

**Primary Dependencies**: asyncpg, módulo de seguridad existente, biblioteca estándar (argparse, asyncio, uuid, fechas), pytest/pytest-asyncio y Alembic ya declarados. Docker CLI para aprovisionar PostgreSQL desechable; sin dependencia Testcontainers nueva.

**Storage**: PostgreSQL 17, esquema existente hasta Alembic head. Instancia de pruebas separada, sin volúmenes ni scripts de inicialización de desarrollo. Sin persistencia física documental.

**Testing**: Unitarias de manifiesto/entradas e integración opt-in `postgres_integration` con conexión real inyectada. La ejecución explícita de integración falla si falta un destino seguro; mocks/skips no acreditan idempotencia.

**Target Platform**: Backend local Windows/PowerShell y Linux/CI con PostgreSQL aislado; aceptación manual sobre backend/Scalar existentes.

**Project Type**: CLI interna de mantenimiento de desarrollo, no servicio HTTP nuevo.

**Performance Goals**: 19 filas lógicas; consistencia y no duplicación. No se inventa SLA ni benchmark.

**Constraints**: Destino explícito, confirmación humana de desarrollo, atomicidad, sin secretos en Git/logs, edad calculada, sin reset de contraseñas, sin episodios/archivos, almacenamiento manual intacto, sin migraciones implícitas.

**Scale/Scope**: Solo Tarea 1.4 / BD-04. No se inventan diagnósticos, CIE-10, scores ni routing. Colores exclusivamente visuales de las prioridades existentes; Ambiguo significa incertidumbre.

## Constitution Check

*Revisión antes de investigación y después del diseño; no equivale a certificar una implementación inexistente.*

- **I — TDD/calidad**: Diseño conforme: empezar la implementación con pruebas, conservar suites, exigir pytest/Vitest/build/SQL offline en verde. Las verificaciones previas en [checklist](checklists/requirements.md) están bloqueadas por dependencias ausentes; no se declaran superadas.
- **II — Consulta/alcance**: Decisiones clínicas y alcance aprobados; propuestas técnicas explícitas para revisión, sin nuevos roles ni equivalencias de gravedad.
- **III — Persistencia**: PostgreSQL real, edad desde fecha_nacimiento, legado paciente_edad NULL, UPSERT, configuración intacta. Sin tablas/columnas nuevas que requieran migración/comentarios.
- **IV — RBAC**: Cuatro OPERADOR con especialidad; ADMINISTRADOR existente solo para consulta de usuarios, sin nuevas cuentas privilegiadas o permisos de auditoría.
- **V — Trazabilidad**: Registros sintéticos recibidos, no resultados de procesamiento/auditoría aparentes. Conservar datos ajenos; no borrar registros clínicos. Teardown solo de infraestructura de prueba propia.

**Resultado inicial**: Sin infracciones de diseño injustificadas. Puertas de ejecución pendientes de implementación/entorno.

**Reevaluación posterior**: Los cinco artefactos conservan los límites. No se usa el repositorio general de triaje (evita edad fija, archivos e historial repetido); preparación del esquema únicamente en conexión aislada comprobada; autorización test/desarrollo separada. Sin excepciones constitucionales solicitadas.

## Project Structure

### Documentation (this feature)

```text
specs/005-seed-hospital-data/
├── spec.md                     # aprobado; sin cambios
├── checklists/requirements.md   # existente; sin cambios
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/seed-command-contract.md
```

### Source Code (repository root)

Ubicaciones previstas **para implementación posterior**, no creadas por este plan:

```text
backend/
├── app/scripts/__init__.py
├── app/scripts/seed_hospital_data.py
├── tests/test_seed_hospital_data.py
├── tests/test_seed_hospital_data_postgres.py
└── pyproject.toml              # registro del marcador propuesto
```

**Structure Decision**: Manifiesto tipado y carga en un módulo pequeño; conexión/entradas inyectadas y CLI controla adquisición, cierre y confirmación. Sin repositorio genérico, API o capa de almacenamiento nuevos; no hace falta entry point adicional. No crear tasks.md.

## Phase 0 — Investigación concluida

Decisiones/alternativas en [research.md](research.md). Se contrastaron plan operativo, seguridad, APIs, repositorios, fixtures y migraciones sin conectar PostgreSQL. No quedan aclaraciones funcionales. Flags/variables son propuestas del diseño, no interfaces ya disponibles.

## Phase 1 — Diseño de la carga

1. Validar manifiesto 10/4/5, prioridades, OPERADOR, cuatro especialidades, fechas, credenciales y destino. Importar el módulo no produce efectos.
2. Validar URL antes de conectar y destino efectivo al conectar. Desarrollo exige confirmación interactiva; tests solo usan sandbox registrado por su fixture.
3. Abrir conexión asyncpg explícita y comprobar esquema sin migrarlo. Bloqueo asesor transaccional de clave BD-04 estable para serializar ejecuciones y evitar carreras de comprobación/inserción.
4. En una transacción, comprobar propiedad/compatibilidad por UUID y claves naturales; insertar/reutilizar pacientes y usuarios; persistir documentos con UPSERT por documento_id restringido a filas propias compatibles. Conflicto tardío revierte esta ejecución completa.
5. Hash/salt solo al crear usuarios; conservar credenciales/estado existentes y no generar sesiones.
6. Edad documental, episodio, destino clínico y rutas físicas sin asignar; defaults recibidos vigentes, sin servicios de triaje.
7. Verificar conjunto por identidades, confirmar transacción y devolver cantidades saneadas. Cerrar conexión siempre; no cambiar LOCAL/OCI.

Campos/propiedad en [data-model.md](data-model.md); interfaz/errores en [contrato](contracts/seed-command-contract.md).

## Pruebas automáticas — primer momento

### Aislamiento y preparación

- PostgreSQL 17 desechable separado, puerto local propio, sin volúmenes de desarrollo. `BD04_TEST_DATABASE_URL` apunta a `mediflow_bd04_test` de ese sandbox, nunca a mediflow_dev.
- Fixture explícita `postgres_integration`; mantener DATABASE_URL vacía y mocks autouse de la suite ordinaria. Integración invoca carga con conexión real. Para consultas de pacientes inyectar pool real en el repositorio, no resultados mock.
- Cada conexión se valida antes de escritura/limpieza: URL parseada, base/host/puerto/usuario esperados y valores efectivos current_database/current_user/schema/search_path/endpoint. Validar una conexión no autoriza abrir otra sin guardia.
- Aprovisionar sandbox limpio por escenario; en entorno aprovisionado externamente, restaurar únicamente el recurso desechable propiedad de la suite entre escenarios. Nunca limpiar entre ambas cargas de idempotencia. Teardown después de aserciones; no limpiar recursos arbitrarios del usuario.
- Esquema: emitir SQL Alembic head offline en subproceso con URL de test explícita y aplicarlo íntegro a la misma conexión asyncpg aislada comprobada. Respetar BEGIN/COMMIT; no dividir por semicolons ni envolver en otra transacción. No cambiar alembic/env.py ni invocar migración online desde el loop pytest: evita otra conexión que pueda resolver .env de desarrollo.
- Verificar alembic_version y columnas/enums tras bootstrap; salida no SQL o error aborta fixture. Las migraciones ya insertan usuarios/documentos históricos: snapshot baseline y conteos exclusivamente BD-04.
- Suite ordinaria puede omitir integración no solicitada; ejecución explícita de integración/CI debe fallar si falta URL, guardia o servidor. Skips no prueban persistencia.

### Casos y evidencias

- **Primera carga (FR-001–006)**: conteos por identidad 10/4/5, rol/especialidades, tres prioridades, FK correcta, episodio/edad nulos y ausencia de archivos/rutas nuevas.
- **Dos cargas (FR-007)**: commit de primera, lectura desde conexión nueva, commit de segunda sin rollback/borrado entre cargas. Comparar UUID/claves/FK/credenciales. También dos subprocesos CLI test independientes.
- **Parcial/conflictos (FR-007–008)**: completar subconjunto propio, rechazar colisiones UUID/clave/HC o metadata ajena; conflicto tardío prueba atomicidad.
- **Conservación (FR-008/011)**: snapshots de filas ajenas, episodios, configuración, auditorías/notificaciones/colas; sin cambios de BD-04 ni duplicados por triggers. No cambiar LOCAL/OCI para fabricar casos.
- **Credenciales (FR-009)**: verificar las cuatro con verify_password, rechazar password incorrecta, ausencia de texto plano en datos/salida; segunda carga conserva hashes/salts aun con otra entrada, sin compararlos con un nuevo hash aleatorio.
- **Edad (FR-010)**: query real CURRENT_DATE; en tests exclusivamente, sustituir/parametrizar fecha en proyección SQL para día anterior y cumpleaños sobre misma fila sin actualizarla. Congelar Python no controla PostgreSQL. Febrero 29 sigue age de PostgreSQL. Esquema/JSON verifican ausencia de edad fija solo en filas BD-04.
- **Guardias/fallos (FR-012–013)**: URL/target efectivo dev en test, secretos ausentes para nuevas cuentas, fechas inválidas, esquema ausente o caída de conexión fallan sin escritura/éxito parcial. Import/help sin efectos; development no interactivo se rechaza.

Evidencias futuras de aserciones sin secretos; no se incluye implementación ni suite completa.

## Aceptación manual posterior — segundo momento

- Requisitos: script implementado/revisado, pruebas aisladas y gates del repositorio superados; permisos/sesión de desarrollo disponibles. No se ejecuta hoy.
- Desarrollador confirma mediflow_dev y ejecuta módulo; sin migraciones, resets o cambios de almacenamiento implícitos.
- Scalar: 10 pacientes/edad en GET /api/v1/patients; cuatro médicos OPERADOR en GET /api/v1/users con sesión ADMINISTRADOR existente; cinco documentos por ID. Endpoint de pacientes no acredita los otros conjuntos ni se descargan archivos inexistentes.
- Comandos futuros/resultados en [quickstart.md](quickstart.md). Manual no sustituye reejecución automática aislada.

## Trazabilidad

- FR-001–004: manifiesto/modelo y primera carga.
- FR-005–006: ausencia de episodios y prioridades existentes.
- FR-007–008: propiedad/transacción y doble carga/colisiones.
- FR-009–010: seguridad y edad real.
- FR-011: almacenamiento intacto y snapshots.
- FR-012–013: contrato/quickstart y dos momentos.

## Complexity Tracking

Sin infracciones que justificar. Sin servicios, dependencias Python, migraciones o cambios de desarrollo nuevos. Manifiesto estable y conexión explícita bastan para este volumen.
