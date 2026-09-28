# Historial de Cambios — 2026-09-27 (CAMBIO2)

**Fecha**: 27/09/2026 (obtenida del sistema).  
**Identificador de Cambio**: CAMBIO2.  
**Autor**: Krystopher.  
**Sprint / Fase**: Sprint 1 — US-01, revisión final del contrato.  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal.

## Resumen ejecutivo

La revisión final detectó que dos documentos iniciales producían respuestas incompatibles con el enum de `ResultadoTriaje`. Se corrige la adaptación de salida de `/documents` y se amplía la verificación a listas con contenido y consultas por ID. El cambio completa la compatibilidad del contrato de US-01 sin introducir funcionalidades clínicas nuevas.

PR documental asociado: [PULL_REQUEST_2026-09-26_PR1.md](../pull_requests/PULL_REQUEST_2026-09-26_PR1.md). Se actualiza ese PR1 existente; no se crea ni publica un PR en GitHub.

## Detalle de cambios por capa técnica

### 1. Base de Datos & Migraciones

- No se modifica el esquema ni se crean migraciones o actualizan datos históricos.
- Los valores originales permanecen en PostgreSQL; la normalización ocurre al construir la respuesta HTTP.
- La comprobación de los tres documentos reales utiliza una conexión de solo lectura. El modo de almacenamiento conserva `LOCAL`.
- `alembic upgrade head` termina correctamente sin migraciones pendientes; `current` y `heads` coinciden en `n7o707411jk3`.

### 2. Backend & Agente IA

- `backend/app/api/v1/documents.py`: reutiliza `normalizar_tipo_documento` del catálogo clínico existente.
- `Analítica de Laboratorio` se entrega como `Informe de Laboratorio`; `Informe de Estudio por Imagenes` se entrega como `Informe de Estudio por Imágenes`.
- Conserva los valores de compatibilidad del contrato: `Desconocido`, `Error` y `Documento Clínico`. Los tipos no reconocidos usan `Otro`; un tipo ausente conserva el valor de respaldo `Documento Clínico`.
- Aplica la adaptación a filas planas y a documentos con clasificación anidada. Copia la clasificación antes de modificarla para no alterar el objeto original.
- `backend/tests/test_openapi_contract.py`: añade 16 casos parametrizados. Cada caso consulta lista y detalle, valida el JSON contra OpenAPI y Pydantic, verifica el tipo esperado y comprueba que el registro original no fue modificado. La persistencia está simulada.
- No se alteran firmas, schemas ni nodos del agente: se ajustan las respuestas para cumplir el contrato existente.

### 3. Frontend & UX

- Esta corrección no modifica archivos del frontend. Se verifica su compilación con los tipos generados actuales.

### 4. Infraestructura, Scripts & Documentación

- Se actualizan el documento PR1 y los índices de PR e historiales con esta verificación final.
- Se mantiene el alcance en US-01. La demostración funcional del PDF con IA real, OCI y extracción de medicamentos/dosis no forma parte de esta corrección.

## Verificación y pruebas

- Reproducción antes de corregir: 7 casos nuevos fallaban y 9 pasaban.
- Backend: **108 passed in 93.88s**, sin conexiones de pytest a la base de desarrollo.
- Frontend: `npm run build` en Docker, código 0; 78 módulos; build Vite de 2.28 s, sin errores TypeScript.
- Contrato: `make validate`, `make generate` y `make generate-check` terminan con código 0. Spectral informa 0 errores y 1 advertencia por `EntidadesMedicas` todavía sin uso.
- Generación: 4 salidas, 0 actualizadas; los modelos ya coinciden con el YAML.
- Alembic: `upgrade head`, `current` y `heads` correctos en Docker, revisión `n7o707411jk3`.
- Documentos reales: **3/3 compatibles** con `ResultadoTriaje` tras aplicar el adaptador, comprobados con `default_transaction_read_only=on`.
- No se verificaron llamadas reales a IA u OCI como parte de esta corrección.
