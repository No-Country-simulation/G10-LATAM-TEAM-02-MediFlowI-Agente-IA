# Data Model — API-04 (#35)

**Fecha**: 2026-10-10. Modelo **de lectura de datos existentes**, no creación de tablas, vistas, índices o migraciones. Las reglas funcionales aprobadas permanecen en [spec.md](spec.md); las decisiones de consulta siguientes son propuestas técnicas de plan. Ninguna instancia PostgreSQL fue inspeccionada.

## Entidades existentes y relaciones comprobadas

### Documento de triaje

`backend/alembic/versions/a3eb75cf454e_initial_schema.py:30–58`:

- `id`: UUID interno, PK; identidad canónica de relaciones.
- `documento_id`: `VARCHAR(255) UNIQUE NOT NULL`, identificador externo. Es la unidad pública aprobada de conteo; **no es el UUID interno**, aunque ambos puedan parecer cadenas en JSON.
- `status`: enum de estado. Valores iniciales `procesado/error/pendiente_auditoria` (`:25`), ampliados en `j3k303277fg9_add_document_statuses.py:18–23` a `recibido/procesando/rechazado/no_soportado`.
- `nivel_prioridad`: enum `Urgente/Rutina/Ambiguo`, nullable (`a3eb75cf454e_initial_schema.py:24,39`). Se lee la prioridad vigente, sin reconstruir la inicial.
- `requiere_auditoria_humana`: booleano no nulo, default falso (`:51`). Es evidencia suficiente cuando verdadero, pero no la única fuente histórica.
- `tiempo_procesamiento_ms`: integer nullable (`:58`), sin CHECK de no negatividad; el lector filtra negativos, no corrige datos.
- Paciente/episodio, metadata, nodos, fechas y contenido clínico: no se necesitan para elegir la población ni se devuelven. Ausencia de paciente/episodio no excluye.

La unicidad externa y una lectura de la tabla base sin joins expansivos implican que `COUNT(*)` sobre C equivale a contar `documento_id` distintos. No se necesita elegir arbitrariamente una fila por documento ni aplicar DISTINCT sobre tiempos (dos documentos pueden tener el mismo tiempo).

### Auditoría HITL heredada

`backend/alembic/versions/a3eb75cf454e_initial_schema.py:28,65–76`:

- `documento_triaje_id`: UUID obligatorio, FK a `documentos_triaje.id`.
- `documento_id`: texto externo conservado. No utilizarlo para sustituir la FK, hacer fallback o mezclar identidades.
- `decision`: enum `aprobar/rechazar/reclasificar`.
- Varias filas pueden referir al mismo documento. Identidad/auditor/justificación no se leen para respuesta pública. `auditor_id` pasó a UUID/FK de usuario en `k4l404288gh0_add_document_traceability.py:23–29`; las fixtures respetarán esa integridad.

### Auditoría de coordinación (BD-03)

`backend/alembic/versions/o8p808522kl4_implement_unified_db_proposal.py:66–80`:

- `documento_id`: **UUID interno nullable**, FK a `documentos_triaje.id`, no el identificador externo homónimo.
- `episodio_id`: nullable; no se usa para inferir documento.
- `decision`: `VARCHAR(30) NOT NULL`, no enum ni decisión clínica normalizada por este endpoint.
- Sin unicidad por documento; puede haber varios dictámenes o solo asociación a episodio.

BD-03 existe en `backend/app/repositories/audit_repository.py:20–31,87–138`, con comprobación de pool e inserción. El repositorio recibe texto externo y lo resuelve al UUID por subconsulta (`:98–101,115–118`); API-04 leerá el UUID ya almacenado. Esto acredita presencia en código/migraciones, no que haya tablas o dictámenes en el entorno destino.

### Historial del documento

`backend/alembic/versions/k4l404288gh0_add_document_traceability.py:39–48`:

- `documento_triaje_id`: UUID obligatorio/FK a `documentos_triaje.id`.
- `evento`: `VARCHAR(100) NOT NULL`, repetible; no enum ni unicidad por tipo.
- `created_at`, estados previos/nuevos, metadata: no imponen ventana temporal, vigencia de intento ni duración de la IA.
- `PROCESAMIENTO_FINALIZADO` acredita el procesamiento registrado requerido. Se inserta en el productor actual (`backend/app/repositories/postgres_storage.py:340–372`).
- Los cuatro eventos HITL admitidos se leen por nombre exacto. Para eventos genéricos de fixture se propone `DOCUMENTO_RECIBIDO`, ya emitido en `postgres_storage.py:345`, que no acredita HITL por sí solo.

Relaciones de lectura, todas por UUID:

```text
historial_documento.documento_triaje_id ─────> documentos_triaje.id
auditorias_hitl.documento_triaje_id ──────────> documentos_triaje.id
auditorias_coordinacion.documento_id ────────> documentos_triaje.id
```

No joins por paciente/episodio, no casts UUID->texto, no relación usando el texto externo de legacy como atajo. Un dictamen solo asociado a episodio, UUID nulo, documento fuera de C o vínculo a otro documento no cuenta para el documento consultado. Los huérfanos prohibidos por FKs no deben fabricarse desactivando restricciones en pruebas.

## Reglas de lectura aprobadas, sin cambios

### C, D y distribución — FR-002/003/011, SC-001

C incluye cada documento de todo el historial, sin fecha límite, si `status IN ('procesado','pendiente_auditoria','rechazado')` y existe al menos un historial final **ligado a su UUID**. D=|C|. No se exige paciente, episodio, tiempo, nodos ni origen; no se excluye metadata semilla. BD-04 recibido queda fuera y procesado posteriormente puede entrar con nodos vacíos/tiempo nulo. Otros estados y ausencia de evento final quedan fuera, aunque tengan prioridad o eventos antiguos.

Rojo cuenta Urgente, Amarillo cuenta Ambiguo, Verde cuenta Rutina; sin equivalencias clínicas nuevas. Prioridad nula permanece en D pero en ningún color. La suma de colores puede ser inferior a D; no completar con Rutina ni añadir categoría. La cobertura es procesamiento registrado alguna vez, no actividad total asegurada ni último intento; ausencia de evento no demuestra ausencia de procesamiento.

### H, N y tasa — FR-004/005/016, SC-002

Para cada documento de C, H es un booleano: bandera verdadera **OR** existe legacy con `aprobar/reclasificar/rechazar` **OR** existe historial con `PENDIENTE_AUDITORIA/AUDITORIA_APROBADA/AUDITORIA_RECLASIFICADA/AUDITORIA_RECHAZADA` **OR** existe coordinación directamente ligada con `aprobar/aprobado/reclasificar/reclasificado/rechazar/rechazado`.

Cada fuente basta sola. N=count(H=true), máximo un aporte por documento; tasa=100*N/D si D>0, null si D=0. N=0/D>0 produce 0. No inferir H de Ambiguo, `reasignado`, `derivar`, evento genérico ni episodio. No ampliar decisiones mediante lower/trim/sinónimos: las listas son exactas. La convención de coordinación no certifica de forma independiente motivo clínico, y falta de evidencia no acredita ausencia de revisión histórica.

### T, S y tiempo — FR-013/014, SC-003/005

T contiene los documentos de C con tiempo persistido no nulo y >=0. S es la suma **original** de esos milisegundos, una vez por documento. Promedio en segundos=S/|T|/1000 si |T|>0; null en otro caso. Cero participa y puede producir promedio 0; nulo/negativo no son ceros ni forman parte del divisor. No exigir nodos, último evento único ni origen real de medición. Se aceptan valores anteriores/sintéticos; no se certifican última ejecución/intentos/nodos/respuesta HTTP.

## Forma de consulta propuesta

Una sentencia de lectura asyncpg, con CTE lógicas (no objetos persistidos):

1. **`cohorte`**: SELECT de `documentos_triaje` con campos mínimos (`id`, prioridad, bandera y tiempo), filtro de estados y `EXISTS` de historial final. Calcular H con los tres `EXISTS` restantes más bandera. Las tablas conservadas son documentos/coordinación y las complementarias son legacy/historial; no se sustituye ninguna fuente.
2. **`agregados`**: un SELECT sin GROUP BY obtiene `COUNT(*) FILTER` por color, D, N, `COUNT(*) FILTER (WHERE tiempo_procesamiento_ms >= 0)` para |T| y `SUM(tiempo_procesamiento_ms::numeric) FILTER (...)` para S. SQL descarta nulos mediante el predicado; nunca `COALESCE(tiempo,0)` ni `SUM(DISTINCT tiempo)`. COUNT de conjunto vacío produce 0; SUM puede producir null y solo se utiliza cuando |T|>0.
3. **Proyección final**: una fila con cinco escalares públicos (tres colores y dos indicadores), sin exponer D/N/T/S, UUID o detalle. Aplicar guardas D=0/T=0 y el único redondeo final exacto descrito abajo. Mapear después a las tres raíces del modelo generado. Una llamada `conn.fetchrow` ejecuta la **misma sentencia** que validarán las pruebas PostgreSQL.

Esquema SQL documental de predicados, no archivo de implementación:

```sql
-- Base: una fila por documento externo UNIQUE.
FROM documentos_triaje d
WHERE d.status IN ('procesado', 'pendiente_auditoria', 'rechazado')
  AND EXISTS (
    SELECT 1 FROM historial_documento f
    WHERE f.documento_triaje_id = d.id
      AND f.evento = 'PROCESAMIENTO_FINALIZADO'
  )
-- H = bandera OR EXISTS(legacy por documento_triaje_id = d.id)
--             OR EXISTS(historial HITL por documento_triaje_id = d.id)
--             OR EXISTS(coordinacion por documento_id = d.id).
-- Cada EXISTS filtra su lista exacta anterior; no joins expansivos.
```

`EXISTS` no produce filas adicionales. Repetir un final, un dictamen o evidencias de varias tablas solo conserva H=true; no altera D, conteos ni S/T. Evita el error de compensar joins con COUNT(DISTINCT) mientras AVG/SUM siguen inflados. No utiliza `v_estadisticas_hoy`, que filtra día actual y población distinta (`a3eb75cf454e_initial_schema.py:174–186`).

## Aritmética y redondeo exactos propuestos

Como milisegundos son enteros y los valores admitidos/resultados no negativos, se propone cuantizar **solo el resultado final** mediante cociente entero exacto de `numeric`, evitando `AVG`/división aproximada previa, float y redondeo bancario de Python:

- Porcentaje a centésimas: `q = div(2 * 10000 * N + D, 2 * D)` si D>0; valor=q/100. Aquí `10000*N/D` es el porcentaje escalado por 100. Empate exacto sube una unidad final.
- Segundos a milésimas: `q = div(2 * S + |T|, 2 * |T|)` si |T|>0; valor=q/1000. Redondear S/|T| milisegundos **es** el redondeo final del promedio en segundos a tres decimales, no un redondeo previo por documento.
- Convertir operandos a `numeric` **antes** de multiplicar/sumar para evitar overflow bigint; SUM usa `numeric`. `div` trunca el cociente no negativo exacto sin división binaria; las divisiones finales por 100/1000 son decimales terminantes. Casos guardados: D=0 -> null, |T|=0 -> null, N=0 con D>0 ->0, S=0 con |T|>0 ->0.
- asyncpg entrega numeric como Decimal. Convertir el valor ya cuantizado a número compatible con `MetricsResponse` generado en la frontera de serialización; conservar None, nunca `str(Decimal)`/JSON string. No volver a redondear ni sustituir null. Verificar cuerpo JSON real contra el contrato. `1000+2333`, T=2 ->1.6665 ->1.667; N=1,D=3 ->33.33.

Alternativa evaluada: `ROUND(numeric, escala)` final tras división/AVG numeric, cuyo empate para valores positivos es hacia arriba. La propuesta de cociente entero explicita el empate sin depender de precisión intermedia de una fracción periódica; no introduce dependencia ni campo nuevo. El contrato no obliga a una técnica aritmética ni a padding textual.

## Snapshot, frescura y estados observables — FR-017, SC-009

El repositorio adquiere una conexión del pool global existente; abre una transacción **nueva por petición**, `READ COMMITTED`, `READ ONLY`, y ejecuta una única sentencia agregada. BEGIN/COMMIT son controles adicionales, no tres consultas de indicadores. SELECT sin FOR UPDATE comparte snapshot entre CTE/subconsultas/agregados; no bloquea filas para actualizar ni reutiliza snapshot entre peticiones. No caché de resultados ni TTL; el pool cacheado es conexión, no datos.

PostgreSQL 17 describe el snapshot de SELECT en READ COMMITTED en [§13.2.1](https://www.postgresql.org/docs/17/transaction-iso.html#XACT-READ-COMMITTED), consultado 2026-10-10. Una nueva petición después de COMMIT ejecuta la sentencia después de ese COMMIT y ve cambios conforme a C/H/T. Cambios durante autenticación/espera de conexión pueden aparecer; los posteriores al comienzo del SELECT no aparecen en esa sentencia. Ambas posibilidades durante la petición están aprobadas, sin mezclar vistas.

Autenticación se hace antes y es una lectura separada; la vista compartida exigida corresponde a los **tres indicadores**, no a un snapshot único de sesión más métricas. La transición atómica controlada de prueba debe observar antes o después completos. El UPSERT de resultados/historial actual no es una transacción única (`postgres_storage.py:220–372`); una parcialidad **ya confirmada** puede observarse y aplica C sin inventar atomicidad del productor. Resolver HITL usa su transacción (`:497–594`); API-04 no modifica ninguna de ellas.

## Índices y disponibilidad: evidencia estática, no garantía

- Documentos: PK/UNIQUE y estado/prioridad/bandera parcial (`a3eb75cf454e_initial_schema.py:31–32,103–108`).
- Historial: `(documento_triaje_id, created_at DESC)` (`k4l404288gh0_add_document_traceability.py:48`); localizar por UUID y filtrar evento.
- Coordinación: índice UUID `documento_id` (`o8p808522kl4_implement_unified_db_proposal.py:79`).
- Legacy: índice **texto externo**, no UUID referenciante (`a3eb75cf454e_initial_schema.py:113–115`). No se encontró índice específico de `documento_triaje_id` en migraciones inspeccionadas; FK no lo crea automáticamente. No usar una relación incorrecta para aprovechar el índice externo.
- Sesiones: token_hash UNIQUE e índices (`m6n606300ij2_add_persistent_user_sessions.py:17–30`).

No se crean índices ni migraciones en este alcance. Registrar tiempos en la comprobación práctica P04 vigente; no perfil obligatorio de benchmark ni SLA numérico. Si fuese necesario estudiar `EXPLAIN (ANALYZE, BUFFERS)`, solo en sandbox y fuera de observación; cualquier ajuste SQL requiere pruebas/equivalencia y autorización, y cambios de esquema requieren consulta separada. Índices/pool no demuestran carga ni rendimiento de la VM de producción.

## Modelo de salida y transiciones

`DistribucionPrioridadMetrics` y `MetricsResponse` son schemas contractuales propuestos, no tablas. Campos obligatorios y `additionalProperties: false` en ambos objetos; los dos indicadores aceptan número o null y no son opcionales. El endpoint no produce transiciones, eventos ni auditorías por leerse. Relecturas pueden observar cambios de estado, prioridad, evidencia o tiempo confirmados por otros procesos, siempre aplicando las reglas aprobadas. No normaliza/modifica productores, cuentas, permisos, configuración o archivos.
