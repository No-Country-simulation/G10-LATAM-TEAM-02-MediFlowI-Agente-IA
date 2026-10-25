# Issue #84 — Códigos de respuesta OpenAPI

## Alcance SDD

`specs/openapi.yaml` y sus referencias son el contrato existente y no se
modifican. El cambio sólo alinea los códigos documentados por FastAPI:
declaraciones `responses` en routers, modelos generados compartidos y eliminación
puntual del `422` implícito. No cambia validación, autenticación, persistencia,
almacenamiento ni decisiones clínicas. No se reemplaza el esquema runtime por YAML.

## Comparación previa a la implementación

Se resolvió el contrato mediante `infrastructure/scripts/sdd.py:bundle_spec` y
se comparó por método y ruta con `GET /openapi.json`, sin invocar operaciones de
negocio. Las 28 operaciones presentaban diferencias:

- `POST /triage` y `/triage/upload`: faltaban `207`, `400`, `401`, `500`, `503`;
  en upload faltaban también `413`, `415`.
- `GET /health`: faltaba `503`, también en su alias sin prefijo.
- Documentos: faltaban respuestas de autenticación, autorización,
  indisponibilidad, recurso ausente y conflictos según la operación.
- Auth, users, patients, settings, metrics y coordination: faltaban los errores
  correspondientes declarados en el contrato.
- Sobraba el `422` automático en 20 operaciones: alerts/stream, metrics, las
  cuatro operaciones de auth, las tres de users, las siete de patients, las dos
  de settings y los GET pending/audit de coordination. Los `422` previstos en
  triage, documents y POST coordination/resolve se conservan explícitamente.

## Rutas y excepciones

- Los servidores SDD ya terminan en `/api/v1`; cada ruta relativa se compara con
  `/api/v1` + ruta, conservando método y nombres de parámetros.
- El alias adicional `GET /health` se verifica con los mismos códigos que
  `GET /api/v1/health`; no se elimina ni se oculta.
- No se exige igualdad inversa a operaciones exclusivas del runtime y no cubiertas
  por el contrato: `GET /api/v1/documents/{documento_id}/file`,
  `GET|POST /api/v1/episodes/`, `GET /api/v1/episodes/{episode_id}` y
  `PATCH /api/v1/users/{user_id}`. Conservan su documentación automática.

## Diferencias funcionales fuera de alcance

### Limitación separada: respuestas 422 reales no documentadas

El contrato no enumera todos los errores realmente posibles. Por ejemplo, login
devuelve `422` explícitamente para identificadores inválidos y FastAPI mantiene
su validación de entrada aunque un contrato no declare `422`. Por tanto, algunos
endpoints pueden seguir devolviendo `422` aunque ese código se haya retirado del
esquema runtime para igualar el contrato SDD. La igualdad comprobada es documental,
no garantiza que estén enumerados todos los códigos HTTP realmente posibles.
Esta limitación es independiente del entorno Node y del resultado de Vitest.

También existen errores de autenticación o internos no enumerados en algunas
operaciones de users/patients. No se remapean esos códigos ni se modifican reglas
funcionales para forzar la coincidencia documental. Corregir ese comportamiento
o ampliar el contrato requiere una decisión SDD separada.

## Verificación

- La prueba nueva usa el contrato resuelto con `bundle_spec` y exige igualdad de
  conjuntos en **todas** sus operaciones, sin ignorar `422`. Acumula diagnósticos
  con método, ruta, códigos faltantes y sobrantes, incluso si falta una operación.
- Evidencia red: falló antes del arreglo en las 28 operaciones y el alias health.
- Evidencia green: la misma prueba pasa después del arreglo.
- Regresiones adicionales verifican que la política sólo retire `422` implícitos,
  preserve caché y demás metadatos de FastAPI, y mantenga modelos útiles en las
  respuestas de éxito, auditoría y error de ambos endpoints de triaje.
- El cliente sólo consulta el esquema; `conftest.py` fuerza `DATABASE_URL=""`,
  proveedor LLM simulado y persistencia simulada. No requiere PostgreSQL, Gemini
  ni OCI.

### Resultados locales

- `backend/.venv/Scripts/python.exe -m pytest tests/test_openapi_contract.py -q`:
  **53 passed**.
- `backend/.venv/Scripts/python.exe -m pytest -q -ra`: **508 passed, 102 skipped,
  1 warning**. Los skips son integraciones que requieren sandboxes PostgreSQL
  registrados y activados explícitamente; no acreditan integración real. El aviso
  existente es `HTTP_422_UNPROCESSABLE_ENTITY` deprecado en el handler de login;
  no se modifica lógica ajena al alcance. La primera ejecución agotó el límite
  de 120 s; la repetición terminó en 121,32 s sin fallos.
- `alembic upgrade head --sql`: **exit 0**, 42.733 bytes de SQL, usando una URL
  sintética `mediflow_test` y sin conectarse a ninguna base de datos.
- Antecedente con Node **22.12.0**: `vitest run` y `npm run build` inicialmente bloqueados
  por `module is not defined` en el `tailwind.config.js` CommonJS existente dentro
  del paquete ESM. No se modifica ningún archivo frontend.
- Con `NODE_OPTIONS=--no-experimental-require-module` sólo en el proceso:
  `npm run build` **pasó**, incluido TypeScript; `vitest run` **permaneció bloqueado**
  con 23 errores de workers y ninguna prueba ejecutada, por `ERR_REQUIRE_ESM`
  entre `html-encoding-sniffer` y `@exodus/bytes` al cargar jsdom.
- Repetición con Node **24.22.1**, un solo ejecutor y sin paralelismo de archivos:
  **23 archivos y 130 pruebas aprobadas**, exit 0, en 78,11 s. Se emitieron avisos
  de React sobre actualizaciones sin `act(...)` en StorageSettingsView y Dashboard,
  sin fallos de pruebas. Desde `frontend/`, en PowerShell:

  ```powershell
  $env:PATH = 'C:\Users\USUARIO\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin;' + $env:PATH
  & 'C:\Users\USUARIO\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd' run test --pool=threads --maxWorkers=1 --no-file-parallelism --reporter=dot
  ```

  No se modificaron frontend, dependencias, comportamiento de endpoints ni contrato
  SDD para esta repetición; sólo se actualizó este informe.
- `git diff --check`: sin errores de whitespace. La revisión Ruff adicional
  detecta tres hallazgos preexistentes en imports de documents/tests y el helper
  de métricas; se dejan intactos para evitar cambios fuera de alcance.

La sincronización y sus pruebas están en verde. **El bloqueo de Vitest queda
resuelto usando Node 24.22.1 y la ejecución indicada**, conservando el fallo con
Node 22 como antecedente. Backend, build y SQL offline conservan los resultados
previamente registrados; no se repitieron en este paso documental. Las 102 pruebas
de integración omitidas y los avisos registrados impiden afirmar una validación
global al 100 % sin salvedades. Acreditar PostgreSQL real requiere habilitar los
sandboxes aislados; la limitación de los `422` reales continúa separadamente.
