# Research: BD-04 — Decisiones del plan

Investigación del repositorio en modo lectura. Sin conexión PostgreSQL, ejecución de semilla o código nuevo. Alcance: [spec.md](spec.md), aprobado por el usuario. Se incorporó investigación delegada sobre aislamiento/migraciones.

## 1. Conexión explícita y unidad de carga

- **Decision**: Función asíncrona en el script solicitado, con conexión asyncpg y entradas inyectadas, consultas parametrizadas y una transacción por carga; CLI maneja autorización/cierre.
- **Rationale**: Repositorios existentes no ofrecen atomicidad de 19 filas. postgres_storage además copia edad, consulta almacenamiento y agrega historial. conftest vacía DATABASE_URL y aplica mocks; settings cachea .env y pool global puede existir antes de cambiar variables.
- **Alternatives considered**: Endpoints de creación (sin unidad atómica/idempotencia); guardar_resultado (efectos de pipeline); repositorio genérico nuevo (exceso de alcance); conexión explícita seleccionada.

## 2. Identidades/propiedad sin esquema nuevo

- **Decision**: Manifiesto estable, UUIDv5, claves naturales y marca documental en metadata; verificar propiedad/compatibilidad antes de reutilizar. Bloqueo asesor transaccional estable para serializar cargas. Conservar credenciales existentes.
- **Rationale**: DNI/HC de pacientes, documento_identidad y documento_id ya son únicos. Pacientes/usuarios no tienen metadata de semilla; UUID determinista identifica propiedad sin tabla nueva. Nombre o salt no son identidad segura.
- **Alternatives considered**: UUID aleatorio por ejecución (regenera identidad); reconocer solo DNI (apropiación de filas ajenas); tabla/migración auxiliar (fuera de alcance); truncar (prohibido).

## 3. Registros sintéticos, no procesamiento clínico

- **Decision**: Tipo JSON existente, defaults recibido/Admision, prioridad del manifiesto, FK paciente y episodio/edad/rutas NULL; no IA ni destinos clínicos.
- **Rationale**: Se solicitan registros ficticios, no originales ni diagnósticos. Esquema admite campos clínicos NULL; trigger de cola solo actúa con destino. Ambiguo conserva incertidumbre; ámbar es presentación.
- **Alternatives considered**: PDF simulado (fuera de alcance), triage_service (efectos/dependencia LLM), diagnósticos/routing arbitrarios (reglas inventadas).

## 4. Credenciales y RBAC

- **Decision**: Secretos externos por cuenta, sin defaults/flags de passwords; hash_password y política existentes. Hash/salt solo en creación; las cuatro cuentas son OPERADOR, sin administradores nuevos.
- **Rationale**: security retorna hash/salt; users exige 12 caracteres, mayúscula/minúscula/número/símbolo. ADMINISTRADOR es quien consulta /users, no el médico semilla. auth usa sesiones persistidas, no test tokens.
- **Alternatives considered**: Password pública, salt fijo o algoritmo distinto (rechazados); reset en cada carga (rompe credenciales intervenidas).

## 5. Aislamiento efectivo de PostgreSQL

- **Decision**: Instancia Docker PostgreSQL 17 desechable, base mediflow_bd04_test, variable dedicada, conexiones/guardias explícitas. Desarrollo exige confirmación interactiva.
- **Rationale**: Cambiar DATABASE_URL o marcar repository_mock no acredita persistencia y puede usar caches. Schema en mediflow_dev sigue tocando desarrollo. Compose de BD monta datos/init de desarrollo, no es sandbox.
- **Alternatives considered**: Mocks (insuficientes), schema en desarrollo (rechazado), Testcontainers (dependencia innecesaria); servidor separado aprovisionado con guardias equivalentes (aceptable).

## 6. Esquema de prueba desde SQL Alembic offline

- **Decision**: Emitir SQL head offline con URL explícita de test y aplicarlo íntegro en conexión aislada ya validada; verificar revision/esquema resultante. No cambiar alembic/env.py.
- **Rationale**: env.py puede sobrescribir sqlalchemy.url desde settings y abrir otro engine con asyncio.run; validar una conexión no protege esa otra. SQL offline contiene límites de transacción para enums. Aplicación íntegra en sandbox evita resolución online de .env; no separar por semicolons de funciones/DO blocks.
- **Alternatives considered**: Alembic online sin guardia efectiva (inseguro), plumbing global nuevo (exceso de alcance), DDL abreviado de tests (oculta incompatibilidades), init SQL de infraestructura (no equivale a cadena Alembic actual).
- **Observación**: Migraciones insertan tres documentos y cuatro usuarios históricos y rotan sus credenciales. Preservar baseline; no esperar totales de tabla 10/4/5 ni todas las edades históricas NULL.

## 7. Dos commits y edad calculada en el servidor

- **Decision**: Primera carga commit, lectura desde otra conexión, segunda carga commit sin limpieza; comparar manifiesto/snapshots. Edad real PostgreSQL con referencias controladas solo en tests.
- **Rationale**: Rollback intermedio probaría dos primeras inserciones, no reejecución. Congelar Python no cambia CURRENT_DATE. patient_repository usa age; cumpleaños se prueba sobre misma fila sin actualizar DOB/edad.
- **Alternatives considered**: Comparar nuevos hashes salados (incorrecto), borrar entre cargas (invalida evidencia), mocks o SQL-text-only (insuficientes). Febrero 29 sigue PostgreSQL.

## 8. Dos momentos y límite de entrega

- **Decision**: Revisar plan, implementar después y verificar con PostgreSQL aislado; solo luego ejecutar manualmente en desarrollo y comprobar pacientes en Scalar, médicos/documentos separadamente.
- **Rationale**: Cumple plan operativo y FR-013 sin autorizar escrituras durante planificación.
- **Alternatives considered**: Cargar desarrollo ahora (prohibido), validar solo Scalar o solo integración (omite un momento aprobado).

## Fuentes

- backend/app/core/security.py, core/config.py: credenciales/settings.
- backend/app/repositories/postgres_storage.py, patient_repository.py, user_repository.py: pools, efectos, claves, edad.
- backend/app/api/v1/patients.py, users.py, documents.py, auth.py: formas/permisos existentes.
- backend/tests/conftest.py, test_migrations.py, test_episodios_db.py: aislamiento y SQL offline.
- backend/alembic/env.py y versions/: cadena de esquema, datos históricos, defaults/triggers.
- backend/pyproject.toml e infrastructure/docker/docker-compose.db.yml: dependencias y límites del compose.
- AGENTS.md, Constitución, guía de secretos y plan operativo Tarea 1.4.

Sin aclaraciones funcionales pendientes. Flags/variables son propuestas técnicas a revisar. Los atributos opcionales no solicitados no se convierten en reglas clínicas.
