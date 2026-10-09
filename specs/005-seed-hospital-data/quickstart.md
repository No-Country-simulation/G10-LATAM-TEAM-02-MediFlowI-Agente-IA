# Quickstart: validación de BD-04

**Estado: BD-04 completada y aceptada por el usuario; T001–T039 completadas.** Evidencia en [tasks.md](tasks.md): backend 229 pruebas en verde (90 BD-04), Ruff, mypy del script y SQL Alembic offline pasan; frontend 48 pruebas en 8 archivos y build sin errores TypeScript con **Node 22.23.3/npm 10.9.9**. **T036**: carga manual reportada por el usuario en `mediflow-backend-dev`, destino confirmado `postgres:5432/mediflow_dev`, creados 10/4/5 y exit 0; fecha de ejecución no comunicada y hora exacta no anotada. **T037**: captura/JSON Scalar y comprobación PostgreSQL de fechas/edades usando `CURRENT_DATE` en UTC (`2026-10-08`). **T038**: usuarios HTTP 200 bajo ADMINISTRADOR existente y cinco documentos HTTP 200, según evidencia del usuario. **T039**: cobertura/evidencias consolidadas, sandbox propio detenido y credenciales temporales retiradas, cierre de cuatro sesiones (dos de M01 y dos del ADMINISTRADOR) y limpieza local confirmados por el usuario, seguido de su aceptación final explícita «si acepto». El agente no ejecutó la semilla, cambió permisos o completó campos opcionales. Sin commit, push o PR.

Alcance/campos: [spec.md](spec.md), [data-model.md](data-model.md). Opciones y guardias implementadas: [contrato](contracts/seed-command-contract.md).

## Prerrequisitos

- Python 3.12+, entorno backend con dependencias del proyecto y dev instaladas; PostgreSQL 17 disponible en un sandbox separado para integración.
- Script: `backend/app/scripts/seed_hospital_data.py`; pruebas: `backend/tests/test_seed_hospital_data.py` y `backend/tests/test_seed_hospital_data_postgres.py`. Manifiesto público de identidades sintéticas abajo, sin secretos.
- Docker disponible si se usa el sandbox local. No usar el compose/volúmenes de desarrollo para aprovisionar test.
- Secretos suministrados por entrada oculta o gestor de secretos según la guía del repositorio, nunca como texto público ni argumentos del comando.
- Iniciar los comandos Python desde `backend/`, con su intérprete de entorno. Los comandos siguientes usan `python`; en Windows puede sustituirse por `.venv\Scripts\python.exe` si ese entorno existe.
- Preparar dependencias ya declaradas con `uv sync --extra dev --extra sdd --frozen --link-mode copy`. La suite global usa también `jsonschema` del extra sdd. No se agregaron ni cambiaron dependencias/lockfiles por BD-04.
- Para los controles de regresión frontend, seleccionar **Node 22.23.3 y npm 10.9.9** en la terminal. Es el entorno comprobado; jsdom 29.1.1 no admite el Node 22.12.0 global de este equipo. No usar flags de compatibilidad ni cambiar frontend para BD-04. La distribución portable usada en los controles no modificó la instalación global.

## Manifiesto BD-04/v1 — exclusivamente ficticio

Nombres: `Paciente sintético NN` / `Médico sintético NN`, apellido `BD04`. No usar estos identificadores para personas reales. UUIDv5 derivados del namespace constante `7db6a203-fc73-5abe-bb54-f460519d6ba2` y `BD-04/v1/{patient|user|document}/{Pnn|Mnn|Dnn}`; no cambian entre invocaciones.

Pacientes (clave: numero_documento; historia_clinica; fecha_nacimiento):

- P01: `99040001`; `BD04-HC-001`; `1990-10-08`.
- P02: `99040002`; `BD04-HC-002`; `2000-02-29`.
- P03: `99040003`; `BD04-HC-003`; `1975-01-15`.
- P04: `99040004`; `BD04-HC-004`; `1985-03-20`.
- P05: `99040005`; `BD04-HC-005`; `1960-07-12`.
- P06: `99040006`; `BD04-HC-006`; `1995-12-05`.
- P07: `99040007`; `BD04-HC-007`; `2010-06-18`.
- P08: `99040008`; `BD04-HC-008`; `1980-09-25`.
- P09: `99040009`; `BD04-HC-009`; `2005-04-30`.
- P10: `99040010`; `BD04-HC-010`; `1955-11-02`.

Médicos (todos OPERADOR, sin claves públicas):

- M01: `99041001`, Medicina General; secreto externo `BD04_PASSWORD_M01`.
- M02: `99041002`, Cardiología; secreto externo `BD04_PASSWORD_M02`.
- M03: `99041003`, Neumonología; secreto externo `BD04_PASSWORD_M03`.
- M04: `99041004`, Traumatología; secreto externo `BD04_PASSWORD_M04`.

Documentos (registros tipo JSON, no archivos):

- `BD04-DOC-001`: P01, Urgente.
- `BD04-DOC-002`: P02, Rutina.
- `BD04-DOC-003`: P03, Ambiguo (incertidumbre, no gravedad intermedia).
- `BD04-DOC-004`: P04, Rutina.
- `BD04-DOC-005`: P05, Urgente.

Los documentos crean status `recibido` explícitamente: el enum lo admite, pero el default histórico de la columna es `pendiente_auditoria`. El script no cambia ese default ni el esquema. Canal `Admision` por default vigente; episodio/edad/rutas/destino NULL y metadata solo `seed_source: BD-04`, `seed_version: 1`.

## Momento 1 — pruebas automáticas con PostgreSQL aislado

### 1. Aprovisionar exclusivamente el sandbox

Desde una terminal separada, cargar en el entorno `POSTGRES_PASSWORD` con una clave exclusiva de test (entrada oculta); comprobar que no se imprime ni reutiliza la de desarrollo. Crear un contenedor desechable, sin montajes de datos del proyecto:

```powershell
docker run --rm --name mediflow-bd04-test -p 127.0.0.1:55432:5432 -e POSTGRES_DB=mediflow_bd04_test -e POSTGRES_USER=bd04_test -e POSTGRES_PASSWORD -d postgres:17
```

Si el nombre o puerto ya están ocupados, detenerse y revisar el recurso; no reemplazar/eliminar automáticamente un contenedor ajeno.

Comprobar disponibilidad del sandbox:

```powershell
docker exec mediflow-bd04-test pg_isready -U bd04_test -d mediflow_bd04_test
```

En la terminal de pruebas, suministrar `BD04_TEST_DATABASE_URL` de forma oculta para host `127.0.0.1`, puerto `55432`, usuario `bd04_test` y base `mediflow_bd04_test`. No copiar una URL de desarrollo ni imprimirla. Inyectar también `BD04_PASSWORD_M01`–`BD04_PASSWORD_M04`, secretos efímeros de test que cumplan la política vigente.

Las pruebas generan las cuatro contraseñas efímeras internamente; las variables de contraseña son necesarias solo para invocaciones CLI externas que creen cuentas nuevas. Antes de iniciar pytest, **registrar explícitamente como propio y desechable el sandbox recién creado**:

```powershell
$env:BD04_TEST_SANDBOX_OWNED = '1'
```

Esta variable autoriza exclusivamente a la fixture a restaurar `public` en `mediflow_bd04_test` entre escenarios. Nunca activarla sobre recursos compartidos o datos del usuario. Cada conexión verifica URL/base/usuario/esquema/search_path/endpoint efectivos; el loader no restaura esquemas. La doble carga ocurre antes de cualquier restauración, con dos commits reales y lecturas desde otra conexión. El teardown de la fixture solo cierra conexiones; al final se detiene el recurso desechable propio.

**Alternativa utilizada durante implementación**: Docker estaba instalado pero su daemon no estaba activo. Se aprovisionó una instancia nativa PostgreSQL 17 mediante `initdb` en un directorio nuevo bajo el temporal aprobado de OpenCode, escuchando solo en `127.0.0.1:55432`, usuario `bd04_test`, autenticación SCRAM y base `mediflow_bd04_test`. Se usaron credenciales aleatorias exclusivas; ninguna conexión al servicio de desarrollo. Esta alternativa está admitida en research.md (§5). Para reproducirla, el responsable debe aprovisionar un clúster nuevo con estas guardias; nunca reutilizar el data directory, servicio o puerto de desarrollo. Con Docker, el puerto interno efectivo es 5432; con el clúster nativo es 55432.

### 2. Esquema y pruebas de integración

La fixture prepara el esquema hasta Alembic head `p9q909633lm5` mediante SQL **offline** aplicado íntegramente sobre su conexión aislada validada, como describe [plan.md](plan.md). Usa `PYTHONIOENCODING=utf-8` en el subproceso para no corromper SQL/comentarios en Windows. No ejecutar `alembic upgrade head` online con configuración implícita ni montar init SQL de desarrollo.

Desde `backend/`, ejecutar las pruebas:

```powershell
python -m pytest tests/test_seed_hospital_data.py -v
```

Ejecutar el grupo real PostgreSQL con exigencia explícita:

```powershell
$env:BD04_REQUIRE_POSTGRES = '1'
python -m pytest tests/test_seed_hospital_data_postgres.py -m postgres_integration -v
```

`BD04_REQUIRE_POSTGRES` y el marcador están implementados. Ante URL ausente, destino inseguro o conexión fallida, esta ejecución falla, no pasa con skips. La suite ordinaria mantiene las guardias actuales que vacían DATABASE_URL; la integración usa la variable dedicada, nunca fallback a `.env`. La integración no solicitada puede omitirse, pero eso no acredita BD-04. No ejecutar escenarios en paralelo contra un mismo sandbox externo.

**Evidencia requerida**:

- Primera carga confirmada; consulta desde otra conexión demuestra persistencia real del conjunto 10/4/5.
- Segunda carga confirmada en la misma base y mismos datos sin borrar, recrear ni hacer rollback entre ejecuciones; UUID/claves/FK/credenciales y cantidades conservadas.
- Pruebas de CLI en dos subprocesos distintos usando `--target test`, ambos con guardias del destino efectivo. No se invoca el modo development desde pytest.
- Completar conjunto parcial; rechazar conflictos y fallo tardío con rollback de esa ejecución, sin sobreescribir ajenos.
- OPERADOR y cuatro especialidades; prioridades existentes; ninguna edad fija, episodio, ruta física, archivo o cambio de configuración.
- Edad real y cumpleaños con fechas de referencia controladas en SQL de test, sin alterar las fechas de nacimiento persistidas; verificación de las cuatro contraseñas mediante el helper existente.

Los documentos y usuarios de migraciones previas son baseline ajeno; no exigir totales de tabla 10/4/5 ni limpiar ese baseline para que las pruebas pasen.

### 3. Gates previos a aceptación en desarrollo

En backend, con integración exigida y destino de test protegido:

```powershell
python -m pytest
```

Validación de migraciones únicamente offline, con URL explícita de test durante ese comando:

```powershell
$env:DATABASE_URL = $env:BD04_TEST_DATABASE_URL
python -m alembic upgrade head --sql
Remove-Item Env:DATABASE_URL
```

En otra terminal con Node **22.23.3** y npm **10.9.9**, desde `frontend/`, sin `NODE_OPTIONS` de compatibilidad:

```powershell
npm test
npm run build
```

**Resultado registrado de T034**: control original normal **48 pruebas / 8 archivos**, 19.74 s, y build exit 0, cero errores TypeScript, 6.88 s. Tras la simplificación de CLI se repitieron ambos comandos normales: **48 pruebas / 8 archivos**, 24.36 s, y build **exit 0, cero errores TypeScript**, Vite 19.36 s. Node **22.23.3**, npm **10.9.9**, sin flags de compatibilidad ni NODE_OPTIONS. El aviso de tiempos de plugins y la sugerencia de rendimiento de entornos Vitest son informativos. No se cambió código, configuración, manifiestos o lockfiles frontend; la comparación SHA-256 original verificó 287 archivos intactos y la de esta revisión confirma nuevamente frontend intacto, con solo artefactos normales ignorados de build/cache.

Esos comandos no deben usar `mediflow_dev`. Los fallos anteriores con Node 22.12.0 quedaron superados usando el entorno compatible, sin corregir frontend. La versión global del equipo continúa en Node 22.12.0/npm 10.9.0: es necesario seleccionar el entorno aprobado antes de repetir estos comandos. Ante futuros fallos, detener la aceptación manual; tener los gates en verde no autoriza al agente a cargar desarrollo ni acredita Scalar. La revisión documental anterior no repitió pruebas; el ajuste posterior del script sí ejecutó de nuevo todos los gates exigidos.

### 4. Cerrar sandbox

Tras las aserciones/evidencias, comprobar que el nombre corresponde al contenedor desechable creado para esta guía y detener solo ese recurso:

```powershell
docker stop mediflow-bd04-test
```

Con `--rm` se retira su contenedor/datos efímeros; no se borran tablas clínicas de desarrollo ni se ejecuta `docker compose down -v` sobre el proyecto. Retirar las variables secretas de la terminal o cerrarla.

Los sandboxes nativos usados en la implementación original y en la simplificación de CLI ya fueron detenidos con pg_ctl después de sus suites finales; se retiraron los archivos temporales de contraseña/URL. Sus datos sintéticos permanecen detenidos en el temporal aprobado. Para una nueva ejecución, aprovisionar un sandbox nuevo y registrar de nuevo su propiedad; no se dejó un servidor de pruebas activo ni se tocó el servidor de desarrollo.

## Momento 2 — ejecución manual posterior en desarrollo

**T036–T039 completadas con evidencia registrada abajo y aceptación final explícita del usuario. No repetir la carga ni los GET para esta aceptación. Los pasos se conservan como referencia; cierre de sesiones y limpieza de secretos confirmados por el usuario.**

### Evidencia real reportada por el usuario — T036

- Ejecución manual dentro de `mediflow-backend-dev`; destino mostrado **`postgres:5432/mediflow_dev`** y confirmado por el usuario.
- Resultado comunicado:

```json
{"total":[10,4,5],"created":[10,4,5],"reused":[0,0,0]}
```

- Código de salida: **0**. Primera carga reportada: 10 pacientes, cuatro médicos y cinco documentos creados, sin registros reutilizados.
- **Fecha de ejecución: no comunicada. Hora exacta: no anotada por el usuario.** No se inventa ni reconstruye un timestamp.
- Fuente: reporte explícito del desarrollador en el chat sobre su ejecución real. El agente no volvió a ejecutar la semilla ni realizó consultas Scalar para corroborarla. Esta evidencia acredita solo T036, no pacientes/edades visualizados, médicos consultados, documentos consultados o aceptación final.

### Procedimiento de carga conservado como referencia — no reejecutar ahora

1. Usar una terminal de desarrollo separada de la de pruebas. Confirmar esquema hospitalario vigente; si falta, detenerse: la semilla no aplica migraciones. Mantener la elección LOCAL/OCI intacta.
2. Suministrar `DATABASE_URL` de desarrollo de forma segura. En el contenedor activo ya la proporciona Compose: **no imprimirla ni transformarla manualmente**. El script admite `postgresql://` y, solo en development, `postgresql+asyncpg://`; normaliza el alias internamente sin cambiar el entorno. No reutilizar variables del sandbox ni divulgar credenciales.
3. Para el contenedor de desarrollo inspeccionado, abrir desde PowerShell una terminal interactiva (no reconstruir/reiniciar ni ejecutar `compose up`, cuyo arranque podría aplicar Alembic):

```powershell
docker exec -it -w /app mediflow-backend-dev /bin/sh
```

Dentro de `/bin/sh`, el procedimiento es ejecutar únicamente el módulo y consultar inmediatamente su código de salida (T036 ya reportada por el usuario; no repetir ahora ni ejecutar desde el agente):

```sh
python -m app.scripts.seed_hospital_data --target development
printf 'Código de salida: %s\n' "$?"
```

Fuera de Docker, desde `backend/` y con la URL explícita en el entorno, el comando del módulo es el mismo:

```powershell
python -m app.scripts.seed_hospital_data --target development
```

4. Revisar host/puerto/base saneados; en el contenedor inspeccionado, el destino debe ser **`postgres:5432/mediflow_dev`**. Escribir `mediflow_dev` para confirmar únicamente si corresponde al servidor autorizado; cancelar ante cualquier diferencia. El script verifica después el destino efectivo y el esquema mediante consultas de lectura, antes de pedir contraseñas o escribir.
5. Introducir las claves directamente en los prompts ocultos `Contraseña para M01:`–`M04:` que aparezcan; no se muestran caracteres ni asteriscos. No escribirlas en el chat, comandos, historial o archivos. Cada clave debe cumplir mínimo 12 caracteres, mayúscula, minúscula, número y símbolo. Se conservan solo en memoria del proceso, sin añadirlas al entorno. Si no se puede ocultar la entrada, EOF o Ctrl+C, se cancela sin iniciar la carga.

   - Las variables `BD04_PASSWORD_M01`–`BD04_PASSWORD_M04` siguen siendo válidas si ya están suministradas de forma segura; una clave configurada pero inválida se rechaza, no se reemplaza automáticamente.
   - Se piden solo claves ausentes para cuentas **nuevas**. Una cuenta propia compatible existente no pide clave y conserva hash/salt/estado; una segunda carga completa no solicita ninguna. Un conflicto de propiedad aborta sin apropiarse de cuentas ajenas.
   - No hace falta pegar un bloque Python auxiliar ni usar `read -s`, que no es portable en `/bin/sh`. El propio script gestiona `getpass`.

6. Resultado esperado: salida 0 con conjunto 10/4/5 y cantidades creadas/reutilizadas; sin contraseñas, episodios, archivos o cambios de configuración. En conflicto, salida no cero y rollback; no borrar el registro ajeno para forzar éxito. Conservar únicamente JSON/código de salida/destino saneado y fecha como evidencia; cerrar la terminal al terminar y retirar variables secretas si se introdujeron manualmente.
7. Solo después de una carga exitosa, abrir `http://localhost:8000/scalar` del backend que usa esa misma base. Obtener sesión real mediante autenticación existente y autorizar Bearer. No usar tokens `test-*-token` como credenciales reales. Las acciones de login pertenecen a la aplicación existente, no a una cuenta adicional de la semilla.

   - Para verificar los tres conjuntos con la misma sesión, usar una cuenta **ADMINISTRADOR existente** en `POST /api/v1/auth/login`, introduciendo su DNI y contraseña solo en Scalar. Exigir HTTP 200 y rol ADMINISTRADOR; conservar `access_token` únicamente de forma privada.
   - En cada GET, completar el header `authorization` con `Bearer <access_token>` en el editor de petición. El backend expone este header; no asumir que Scalar ofrecerá un botón global Authorize. Si lo ofrece, comprobar que realmente envía ese header.
   - Si no se dispone de credenciales ADMINISTRADOR, detener la verificación de médicos y comunicar el bloqueo; no crear administradores, elevar roles ni adivinar contraseñas. No adjuntar tokens/contraseñas ni respuestas de datos reales ajenos al registrar evidencias.

### Pacientes: GET /api/v1/patients

**T037 completada por conformidad del usuario.** Evidencia: captura adjunta en el chat de Scalar con `GET /api/v1/patients`, **200 OK** y `total: 10`, y JSON completo de diez pacientes ficticios. Extracto saneado del JSON aportado, conservando los campos necesarios para fechas/edad:

```json
{
  "total": 10,
  "items": [
    {"numero_documento":"99040001","fecha_nacimiento":"1990-10-08","edad":36},
    {"numero_documento":"99040002","fecha_nacimiento":"2000-02-29","edad":26},
    {"numero_documento":"99040003","fecha_nacimiento":"1975-01-15","edad":51},
    {"numero_documento":"99040004","fecha_nacimiento":"1985-03-20","edad":41},
    {"numero_documento":"99040005","fecha_nacimiento":"1960-07-12","edad":66},
    {"numero_documento":"99040006","fecha_nacimiento":"1995-12-05","edad":30},
    {"numero_documento":"99040007","fecha_nacimiento":"2010-06-18","edad":16},
    {"numero_documento":"99040008","fecha_nacimiento":"1980-09-25","edad":46},
    {"numero_documento":"99040009","fecha_nacimiento":"2005-04-30","edad":21},
    {"numero_documento":"99040010","fecha_nacimiento":"1955-11-02","edad":70}
  ]
}
```

- Cada DNI aparece una vez; las diez DOB coinciden con el manifiesto. Corroboración PostgreSQL anterior en conexión/transacción de **solo lectura**: tabla pacientes total 10, diez identidades una vez, 10/10 DOB correctas y 10/10 edades correctas.
- **Referencia real de edad**: sesión PostgreSQL `TimeZone = UTC`, `CURRENT_DATE = 2026-10-08`; consulta observada en `2026-10-08T04:23:01.109843+00:00`. En Lima aún era `2026-10-07`. El backend usa `EXTRACT(YEAR FROM age(CURRENT_DATE, fecha_nacimiento))::INT`, no la fecha del navegador o de carga. Con DOB `1990-10-08`, 36 es correcto para el día 8 y sería 35 para el día 7. El spec US1.6/FR-010 no prescribe Lima: esta comprobación cumple sin asumir otra zona y sin cambiar la lógica.
- Los campos `genero`, `sexo`, `numero_telefono`, `telefono` y `correo` son NULL en los diez registros aportados. Son opcionales en data-model §Pacientes y admiten NULL en el esquema activo; FR-002 contempla contactos cuando se incluyan. No se completaron ni se consideran un bloqueo de BD-04.
- `created_at = 2026-10-08T03:03:03.743444+00:00` del JSON corresponde al timestamp de registro/transacción (en Lima `2026-10-07 22:03:03.743444`), no a la hora exacta reconstruida del comando T036. La hora exacta de ejecución sigue sin anotarse. El agente no hizo una petición Scalar ni reejecutó la carga; la captura/JSON son evidencia del usuario y el SQL es corroboración separada.

Procedimiento de referencia, no nueva aceptación pendiente:

- Ejecutar el GET sin filtro `search`; exigir HTTP 200.
- En `items`, localizar por `numero_documento` exactamente los 10 pacientes del manifiesto, cada uno una vez.
- Para cada uno revisar `fecha_nacimiento` y `edad` y comparar con años completos a la fecha de consulta del backend, descontando uno si todavía no ocurrió el cumpleaños. No exigir `total == 10` si hay pacientes ajenos.
- Registrar evidencia visual sin datos reales/secretos ajenos. Este endpoint verifica pacientes y edades, **no** cuatro médicos ni cinco documentos. La ausencia de edad persistida se demuestra en pruebas/esquema, no solamente mirando una respuesta.

### Médicos: GET /api/v1/users

**T038 completada, incluida la parte de médicos.** El usuario reportó **HTTP 200** en Scalar para `GET /api/v1/users` con la cuenta ADMINISTRADOR existente de DNI `12345678` y aportó el array de respuesta. Incluye ocho usuarios: cuatro BD-04 y cuatro preexistentes ajenos. Cada médico del manifiesto aparece una vez, todos OPERADOR/ACTIVO y con sus especialidades correctas. Extracto saneado solo de BD-04; no se reproduce el resto del listado ni el header de autorización:

```json
[
  {"documento_identidad":"99041001","rol":"OPERADOR","especialidad_medica":"Medicina General","estado":"ACTIVO"},
  {"documento_identidad":"99041002","rol":"OPERADOR","especialidad_medica":"Cardiología","estado":"ACTIVO"},
  {"documento_identidad":"99041003","rol":"OPERADOR","especialidad_medica":"Neumonología","estado":"ACTIVO"},
  {"documento_identidad":"99041004","rol":"OPERADOR","especialidad_medica":"Traumatología","estado":"ACTIVO"}
]
```

Fuente: observación HTTP explícita y JSON aportados por el usuario, no una petición del agente. No se inventa fecha/hora de consulta ni se toma `created_at` como hora de aceptación. No se creó otra cuenta ni se cambiaron contraseñas/roles. La inspección previa del backend desplegado confirma `require_admin = require_roles("ADMINISTRADOR")`; M01 no está autorizado para este listado y su 403 no es una comprobación requerida para cerrar T038.

- La consulta PostgreSQL de solo lectura confirma una cuenta por DNI, todas OPERADOR/ACTIVO: `99041001` Medicina General, `99041002` Cardiología, `99041003` Neumonología, `99041004` Traumatología. No se leyeron contraseñas/hashes/salts/tokens, ni se crearon sesiones, cuentas o permisos desde el agente.
- Esta corroboración SQL no sustituye la aceptación Scalar: esta última ya fue obtenida por el usuario con ADMINISTRADOR, según el registro anterior.

Procedimiento conservado como referencia, ya verificado:

- Usar sesión de una cuenta ADMINISTRADOR existente, no elevar el rol de los médicos semilla.
- HTTP 200 con array de usuarios: localizar los cuatro DNI del manifiesto y verificar rol OPERADOR y exactamente Medicina General, Cardiología, Neumonología y Traumatología.
- No crear una cuenta administradora adicional ni restablecer credenciales existentes por comodidad de la demostración.

### Documentos: GET /api/v1/documents/{documento_id}

**Parte documental de T038 verificada por el usuario; T038 completa también acredita médicos.** La ruta desplegada usa `require_current_user` sin filtro adicional de rol: M01 está autorizado con una sesión Bearer válida. Fuente de aceptación: cinco cuerpos JSON aportados en el chat y confirmación posterior explícita de que **los cinco devolvieron HTTP 200 en Scalar**, con los IDs/prioridades compartidos. Se registran solo después de esa confirmación, sin inferir HTTP a partir del cuerpo ni atribuir a la consulta una fecha/hora no comunicada:

- BD04-DOC-001: **HTTP 200**, `clasificacion.nivel_prioridad = Urgente`.
- BD04-DOC-002: **HTTP 200**, `clasificacion.nivel_prioridad = Rutina`.
- BD04-DOC-003: **HTTP 200**, `clasificacion.nivel_prioridad = Ambiguo`.
- BD04-DOC-004: **HTTP 200**, `clasificacion.nivel_prioridad = Rutina`.
- BD04-DOC-005: **HTTP 200**, `clasificacion.nivel_prioridad = Urgente`.

Los IDs son distintos y cubren las tres prioridades existentes. La corroboración SQL previa confirma relaciones con P01–P05, status `recibido`, nodos_ejecutados=[] y destino_principal=NULL en los cinco, metadata BD-04/v1 y **cero entradas de esos documentos en cola_procesamiento**. `Cola_Rutina` en todos los cuerpos es el fallback del formateador de API (`row.get("destino_principal") or "Cola_Rutina"`, `documents.py:101`), **no un destino persistido ni un triaje/enrutamiento clínico ejecutado**. La semilla asigna recibido explícitamente y prepara registros sintéticos; estos valores no acreditan procesamiento por LangGraph, diagnósticos ni decisiones de auditoría. No se modificaron reglas clínicas, datos o configuración.

Pasos de referencia para esta parte de T038 con M01 — ya comprobada por el usuario; no repetir para cerrar la aceptación:

1. Reutilizar su sesión válida, si ya existe. En caso contrario, en Scalar ejecutar `POST /api/v1/auth/login` con DNI **99041001** y la contraseña que introdujo el usuario durante la carga. No compartirla en el chat. Exigir HTTP 200, DNI correcto y rol OPERADOR; conservar `access_token` únicamente de forma privada. El login es una acción manual de sesión de la aplicación, no una nueva carga.
2. En cada GET de documento, establecer el header `authorization` a `Bearer <access_token>` con el token de M01. No adjuntar el header/capturas del token al registrar evidencia.
3. Consultar los cinco identificadores por separado y reportar para cada uno HTTP, `documento_id` y `clasificacion.nivel_prioridad`. Se esperan respectivamente Urgente/Rutina/Ambiguo/Rutina/Urgente. Si aparece 401, renovar la sesión por el login existente; ante 403/404/otro fallo, detener y reportar el error saneado, sin modificar datos/permisos ni repetir la semilla.
4. No aceptar T038 solo por documentos o SQL de médicos: también requiere `/users` con ADMINISTRADOR. Ambas partes ya están acreditadas arriba; limpieza de secretos confirmada y aceptación final T039 recibida del usuario.

- Consultar por separado BD04-DOC-001, BD04-DOC-002, BD04-DOC-003, BD04-DOC-004 y BD04-DOC-005.
- Cinco HTTP 200, IDs correctos/distintos y cobertura de Urgente/Rutina/Ambiguo en `clasificacion.nivel_prioridad`.
- Son registros ficticios consultables; no exigir visor, PDF, imagen o descarga física. El listado `/documents` puede estar limitado y su total no cuenta toda la tabla.
- Colores solo presentación existente: rojo, verde y amarillo/ámbar, respectivamente; Ambiguo es incertidumbre, no gravedad intermedia.

## Cierre — T039 completada; BD-04 aceptada

Las pruebas PostgreSQL aisladas (incluida reejecución) y gates backend/frontend/SQL offline están obtenidos; T036–T038 están acreditadas por el usuario, incluidas las tres consultas separadas de Scalar. La cobertura FR-001–013/SC-001–008 está revisada en [tasks.md](tasks.md), usando esas evidencias previas, sin nueva ejecución de pruebas o semilla. Los resultados iniciales de documentos no acreditan triaje ejecutado. No faltan resultados Scalar para T038.

**Confirmación de cierre de sesiones recibida:** el usuario comunica que cerró las cuatro sesiones usadas durante la verificación, **dos de M01 y dos del ADMINISTRADOR**. Se registra únicamente ese reporte, sin tokens ni credenciales. No se infieren HTTP, mensajes de logout, método de cierre o fecha/hora; el agente no realizó consultas ni escrituras de sesiones para corroborarlo.

**Confirmación de limpieza recibida:** el usuario comunica que completó la limpieza de secretos locales solicitada (Scalar, portapapeles y terminales/historial que los contengan). Se registra únicamente su confirmación, sin secretos ni fecha/hora inferida; el agente no verificó ni efectuó esa limpieza. Limpiar copias locales no elimina el contenido ya compartido en el chat. El cierre del sandbox propio y la retirada de sus credenciales temporales ya tienen evidencia registrada. Esta confirmación de limpieza no equivale a aceptación final de BD-04.

**Aceptación final recibida:** después de confirmar la limpieza, el usuario respondió **«si acepto»** a la pregunta explícita de aceptación final de BD-04. Esta respuesta, separada de la confirmación de limpieza, completa T039. **BD-04 queda completada y aceptada** con pruebas, cobertura, carga y verificaciones Scalar documentadas; no se infiere una fecha/hora de aceptación ni se reproducen secretos. No quedan pendientes de esta tarea. No repetir la semilla, crear cuentas o elevar permisos. Sin commit, push o PR.

### Evidencia del ajuste de CLI (no aceptación manual)

- Spec aprobado compatible con entrada segura interactiva y URL Docker; no se cambiaron sus requisitos ni el esquema/API/frontend.
- Suite final **229 pruebas**, incluyendo **90 BD-04**, en PostgreSQL 17 aislado; primera carga 10/4/5, segunda sin prompts ni duplicados con snapshots completos intactos, conjunto parcial y preservación de credenciales. Ruff, mypy y SQL Alembic offline pasan. Gates frontend repetidos como se registra arriba.
- Terminal Linux real del contenedor con conexión/loader simulados: cuatro prompts con eco desactivado, ninguna clave en la salida, **sin conexión o carga real de desarrollo**. El modo test no pide contraseñas; sus pruebas conservan variables de entorno/secretos efímeros.
- Al finalizar el ajuste de CLI todavía no se había ejecutado la carga real en `mediflow_dev`, Scalar o migraciones de desarrollo ni reconstruido contenedores. Ese estado es histórico: el usuario acreditó posteriormente T036–T038 y confirmó cierre de sesiones/limpieza y aceptación final T039, registrados arriba. El estado vigente es BD-04 completada y aceptada, sin repetir la carga.
