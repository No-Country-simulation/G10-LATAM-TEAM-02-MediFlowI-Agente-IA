# Historial de cambios — 2026-09-26 (CAMBIO1)

> Actualización del 27/09: el pendiente de Alembic descrito en este registro histórico fue resuelto en Docker. Véase [la verificación posterior](HISTORIAL_CAMBIOS_2026-09-27_CAMBIO1.md).

**Autor:** Krystopher  
**Historia:** US-01 — Contrato OpenAPI 3.1 y generación de tipos (SDD)  
**Sprint:** Sprint 1, semana del 21 al 27 de septiembre de 2026  
**Estado:** contrato y generación verificados; sincronización de la base real pendiente de configurar DATABASE_URL.

## Resultado

El contrato modular OpenAPI 3.1 produce modelos Pydantic v2 y tipos TypeScript mediante herramientas de generación. Se eliminó el éxito aparente basado en conservar archivos existentes. Los errores de herramientas o del contrato terminan el comando con código distinto de cero.

## Contrato y herramientas

- `specs/openapi.yaml` conserva `/triage`, `/triage/upload`, `/documents` y `/health`, además de las rutas que ya existían.
- Los schemas usan nulabilidad de JSON Schema 2020-12, campos obligatorios y enums coherentes. `PrioridadTriaje` se reutiliza mediante referencias.
- `canal_origen` es opcional con default vacío para preservar el comportamiento de la API; no admite null.
- El enum de tipo de documento conserva el catálogo y declara los valores de compatibilidad existentes: `Desconocido`, `Error` y `Documento Clínico`. Se rechaza texto arbitrario como `FACTURA`.
- `ErrorResponse` representa el envoltorio `detail` real. Los errores 422 tienen un schema específico. No se modificaron los handlers productivos.
- `EntidadesMedicas` permanece independiente, sin añadir nuevas capacidades al agente. Su uso futuro se documenta; Spectral mantiene visible la advertencia de componente sin uso.
- Las referencias se reúnen con Redocly en un JSON temporal. Sobre ese mismo contrato se ejecutan Spectral, datamodel-code-generator y openapi-typescript. Esto resuelve los fallos reproducidos de referencias externas en las herramientas utilizadas.
- `package.json` y `package-lock.json` fijan las herramientas Node. El extra `sdd` de `backend/pyproject.toml` declara versiones de generación Python.
- `make generate-check` detecta salidas desactualizadas sin modificarlas. La salida no incluye timestamps ni rutas temporales y se normaliza a LF para Windows/Unix.
- Las salidas se preparan y comprueban antes de publicarlas; un fallo de generación conserva las anteriores y reporta error.

## Backend y frontend

- `models.py` se genera desde el contrato. El endpoint de triaje importa `DocumentoClinico` como `DocumentoClinicoRequest`, eliminando esa duplicación sin cambiar su comportamiento de entrada.
- `AgentState` permanece en `app.agent.state`; no se altera la orquestación LangGraph.
- `types.ts` incluye tipos de schemas y operaciones HTTP. `index.ts` expone alias generados de los schemas.
- `triage.api.ts` conserva las funciones HTTP e importa los tipos generados. Se eliminaron redefiniciones que ocultaban campos anulables en la adaptación de documentos.
- `probando_modelos.py` serializa `EntidadesMedicas` por separado y comprueba el round-trip; ya no pasa un campo inexistente a `DatosExtraidos`.

## Pruebas y protección de datos

- Pytest fuerza DATABASE_URL vacío y usa almacenamiento temporal, evitando conexiones a mediflow_dev y mezcla de archivos sintéticos con documentos locales.
- La prueba pública de salud verifica 503 sin PostgreSQL; las pruebas existentes siguen verificando 200 cuando la dependencia está disponible mediante un doble de prueba.
- Las pruebas de Alembic proporcionan una URL ficticia exclusivamente para `upgrade head --sql`. No conectan a una base real.
- Se añadieron pruebas de respuestas HTTP contra JSON Schema, nulabilidad, enums, generación desde cero, propagación de un cambio a Python/TypeScript, repetibilidad, fallo por herramienta ausente, fallos de generadores y reglas Spectral.

## Verificación ejecutada

- `make validate`: código 0; **0 errores y 1 advertencia**, correspondiente a `EntidadesMedicas` reservado.
- `make generate`: código 0; generación real de las cuatro salidas.
- `make generate-check`: código 0; las salidas versionadas coinciden con una nueva generación.
- `python -m pytest tests/ -q --tb=short` desde backend: **92 pruebas pasando**, 71.14 segundos.
- `npm run build` desde frontend: código 0; 78 módulos y sin errores TypeScript.
- `python backend/probando_modelos.py`: código 0; ejemplo y serialización correctos.
- Ruff sobre los scripts y archivos Python manuales modificados: sin errores.
- `git diff --check`: sin errores de whitespace.
- `alembic upgrade head` contra la configuración real: **no completado**. `backend/.env` no tiene DATABASE_URL; Alembic intenta usar el dialecto de ejemplo `driver` de su configuración. No se modificó `.env` ni se aplicaron migraciones a mediflow_dev.

La generación SQL offline pasó en pytest. Eso no demuestra sincronización de la base real; esta comprobación sigue pendiente. No se agregaron migraciones ni se cambió el modo LOCAL/OCI.

## Uso para el colaborador

Consulta [GUIA_SDD_US01.md](../GUIA_SDD_US01.md). El flujo es editar el contrato, validar, generar, probar y revisar el diff. No editar manualmente los archivos `_generated/`.

No se realizó commit, push ni PR.
