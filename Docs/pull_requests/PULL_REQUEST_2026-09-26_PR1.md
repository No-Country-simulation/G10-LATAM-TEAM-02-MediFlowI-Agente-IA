# Pull Request — 2026-09-26 (PR1)

## feat(US-01): definición de contrato openapi 3.1 y generación de tipos sdd

### Datos del Pull Request

- **Título del PR**: `feat(US-01): definición de contrato openapi 3.1 y generación de tipos sdd`
- **Identificador documental**: PR1 del día 2026-09-26; no corresponde a un número de PR de GitHub.
- **Fecha**: 2026-09-26 (obtenida del sistema).
- **Autor**: Krystopher.
- **Rama de origen**: `dev-krystopher`.
- **Rama de destino**: `develop`.
- **Estrategia de merge**: Squash and merge.
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal.
- **Base de revisión local**: `760af40`.
- **Historial asociado de revisión**: [HISTORIAL_CAMBIOS_2026-09-26_CAMBIO2.md](../historial_cambios/HISTORIAL_CAMBIOS_2026-09-26_CAMBIO2.md).
- **Historial de implementación**: [HISTORIAL_CAMBIOS_2026-09-26_CAMBIO1.md](../historial_cambios/HISTORIAL_CAMBIOS_2026-09-26_CAMBIO1.md).
- **Verificación Docker posterior**: [HISTORIAL_CAMBIOS_2026-09-27_CAMBIO1.md](../historial_cambios/HISTORIAL_CAMBIOS_2026-09-27_CAMBIO1.md).
- **Corrección final de compatibilidad US-01**: [HISTORIAL_CAMBIOS_2026-09-27_CAMBIO2.md](../historial_cambios/HISTORIAL_CAMBIOS_2026-09-27_CAMBIO2.md).
- **Estado actualizado al 27/09**: documento local preparado para revisión; publicación en GitHub pendiente. Alembic verificado contra PostgreSQL real en Docker, revisión `n7o707411jk3 (head)`.

### Resumen del PR

El contrato pasa a OpenAPI 3.1.0 y se convierte en la fuente común para generar modelos Pydantic v2 y tipos TypeScript. `make generate` valida el contrato, ejecuta ambos generadores y actualiza las salidas únicamente después de que la generación y sus comprobaciones terminen correctamente. Los fallos de herramientas devuelven error en lugar de presentar archivos anteriores como una generación exitosa.

El backend utiliza el modelo generado de entrada en `/triage` y el frontend importa los tipos generados para sus funciones HTTP. Las pruebas verifican generación desde cero, reproducibilidad, propagación de cambios a ambos lenguajes y conformidad de respuestas representativas con el contrato.

Las respuestas de `/documents` normalizan nombres históricos al catálogo del contrato: por ejemplo, `Analítica de Laboratorio` se entrega como `Informe de Laboratorio`. Se reutiliza el normalizador existente, sin modificar los valores almacenados. Las pruebas cubren listas con contenido y consulta por ID, tanto para filas PostgreSQL como para documentos previamente estructurados.

### Cambios Detallados por Capa Técnica

#### Base de Datos & Migraciones

- No se añaden migraciones ni se modifica el esquema persistido.
- PostgreSQL mantiene su función de fuente de verdad y la selección LOCAL/OCI sigue siendo manual.
- Pytest aísla la base y los archivos locales. Las pruebas de Alembic generan SQL offline; no certifican el estado de `mediflow_dev`.

#### Backend & Agente IA

- Modelos Pydantic generados desde los schemas clínicos y de respuestas HTTP.
- `/triage` importa `DocumentoClinico` en lugar de mantener una definición duplicada de entrada.
- `canal_origen` conserva su comportamiento opcional con valor vacío y rechaza `null`.
- El catálogo de documentos incluye los valores de compatibilidad que ya devuelve la aplicación, manteniendo el rechazo de texto arbitrario.
- El adaptador de `/documents` normaliza tipos históricos y conserva `Desconocido`, `Error` y `Documento Clínico`. La adaptación trabaja sobre copias y no modifica los registros originales ni requiere una migración.
- El contrato documenta el envoltorio `detail` de FastAPI y un schema específico para errores 422.
- El ejemplo de modelos utiliza campos existentes y serializa `EntidadesMedicas` por separado.
- Se preservan los cinco nodos LangGraph y el estado interno `AgentState`.

#### Frontend & UX

- Generación de schemas y tipos de operaciones HTTP con `openapi-typescript`.
- Alias de importación generados en `index.ts` y consumo de esos tipos en `triage.api.ts`.
- Ajuste del adaptador de documentos para conservar la nulabilidad del contrato.
- Sin cambios de pantallas ni de estilos.

#### Infraestructura & Documentación

- Contrato modular OpenAPI 3.1.0 con nulabilidad compatible, respuestas tipadas y los cuatro schemas requeridos por US-01.
- Bundle temporal con Redocly para procesar las referencias externas de forma compatible con las herramientas utilizadas.
- Spectral con reglas para operaciones, seguridad, identificadores, confianza y nulabilidad.
- Herramientas Node fijadas en `package.json` y `package-lock.json`; herramientas Python declaradas en el extra `sdd`.
- `make validate`, `make generate` y `make generate-check` con códigos de salida que reflejan los fallos.
- Salidas sin timestamps y con saltos de línea LF para mantener la comparación reproducible en Windows y Unix.
- Guía de uso SDD e historiales vinculados a sus índices.

### Archivos Modificados / Creados

Las rutas se expresan respecto de la raíz del repositorio. El detalle de implementación está en el historial asociado y en el diff del PR.

| Tipo de cambio | Archivos | Función |
| :--- | :--- | :--- |
| Modificados | `specs/openapi.yaml`, `specs/components/schemas.yaml`, `specs/components/responses.yaml` | Contrato central, schemas y respuestas compartidas. |
| Modificados | `specs/paths/{triage,documents,health,auth,patients,settings,users}.yaml` | Rutas, referencias y respuestas HTTP tipadas. |
| Modificados | `.spectral.yaml`, `Makefile`, `.gitignore`, `backend/pyproject.toml` | Reglas, comandos y dependencias del proceso SDD. |
| Nuevos | `.gitattributes`, `package.json`, `package-lock.json` | Reproducibilidad de las salidas y de las herramientas Node. |
| Modificados | `infrastructure/scripts/generate.py`, `infrastructure/scripts/validate_spec.py` | Generación y validación con fallo explícito. |
| Nuevos | `infrastructure/scripts/bundle_spec.mjs`, `infrastructure/scripts/sdd.py` | Resolución de referencias y ejecución compartida de herramientas. |
| Modificados | `backend/app/_generated/models.py`, `backend/app/_generated/README.md`, `backend/app/api/v1/triage.py` | Modelos e integración del endpoint. |
| Modificado | `backend/app/api/v1/documents.py` | Compatibilidad de respuestas históricas con el catálogo del contrato. |
| Nuevos | `backend/app/_generated/__init__.py`, `backend/probando_modelos.py` | Paquete generado y ejemplo ejecutable. |
| Modificados | `frontend/src/_generated/api/types.ts`, `frontend/src/api/triage.api.ts`, `frontend/src/api/documentsApi.ts` | Tipos e integración del frontend. |
| Nuevo | `frontend/src/_generated/api/index.ts` | Exportaciones de tipos. |
| Modificados | `backend/tests/conftest.py`, `backend/tests/test_health.py`, `backend/tests/test_migrations.py` | Aislamiento y verificaciones independientes de la base real. |
| Nuevos | `backend/tests/test_generated_models.py`, `backend/tests/test_openapi_contract.py`, `backend/tests/test_sdd_pipeline.py` | Validación de modelos, respuestas y generación. |
| Nuevos | `Docs/GUIA_SDD_US01.md`, `Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-26_CAMBIO1.md`, `Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-26_CAMBIO2.md`, este documento | Guía, implementación, revisión y propuesta de PR. |
| Nuevos | `Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-27_CAMBIO1.md`, `Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-27_CAMBIO2.md` | Verificación Docker y cierre de compatibilidad US-01. |
| Modificados | `Docs/HISTORIAL_CAMBIOS.md`, `Docs/PULL_REQUEST.md` | Índices maestros. |

### Criterios de Aceptación de US-01

- [x] `specs/openapi.yaml` declara OpenAPI 3.1.0 y conserva `/triage`, `/documents` y `/health`.
- [x] `make validate` termina con 0 errores Spectral.
- [x] `make generate` produce Pydantic en `backend/app/_generated/` y TypeScript en `frontend/src/_generated/`.
- [x] Se modelan `DocumentoClinico`, `ResultadoTriaje`, `EntidadesMedicas` y `PrioridadTriaje`.
- [x] Una generación repetida coincide con los archivos guardados.

### Checklist de la Regla de Oro

- [x] **Arquitectura de persistencia**: PostgreSQL permanece como fuente de verdad; conexión real verificada mediante el endpoint de salud en Docker el 27/09.
- [x] **Control manual de almacenamiento**: selección LOCAL/OCI preservada.
- [x] **Pruebas backend**: 108 aprobadas, con base y almacenamiento del usuario aislados.
- [x] **Compilación frontend**: build sin errores TypeScript.
- [x] **Migraciones Alembic sincronizadas**: el arranque Docker ejecutó `alembic upgrade head`; `current`, `heads` y `alembic_version` coinciden en `n7o707411jk3` en la base local del contenedor.

### Verificación y Pruebas

Resultados del 27/09 después de corregir las respuestas de documentos históricos:

1. `make validate`: **0 errores, 1 advertencia** por `EntidadesMedicas` sin uso.
2. `make generate`: código 0; **4 salidas, 0 actualizadas** al repetir la generación.
3. `make generate-check`: código 0; salidas consistentes.
4. `python -m pytest -q`, desde `backend`: **108 passed in 93.88s**. Los 16 casos nuevos cubren lista y detalle con nombres históricos, tipos canónicos, tipo desconocido, tipo ausente y los tres valores especiales. Antes de la corrección, 7 de estos casos reproducían el fallo.
5. `npm run build`, dentro del contenedor frontend: código 0; **78 módulos**; Vite completó el build en **2.28 s**, sin errores TypeScript.
6. `git diff --check`: sin errores de whitespace.
7. `alembic upgrade head`, `alembic current` y `alembic heads`, dentro del backend: código 0, revisión `n7o707411jk3 (head)`.
8. Lectura de los registros reales mediante una conexión PostgreSQL con `default_transaction_read_only=on`: **3/3 documentos** validados con `ResultadoTriaje` tras aplicar el adaptador público. El modo de almacenamiento sigue siendo `LOCAL`.

Verificación adicional del 27/09 en Docker: construcción y arranque completos con código 0; frontend, backend y PostgreSQL activos; frontend, `/health` y `/docs` devuelven HTTP 200; PostgreSQL disponible y Alembic en head. `modo_almacenamiento` conserva `LOCAL`. El endpoint de salud indica que el proveedor LLM no está configurado; no se verificaron llamadas reales a IA ni a OCI.

Para preparar otro entorno, seguir [GUIA_SDD_US01.md](../GUIA_SDD_US01.md): instalar los extras Python `dev,sdd` y ejecutar `npm ci` en la raíz para las herramientas del contrato. Las dependencias del frontend se instalan en su propia carpeta. Usar el entorno virtual del proyecto y Node disponible en PATH o mediante `NODE_BINARY`.

### Límites y Pendientes para la Revisión

- `EntidadesMedicas` está modelado y se genera, pero todavía no integra las respuestas del agente. La advertencia de Spectral permanece visible.
- `/triage` utiliza el modelo generado de entrada. Sus respuestas representativas se verifican en pruebas; no se añadió un `response_model` generado al endpoint.
- El YAML define la comunicación HTTP. No genera lógica clínica, rutas FastAPI, tablas de base de datos ni validación de JSON en ejecución dentro del navegador.
- La comprobación real de Alembic se completó el 27/09 dentro de Docker, donde Compose proporciona `DATABASE_URL`. El intento previo desde Windows y las pruebas SQL offline quedan documentados como verificaciones distintas.
- Los resultados descritos corresponden al entorno local. No acreditan una ejecución de CI ni un despliegue.
- US-01 cubre contrato y generación de tipos. La demostración completa del PDF con IA real, OCI y extracción de medicamentos/dosis corresponde a integración funcional posterior; no se incorpora a este PR ni se acredita con estas pruebas.
