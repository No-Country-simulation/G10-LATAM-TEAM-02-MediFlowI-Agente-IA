# Specification Quality Checklist: API-04 (#35) — Métricas hospitalarias de triaje

**Purpose**: Validar calidad y completitud antes de planificar, separando decisiones confirmadas, propuestas y hechos del repositorio.
**Created**: 2026-10-10
**Feature**: [spec.md](../spec.md)
**Status**: Especificación aclarada — 16/16 criterios documentales, revalidados tras revisión práctica P04 del 2026-10-11; sin decisiones pendientes. T001–T021 conservan evidencia; T022–T029/Scalar/puertas finales pendientes. P04 actual conserva «sin retrasos perceptibles» con tiempos observados/Scalar sin SLA numérico, no carga ni VM de producción. Checklist no acredita ejecución ni completa tareas.

## Content Quality

- [x] CHK001 No implementation details (languages, frameworks, APIs).
- [x] CHK002 Focused on user value and business needs.
- [x] CHK003 Written for non-technical stakeholders.
- [x] CHK004 All mandatory sections completed.

## Requirement Completeness

- [x] CHK005 No clarification markers remain.
- [x] CHK006 Requirements are testable and unambiguous.
- [x] CHK007 Success criteria are measurable.
- [x] CHK008 Success criteria are technology-agnostic (no implementation details).
- [x] CHK009 All acceptance scenarios are defined.
- [x] CHK010 Edge cases are identified.
- [x] CHK011 Scope is clearly bounded.
- [x] CHK012 Dependencies and assumptions identified.

## Feature Readiness

- [x] CHK013 All functional requirements have clear acceptance criteria.
- [x] CHK014 User scenarios cover primary flows.
- [x] CHK015 Success criteria define verifiable acceptance outcomes and their conditions, without requiring implementation or executed API-04 tests at specification time.
- [x] CHK016 No implementation details leak into specification.

## Notes

### Antecedente histórico — validación documental de la primera revisión

**Antecedente histórico**: estos puntos registran la evaluación inicial. Q1–Q6/P01/P03/P06 y frescura/coherencia siguen intactos; el benchmark/perfil P04, cifras de SC-006 y razones técnicas asociadas fueron sustituidos por la revisión práctica vigente al final de este documento, no son bloqueos de entrega actuales.

- **Confirmado Q1**: «Documentos de triaje»; conteo por documento, no paciente ni ejecución.
- **Confirmado Q2**: colores de presentación `Urgente`→rojo, `Rutina`→verde, `Ambiguo`→amarillo/ámbar. No severidad clínica intermedia; contrato futuro debe explicarlo.
- **Confirmado Q3**: mantener documentos/coordinación y autorizar lecturas históricas complementarias de auditoría heredada e historial; deduplicar casos y conservar revisión resuelta. No se aprobó cohorte/denominador ni lista exacta de evidencias.
- **Confirmado Q4 en clarify**: evento final de procesamiento ligado al documento y estado actual procesado/pendiente_auditoria/rechazado; todo el historial, denominador por documento distinto, sin exigir nodos/tiempo/paciente/episodio. Prioridad vigente; nulos fuera de colores pero dentro del denominador. BD-04 procesado después puede entrar; ausencia de evento significa falta de cobertura, no ausencia demostrada de procesamiento.
- **Confirmado Q5 en clarify**: todos los usuarios con sesión válida y activa, incluidos ADMINISTRADOR/COORDINADOR/SUPERVISOR/AUDITOR/OPERADOR, acceden exclusivamente a agregados; no se amplían otros permisos. 401 para sesión ausente/inválida/expirada; 503 si falla validación por PostgreSQL. Fundamento contrastado: matriz Dashboard & KPIs de DocumentationView y ProtectedRoute sin filtro de rol, citados en F09b.
- **Confirmado Q6/P05 en clarify**: promedio una vez por documento elegible del tiempo persistido no nulo/no negativo, convertido a segundos; cero entra y nulo no se convierte en cero. Acepta valores anteriores/sintéticos sin garantizar última ejecución/intentos/nodos/respuesta HTTP completa; exige documentar límites y no cambiar productores.
- **Confirmado P06 en clarify**: bandera, legacy con decisiones admitidas, cuatro eventos HITL específicos o dictamen directamente ligado de coordinación con aprobar/aprobado/reclasificar/reclasificado/rechazar/rechazado; cada evidencia basta sin corroboración duplicada, contar una vez solo en Q4. Excluir otras decisiones, vínculos solo a episodio y Ambiguo sin evidencia. Convención y límites explícitos, sin modificar el flujo.
- **Confirmado P01 en clarify**: exactamente tres raíces y colores Rojo/Amarillo/Verde; conteos enteros, tasa 0–100/segundos como números o null. Null sin denominador/valores, cero cuando el cálculo con datos da cero. Redondear una vez al final a dos/tres decimales, empate hacia arriba; no strings numéricos, campos extra o padding obligatorio.
- **Confirmado P03 en ronda de cierre**: conformidad OpenAPI futuro, modelos/tipos generados coherentes y prueba TypeScript externa al dashboard con números/null normales/cero/sin datos; mantener null, claves, unidades y redondeo. DashboardSummary no consume /metrics: no hay promesa de integración visual ni cambios de dashboard.
- **P04 histórica, sustituida**: el benchmark/perfil anterior fue evaluado entonces (4 CPU/SSD, primero 8 GB disponibles y después VM conjunta 4 GB, dataset 1000/300/200/8000, 20 calentamientos/500 medidas/cinco clientes, ≥475 ≤500 ms/timeout 5 s). No es requisito vigente ni ejecución acreditada. Se conserva en spec Clarifications/antecedente P04 y quickstart §6-H. Frescura/vista coherente FR-017/SC-009 y desarrollo preservado siguen vigentes, separadas de la prueba de carga retirada.
- **CHK001/CHK016 — evaluación histórica**: las condiciones de benchmark/VM se habían tratado entonces como restricciones confirmadas. Esa justificación queda sustituida: las excepciones vigentes se limitan a restricciones heredadas ruta/campos/PostgreSQL/asyncpg/contrato/generación/consumo/Scalar, sin perfil de carga o recursos obligatorio. La transición funcional no modifica atomicidad del productor; técnica SQL/caché/índices pertenece al plan.
- **CHK005 cumplido**: sin marcadores; P03/P04 confirmadas, sin otras decisiones pendientes. No se infiere aprobación por ausencia de marcadores.
- **CHK006/CHK009/CHK013 cumplidos tras P03/P04**: FR-010/015/017 y escenarios 8–10 de historia 4 fijan consumo tipado, carga/errores y frescura/coherencia. Los demás FR y casos mantienen decisiones anteriores y aceptación explícita en SC-001–009; no se introducen reglas clínicas ni exigencia de integración visual.
- **CHK007 — evaluación histórica sustituida para SC-006**: las cifras de benchmark eran la condición entonces; SC-006 vigente requiere tiempos prácticos/Scalar y valoración manual, no umbral numérico. SC-009 coherencia y SC-008 contrato permanecen intactos. La revalidación vigente al final de este documento explica el resultado documental actual, sin afirmar mediciones.
- **CHK008 cumplido**: SC describe conteos, porcentajes, tiempo percibido, protección de datos y resultados observables; no prescribe framework, mecanismo SQL ni estrategia de caché.
- **CHK015 cumplido por definición verificable completa**: P03/P04 fijan condiciones de SC-006/008/009, y las demás ya eran verificables. No exige implementar ni ejecutar pruebas para finalizar especificación; suites/benchmark aún no acreditan aceptación y se documentan separadamente.
- **CHK002/003/004/010/011/012/014 cumplidos**: historias explican valor para Director Médico/Tech Lead y seguridad, todas las secciones efectivas están presentes, se cubren casos vacíos/repeticiones/fallos/permisos, se acota alcance, se verifica BD-03 en repositorio/esquema/uso estático y se separan propuestas de decisiones. No se añade API-02 como dependencia ni se cambia BD-04.

### Antecedente histórico — pendientes resueltos durante clarify

- Q4 resuelta: definición en FR-011; límites de cobertura explícitos. No se infiere último procesamiento mediante nodos.
- Q5 resuelta: cualquier sesión válida y activa; no se aplica 403 por rol al endpoint ni se amplían permisos de otras operaciones.
- Q6 resuelta: promedio de tiempo registrado con límites aceptados, no garantía de ejecución vigente.
- P01 resuelta: formato, nulabilidad y redondeo en FR-001/014 y escenarios de vacío/cero.
- P02 resuelta: procesamiento registrado/estado/prioridad/origen semilla Q4 y selección temporal Q6.
- P03 resuelta en ronda de cierre: contrato verificable y aptitud de consumo tipado, sin integración visual ni cambios de dashboard.
- P04 se resolvió entonces con perfil/benchmark, después sustituido por aceptación práctica FR-015/SC-006; latencia distinta de tiempo IA y frescura/coherencia FR-017/SC-009 se conservan.
- P05 resuelta: prioridad vigente Q4 y tiempos anteriores/sintéticos persistidos Q6, una vez por documento.
- P06 resuelta: lista y suficiencia de evidencias en FR-016; cobertura física se verificará posteriormente sin exigir cambios del flujo ni reabrir la convención.

### Evidencia histórica de specify (2026-10-10) — no estado actual ni aceptación de API-04

- Backend: `pytest -q` **no inicia**, falta `bcrypt` en el intérprete disponible. No se considera suite ejecutada ni BD-03 probado en verde en esta sesión.
- Frontend: `npm test` y `npm run build` **fallan** por `ReferenceError: module is not defined` en `frontend/tailwind.config.js:2` con Node v22.12.0. No se modifica configuración ni código para forzar éxito.
- Alembic: `upgrade head --sql` **correcto**, únicamente generación offline con URL de pruebas; no se aplicó SQL ni se verificó instancia live.
- Conexiones automáticas a desarrollo deshabilitadas para pytest; integración PostgreSQL BD-04 no activada. No se modificó `mediflow_dev`, modo de almacenamiento, semilla ni reglas del agente.
- Presencia de BD-03 y migraciones no acredita uso real de coordinación: el flujo actual resuelve en `auditorias_hitl`; no se encontraron llamadas productivas a `AuditRepository`.

### Antecedente histórico — puerta de revisión de specify/clarify

Primera ronda: 5 preguntas/respuestas, checklist 8/16 → 9/16 y CHK005 recién cumplido. Ronda de cierre: 2 preguntas/respuestas, checklist 9/16 → 16/16; pasan CHK001/006/007/009/013/015/016, sin regresiones ni casillas abiertas. CHK001/016 tienen excepciones técnicas documentadas y CHK015 evalúa definición verificable, no ejecución. Sin decisiones pendientes: especificación lista para plan bajo autorización explícita. **No ejecutar plan, tasks ni implement en esta entrega.** Bloqueos de suites y verificación empírica posterior permanecen separados; no se declara API-04 implementada, contrato actualizado, SLA demostrado ni pruebas en verde.

### Antecedente histórico — revisión P04 de memoria (2026-10-11)

**Registro histórico de primera revisión de memoria**, sustituida después por aceptación práctica: conservar estas observaciones, no usarlas como criterio vigente.

- Cambio confirmado directamente, **0 preguntas nuevas**: límite conjunto de 4 GB totales; memoria disponible al inicio/durante la prueba, sin mínimo de 4 GB libres. Spec FR-015/SC-006/P04, plan/research/quickstart y tasks T022–T024 sincronizados; speckit-analyze antes de reanudar T022.
- **16/16 → 16/16**, sin cambios de casillas, regresiones ni pendientes documentales; todas las categorías de cobertura funcional/datos/interacción/calidad/integraciones/errores/restricciones/terminología/cierre quedan claras. No se reabre población, permisos, colores, HITL, tiempos, nulabilidad, redondeo, UI ni los demás criterios de rendimiento.
- Las evidencias posteriores de suites están en `tasks.md`; los fallos de specify se conservan arriba únicamente como antecedentes. La verificación del entorno limitado y la medición P04 no están acreditadas por esta revisión. T022 sigue pendiente hasta demostrar recursos efectivos y guardas; no hay autorización documental para conectar desarrollo, modificar código/frontend, hacer commit ni PR.

### Revalidación vigente — P04 práctica sin benchmark obligatorio (2026-10-11)

- Decisión directa del usuario registrada en spec Clarifications: **0 preguntas nuevas**, sin ambigüedad crítica adicional. Recursos fijos/VM 4 GB, fixture de carga, calentamientos, 500 medidas/cinco clientes, umbral 500 ms/475 respuestas y timeout 5 s dejan de ser criterios o bloqueos de aceptación; issue #35 reconsultada vía API pública y tarea 3.4 local no los exigen. No se demuestra ni se acredita retroactivamente el perfil anterior.
- **CHK006/007/009/013/015**: FR-015/SC-006/historia 4 escenario 9 exigen comprobar GET con PostgreSQL aislado/sesión real, registrar tiempos observados/estado/contrato/oráculo/contexto y revisar manualmente Scalar «sin retrasos perceptibles». Sin SLA numérico inventado. La evaluación manual debe quedar registrada; un fallo/timeout/incompleto, skip o simple prueba HTTP automática no la sustituye. Declaración obligatoria: no demuestra rendimiento bajo carga ni en VM de producción. Reproducibilidad de contexto/método no significa garantía universal de percepción o rendimiento.
- **CHK001/008/016**: restricciones técnicas heredadas justificadas (ruta/campos, PostgreSQL/asyncpg, OpenAPI/generación/consumo, Scalar); se retira la excepción de VM/benchmark como restricción vigente. No nueva arquitectura ni despliegue; resultados observables, sin técnica SQL/caché impuesta. Coherencia concurrente funcional FR-017 se conserva, no prueba de carga.
- **Resto de criterios**: valor/historias, límites de dominio, permisos/errores/vacíos, tiempos anteriores/sintéticos, redondeo, seguridad e integraciones siguen claros e intactos. Guardas T002/identidad real antes de SQL y puertas AGENTS.md se mantienen. Nunca pruebas automáticas sobre mediflow_dev. Plan/research/quickstart/tasks sincronizados; T022–T024 redefinidas sin benchmark, Scalar/puertas con dependencias independientes. Intentos y decisión histórica conservados; no tasks realizadas por documentación.
- **16/16 → 16/16**; sin cambios de casillas ni regresión documental. Cobertura funcional/datos/interacción/calidad/integraciones/errores/restricciones/terminología/cierre clara. La revisión anterior se detuvo antes de implement y no creó evidencia empírica. El usuario autoriza ahora una limpieza/analyze y continuación desde T022 si no hay contradicciones; no tareas completadas por autorización/documentación. Sin cambios funcionales/FR-015/SC-006, frontend/Compose/desarrollo ni commits/PR.
