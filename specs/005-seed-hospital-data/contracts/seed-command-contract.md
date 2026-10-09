# Contract: carga manual BD-04 y verificaciones existentes

Contrato implementado del módulo `app.scripts.seed_hospital_data`. No modifica OpenAPI ni autoriza ejecutar development durante las pruebas.

## Entradas y seguridad del destino

- Invocación: `python -m app.scripts.seed_hospital_data --target test` o `--target development`. Import y --help sin conexión/archivos/hash.
- `--target` es obligatorio; no hay destino predeterminado ni detección automática a partir de credenciales.
- Modo `test`: URL explícita de `BD04_TEST_DATABASE_URL`, solo base aislada `mediflow_bd04_test`; nunca fallback a `.env`, `DATABASE_URL` o al pool global de la aplicación.
- Modo `development`: `DATABASE_URL` explícita para `mediflow_dev`, solo ejecución interactiva manual. Mostrar host, puerto y nombre de base sin credenciales y exigir que el usuario escriba `mediflow_dev` para confirmar antes de cualquier escritura. La falta de terminal/confirmación rechaza la carga.
- URL de desarrollo: aceptar `postgresql://` y el alias `postgresql+asyncpg://` suministrado por Docker Compose; normalizar únicamente ese prefijo a un DSN nativo dentro del script. Sin modificar el entorno ni `.env`, sin permitir query/fragment u otras bases. El modo test conserva exclusivamente `postgresql://` y sus guardias existentes.
- Antes de conectar, validar la URL y el nombre de base permitido. Al conectar, corroborar `current_database()` con el destino declarado **antes de DML**. Para pruebas, la instancia además debe ser el servicio separado configurado por el responsable, nunca la instancia de desarrollo con otro `search_path` accidental.
- Credenciales de los cuatro médicos: conservar variables de entorno `BD04_PASSWORD_M01`–`BD04_PASSWORD_M04` para pruebas/automatización. En desarrollo, tras confirmar y validar destino/esquema, hacer un preflight de propiedad de usuarios mediante SELECT sin DML/bloqueos: pedir mediante `getpass` solo las contraseñas ausentes del diccionario para cuentas nuevas. No pedir ni restablecer claves de cuentas propias existentes; un conflicto de propiedad aborta antes de pedir claves. Sin contraseñas por argumentos CLI, defaults, archivos, variables nuevas de entorno ni claves impresas.
- Entrada oculta requiere terminal interactiva. Convertir `GetPassWarning` en error para impedir el fallback visible; EOF/Ctrl+C cancelan y cierran la conexión sin iniciar la carga. Una contraseña configurada pero inválida para una cuenta nueva se rechaza, no se sustituye silenciosamente por un prompt. Política vigente: mínimo 12 caracteres, mayúscula, minúscula, número y símbolo.
- La creación de una cuenta nueva requiere su contraseña y validación de política. En reejecución no se sustituyen credenciales de cuentas existentes. Las pruebas usan secretos efímeros exclusivos de la instancia aislada.
- Ejecución de integración exigida: marcador `postgres_integration` y `BD04_REQUIRE_POSTGRES=1`. Falta de URL/servidor/guardia produce fallo, no un skip exitoso. La suite ordinaria puede omitir integración no solicitada sin que eso certifique BD-04. La fixture requiere además `BD04_TEST_SANDBOX_OWNED=1` para restaurar exclusivamente el esquema del sandbox desechable propio entre escenarios; no restaura entre las dos cargas de idempotencia.
- El esquema requerido debe existir en public, con revisión Alembic vigente `p9q909633lm5`. El comando no crea base, tabla, enum, vista ni ejecuta Alembic; una incompatibilidad aborta con mensaje saneado.

## Unidad de carga y errores

- Función `seed_hospital_data(conn, passwords, target)` asíncrona reutilizable con conexión asyncpg, diccionario de secretos por M01–M04 y `Target` validado con `parse_target`. Valida manifiesto/destino/esquema y crea su propia transacción; rechaza una transacción externa que oculte commits. Sin singleton de pool o `.env` de desarrollo. La CLI adquiere/cierra conexión; el loader controla commit/rollback y bloqueo asesor BD-04. Reutiliza `hash_password` y `validar_password_segura` vigentes sin modificar sus firmas.
- `run_command` conserva su firma. Solo en development confirmado valida destino/esquema y recoge claves en memoria con `development_passwords` antes de invocar el loader. Este preflight no sustituye las comprobaciones del loader bajo bloqueo asesor: ante cambios concurrentes se revalida propiedad y se aborta con rollback si ya no es compatible. El loader y el modo test no solicitan entrada interactiva.
- Consultas parametrizadas; una transacción para las 19 filas lógicas. Conflicto/error revierte esa ejecución completa, sin eliminar registros de ejecuciones anteriores.
- Identidad, reconocimiento de propiedad y UPSERT de documentos: [data-model.md](../data-model.md).
- Éxito: JSON `total: [10,4,5]`, `created` y `reused` en orden pacientes/usuarios/documentos; código de salida `0`. Retorno Python `SeedResult` con tuplas created/reused. No presentar totales de toda la base como conteos semilla.
- Error de entrada/destino/credenciales/esquema/identidad/persistencia: código `1` y descripción saneada; argumentos inválidos/target ausente: `2`; ayuda: `0`. No mostrar URL completa, contraseña, hash, salt ni tracebacks que los revelen; tampoco repetir argumentos desconocidos que puedan contener secretos. No informar éxito parcial.
- Ni el import del módulo ni `--help` deben conectar, escribir o generar archivos. El modo test puede operar sin interacción; el modo development requiere confirmación humana.

## Consultas de aceptación manual posteriores

- Abrir Scalar del backend de desarrollo, normalmente `http://localhost:8000/scalar`, tras terminar el script y superar sus pruebas.
- Usar una sesión Bearer real mediante autenticación existente. Los `test-*-token` son fixtures de pruebas, no credenciales válidas de la instancia real.
- `GET /api/v1/patients` sin `search`: HTTP 200, objeto con `total` e `items`. Localizar los 10 `numero_documento` del manifiesto y comprobar `fecha_nacimiento` y `edad` por años cumplidos a la fecha del backend. No esperar `total == 10` si hay otros pacientes.
- `GET /api/v1/users`: HTTP 200, array de usuarios, requiere sesión **existente** `ADMINISTRADOR`. Localizar las cuatro cuentas del manifiesto y comprobar rol **OPERADOR** y las cuatro especialidades. No devolver ni consultar hashes/salts mediante esta interfaz.
- `GET /api/v1/documents/{documento_id}` para los cinco identificadores: HTTP 200 con ID esperado y `clasificacion.nivel_prioridad` admitida. Son registros, no archivos descargables. El listado `/documents` tiene límite y no prueba el total almacenado.
- El endpoint de pacientes no comprueba cuentas médicas ni documentos. Las pruebas de persistencia comprueban por separado FK, ausencia de episodios/edad fija, conservación de datos y duplicados.
- Ninguno de estos endpoints se agrega o modifica en BD-04; no se redefinen firmas ni se regenera el contrato OpenAPI.
