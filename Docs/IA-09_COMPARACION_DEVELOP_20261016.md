# Comparación e integración local de IA-09 con develop

## Referencias y respaldo

- Fecha: 16 de octubre de 2026.
- Rama local: `dev-Jefte-Reyes`.
- Base anterior de IA-09: `9ef29a1`, después del trabajo de IA-08.
- Develop obtenido de GitHub y aplicado por fast-forward: **482da50**.
- Diez commits nuevos respecto de esa base; 68 archivos cambiados en develop.
- Los cambios de IA-09 siguen en el árbol de trabajo, sin commits propios ni push.

Antes de actualizar se guardaron los 20 archivos modificados/nuevos de IA-09
en `.venv/ia09-before-develop-20261016-144952.zip`, con manifiesto SHA-256 y base
de origen. La integridad de las 20 entradas se verificó después de la integración.
Además se conserva el stash `backup IA09 local antes de integrar develop
482da50 2026-10-16`, incluidos los archivos nuevos. No se eliminó ese respaldo.

## Aportes encontrados en develop

| Área | Cambios aceptados | Tratamiento en IA-09 |
| --- | --- | --- |
| IA-08 / PR #75 | Alertas SSE, persistencia previa, RBAC y migración MEDICO de nuestro trabajo anterior | Ya son parte de develop; no se reaplicaron ni duplicaron |
| Ingesta multimodal / PR #52 | `completar_multimodal`, visión para imagen/PDF escaneado, rasterizado, OCR de respaldo, WebP y `metodo_extraccion` | Conservados; fusión de imágenes usa ese mismo transporte; PDF mantiene la ruta nueva de develop |
| IA-07 / PR #76 | `MedicamentoPrescritoState`, extracción/deduplicación de medicamentos, catálogo de controlados y routing a Farmacia | Conservados también cuando los datos provienen de Fusion |
| Frontend / PR #74 | Nuevos diseños y pruebas de triaje, auditoría, registro y componentes comunes | Se mantienen los archivos recibidos de develop; se retira únicamente una importación sin uso que impedía compilar |

No se sustituyeron el cálculo de confianza, sus umbrales, la precedencia de
urgencias, las reglas de identidad, la validación CIE-10 o la retención de
medicamentos controlados por versiones anteriores.

## Conflictos resueltos

Hubo cuatro archivos con conflicto al recuperar el trabajo local:

1. `graph.py`: se conserva el grafo compilado reutilizable y el contexto por
   solicitud. Ingesta, extracción y clasificación reciben el mismo cliente y
   el contexto efímero, sin compartir pacientes entre solicitudes.
2. `extraction.py`: se une la reutilización de Fusion con el modelo y parser
   nuevos de medicamentos. CIE-10, identidad y consolidación se ejecutan igual
   con respuesta Fusion y con extracción convencional.
3. `ingestion.py`: se conserva la ingesta convencional de develop y se añade
   la entrada Fusion para imágenes dentro del grafo. WebP se comprime a JPEG;
   se mantiene el método de extracción y la limpieza de Base64.
4. `llm_service.py`: se conserva `completar_multimodal` y su soporte de varias
   imágenes. `completar_imagen` valida Gemini y delega a ese método. Se mantienen
   `timeout=30` y `max_retries=2`, sin un segundo transporte redundante.

La nueva especificación de ingesta exige OCR de respaldo (FR-004). La decisión
previa y explícita del usuario para IA-09 exige revisión humana sin otro intento
OCR/LLM si falla Fusion. Se conserva esa decisión en la ruta Fusion y el fallback
de develop en la ingesta convencional, incluido PDF. No se afirma que FR-004
se cumpla en la ruta Fusion de imágenes ni se reescribe la especificación aceptada.

## Contratos y ajuste de compilación

- Se regeneraron los DTO Python y TypeScript desde el contrato combinado, con
  `MedicamentoPrescrito`, los modelos Fusion y los datos previos de IA-08.
- Se documenta `metodo_extraccion` con los valores existentes y la admisión de
  WebP en upload. No se crea un valor de método exclusivo que rompa consumidores.
- Se retiró `import { Link } from 'react-router-dom'` en `UsersManagementView.tsx`:
  el nuevo develop dejó esa importación sin uso y TypeScript emitía TS6133.

## Pruebas añadidas para los cruces

- WebP de develop convertido a JPEG dentro del presupuesto Base64 de IA-09.
- Prescripciones procedentes de Fusion conservadas hasta Farmacia.
- Medicamentos controlados de Fusion retenidos para revisión.
- `metodo_extraccion` mantenido en el estado y los metadatos del servicio.
- Fallo Fusion sin volver a OCR ni a extracción/clasificación mediante LLM.

Las pruebas existentes de ingesta multimodal y fallback convencional se
conservaron y se ejecutaron junto a las regresiones IA-09, sin desactivarlas.

## Límites de esta comprobación

Verificación final de la integración:

- Agente, visión, OCR, medicamentos y Fusion: **83 pruebas aprobadas**.
- Backend completo: **480 aprobadas y 102 omitidas**, sin fallos.
- Frontend nuevo de develop: **80 aprobadas**, sin fallos, y build correcto.
- Ruff de los archivos Python integrados: correcto.
- `generate.py --check`: contrato y tipos sincronizados; cero errores y seis
  advertencias preexistentes de coordinación (tag y nombre de esquema Bearer).
- `alembic upgrade head --sql`: correcto, sin conectarse a PostgreSQL.
- No quedan conflictos ni archivos preparados para commit. HEAD coincide con
  origin/develop en `482da50`; los cambios IA-09 se conservan sin publicar.

Durante la verificación hubo una ejecución que leyó el contrato mientras se
estaba actualizando, causando un fallo de reproducibilidad. Se repitió la suite
con el contrato definitivo sin modificaciones concurrentes: el resultado final
es el indicado arriba. No se relajaron ni desactivaron pruebas para aprobarla.

No se escribió en `mediflow_dev`, no se modificó LOCAL/OCI ni se aplicaron
migraciones sobre una base compartida. Las integraciones con PostgreSQL real
requieren sus sandboxes y no se activaron en esta ejecución.

La primera comprobación sin credencial registró cero muestras válidas. Después
se realizó el benchmark autorizado con Gemini real: `gemini-3.5-flash-lite`,
20 muestras válidas y 20 invocaciones de visión; p50 de 9,794 s, p95 de 24,061 s
y máximo de 27,341 s. Los detalles y límites están en
[IA-09 Pipeline Fusion](IA-09_PIPELINE_FUSION.md#benchmark-real-comparación-antes-y-después).
La clave solo se cargó en memoria, sin modificar los archivos de configuración.
Esa primera medición no cumplió el objetivo. Después se añadió JSON Schema nativo
y razonamiento low, autorizado para Fusion con Gemini 3. La nueva serie completa
de 20 muestras válidas obtuvo **p50 de 2,002 s, p95 de 3,657 s y máximo de 3,895 s**.
Se usaron pausas de seis segundos entre documentos para respetar la cuota,
fuera del tiempo de cada grafo; la serie previa sin pausas tuvo dos fallos por
cuota y se conserva como no aprobada. Se verificaron también los datos explícitos
y las prioridades de los documentos sintéticos. El resultado acredita latencia
individual en esas condiciones, sin certificar carga concurrente ni precisión
clínica general. No se realizaron commits ni push de este trabajo local.

La regresión final tras optimizar Fusion obtuvo **487 pruebas backend aprobadas
y 102 omitidas; 80 frontend aprobadas**, build, Ruff, contratos y Alembic offline
correctos. Las omisiones de integración existentes siguen requiriendo sus sandboxes.
