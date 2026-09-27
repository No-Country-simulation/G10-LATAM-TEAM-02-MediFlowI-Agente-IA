# Historial de Cambios — 2026-09-26 (CAMBIO2)

> Actualización del 27/09: el pendiente de Alembic descrito en este registro histórico fue resuelto en Docker. Véase [la verificación posterior](HISTORIAL_CAMBIOS_2026-09-27_CAMBIO1.md).

**Fecha**: 26/09/2026 (fecha obtenida del sistema)  
**Identificador de Cambio**: CAMBIO2  
**Autor**: Krystopher  
**Sprint / Fase**: Sprint 1 — US-01, contrato OpenAPI 3.1 y generación de tipos (SDD)  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  
**Base de revisión**: commit `760af40`, rama `dev-krystopher`  
**Estado**: criterios de aceptación de US-01 verificados; verificación de Alembic contra la base real pendiente.

## Resumen Ejecutivo

Se registra la segunda revisión de los cambios acumulados desde el último commit y se prepara la documentación del PR hacia `develop`. La implementación y sus decisiones técnicas se detallan en [CAMBIO1](HISTORIAL_CAMBIOS_2026-09-26_CAMBIO1.md). Este registro incorpora los resultados de la revisión posterior y distingue el cumplimiento de US-01 del requisito adicional de comprobar las migraciones en PostgreSQL real.

No se añadieron nuevas funcionalidades durante esta actualización documental. Los ejemplos explicativos de un endpoint de clasificación y del campo `observacion` no se implementaron en el repositorio.

## Detalle de Cambios por Capa Técnica

### 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)

- US-01 no introduce tablas, columnas ni migraciones nuevas. PostgreSQL mantiene su función de fuente de verdad de los datos persistidos.
- Las pruebas de migraciones generan SQL mediante `alembic upgrade head --sql` con una URL ficticia, sin conectarse a `mediflow_dev`.
- La revisión confirmó que `DATABASE_URL` sigue sin estar configurada. El intento previo de `alembic upgrade head` no pudo completarse por el dialecto de ejemplo de Alembic. La sincronización de la base real queda pendiente y no se marca como aprobada.
- No se modificó la configuración LOCAL/OCI ni el archivo `.env`.

### 2. Backend & Agente IA (FastAPI / LangGraph / Python)

- Se verificó que `backend/app/_generated/models.py` procede del contrato y que `/triage` importa el modelo generado `DocumentoClinico` con el alias `DocumentoClinicoRequest`.
- Los modelos validan campos obligatorios, prioridades, tipos de documento y límites de confianza. Los errores HTTP y la nulabilidad se describen en el contrato.
- Las pruebas comparan respuestas de la aplicación con JSON Schema y Pydantic utilizando dependencias simuladas. Esto no equivale a validar todas las salidas de producción mediante `response_model`; esa integración no se incorporó a `/triage`.
- La orquestación LangGraph permanece sin cambios. `EntidadesMedicas` se genera como modelo independiente, pero todavía no forma parte de las respuestas del agente.

### 3. Frontend & UX (React / Vite / TypeScript)

- Se verificó la generación de `frontend/src/_generated/api/types.ts` e `index.ts` y su consumo desde `triage.api.ts`.
- El adaptador de documentos utiliza los tipos compatibles con los campos anulables del contrato. No se modificaron pantallas ni estilos.
- TypeScript comprueba el código durante la compilación; los tipos generados no validan por sí solos el JSON recibido en ejecución.

### 4. Infraestructura, Scripts & Documentación

- Se repitieron `make validate`, `make generate` y `make generate-check`. La generación produjo las mismas cuatro salidas, sin archivos desactualizados.
- La suite comprueba generación desde cero, propagación de cambios del contrato a ambos lenguajes, reproducibilidad y fallos que deben conservar las salidas anteriores y devolver error.
- Se conserva la advertencia de Spectral por `EntidadesMedicas` sin uso; no se deshabilita la regla para ocultarla.
- Se crea este registro incremental y [el documento PR1](../pull_requests/PULL_REQUEST_2026-09-26_PR1.md), vinculados a sus índices maestros. El PR documental resume la implementación completa acumulada, no solo esta actualización de documentación.

## Verificación y Pruebas

Resultados de la revisión más reciente del código, realizada antes de esta actualización exclusivamente documental:

- **Contrato**: OpenAPI `3.1.0`, endpoints `/triage`, `/documents` y `/health`, además de las rutas existentes.
- **Schemas de US-01**: `DocumentoClinico`, `ResultadoTriaje`, `EntidadesMedicas` y `PrioridadTriaje` definidos y generados.
- **Spectral (`make validate`)**: código 0; **0 errores y 1 advertencia** por el componente reservado `EntidadesMedicas`.
- **Generación (`make generate`)**: código 0; **4 archivos de salida, 0 actualizados** en la repetición.
- **Consistencia (`make generate-check`)**: código 0; coincidencia con las salidas guardadas.
- **Backend (`python -m pytest -q`, desde `backend`)**: **92 pruebas aprobadas en 79.54 segundos**; base y almacenamiento del usuario aislados.
- **Frontend (`npm run build`, desde `frontend`)**: código 0; **78 módulos**, sin errores TypeScript; Vite completó el build en **955 ms**.
- **Diff (`git diff --check`)**: sin errores de whitespace.
- **Migraciones reales (`alembic upgrade head`)**: **pendiente** de configurar `DATABASE_URL` y comprobar la base destino. La generación SQL offline no sustituye esta comprobación.

Los criterios específicos de US-01 están verificados en el entorno local. Para dar por cumplida toda la Regla de Oro del repositorio falta la comprobación de Alembic contra PostgreSQL real.

## Entrega

- Guía para colaboradores: [GUIA_SDD_US01.md](../GUIA_SDD_US01.md).
- Documento para el PR: [PULL_REQUEST_2026-09-26_PR1.md](../pull_requests/PULL_REQUEST_2026-09-26_PR1.md).
- Rama de origen: `dev-krystopher`; destino: `develop`; estrategia prevista: **Squash and merge**.
- Se preparó documentación local. No se realizó commit, push, publicación de PR en GitHub ni merge.
