# IA-08: alertas de guardia mediante SSE

## Alcance acordado

Cuando el destino definitivo del documento es `Cola_Emergencia_Medica`,
se guarda un evento `ALERTA_GUARDIA_EMITIDA` en PostgreSQL y se difunde
mediante `GET /api/v1/alerts/stream`. Pueden suscribirse exclusivamente
`MEDICO`, `COORDINADOR` y `ADMINISTRADOR` con una sesión Bearer activa.

La alerta contiene `id` del evento, `documento_id`, `episodio_id` si existe,
`prioridad`, `fecha` y un mensaje genérico. No incluye nombre, documento de
identidad, diagnóstico, texto del documento ni metadatos arbitrarios del agente.
El acceso a los detalles clínicos sigue los endpoints y permisos existentes.

## Flujo y responsabilidades

```mermaid
sequenceDiagram
    participant G as LangGraph / routing
    participant T as TriageService
    participant P as PostgreSQL
    participant B as AlertBroadcaster
    participant S as Cliente SSE autorizado
    G->>T: Decisión y notificación genérica preparada
    T->>T: Resolver identidad y episodio; comprobar destino final
    T->>P: Guardar documento y resultado
    P-->>T: Confirmación
    alt Destino final de emergencia
        T->>P: INSERT ALERTA_GUARDIA_EMITIDA ligado al documento
        P-->>T: Evento confirmado, UUID y fecha
        T->>B: Publicar evento SSE
        B-->>S: JSON mínimo, tras revalidar sesión y rol
    end
```

- `routing.py` prepara la notificación; no realiza conexiones ni escrituras.
  Conserva las reglas clínicas actuales, incluidos los bloqueos CIE-10.
- `triage_service.py` despacha después de persistir el documento y comprobar
  el destino definitivo. Un conflicto de identidad cancela la notificación
  preparada y conserva la derivación a revisión.
- `alert_repository.py` realiza un `INSERT ... SELECT` parametrizado sobre
  el documento persistido cuyo destino sigue siendo emergencia. Usa el UUID
  interno y el episodio guardados en PostgreSQL, nunca un documento huérfano.
  La fecha y el UUID del evento proceden de PostgreSQL. Solo inserta trazabilidad.
- `alert_service.py` difunde el evento confirmado en una `asyncio.Queue`
  independiente y limitada a 128 eventos por conexión. La publicación no espera
  a lectores lentos; una cola llena cierra esa suscripción y registra un aviso.
- `alerts.py` valida RBAC al conectar y revalida la sesión y el rol antes de
  cada evento y cada mantenimiento de 15 segundos. Un fallo de autenticación
  durante el flujo lo cierra. La desconexión libera la cola, incluida cancelación.

No se añaden tablas ni columnas: se utiliza `trazabilidad_eventos` existente.
No se modifica la configuración de almacenamiento `LOCAL`/`OCI`.
La migración `r1s111855no7_add_medico_role.py` añade `MEDICO` a `rol_enum`.
Este rol ya existía en la aplicación y en el alcance aprobado, pero faltaba
en las migraciones de develop. La comprobación real detectó y corrigió esa
inconsistencia. El downgrade conserva el valor para no invalidar usuarios.

## Conexión

Desde PowerShell, con una sesión real de uno de los roles autorizados:

```powershell
curl.exe -N -H "Authorization: Bearer <TOKEN_DE_SESION>" http://localhost:8000/api/v1/alerts/stream
```

La conexión devuelve `Content-Type: text/event-stream`,
`Cache-Control: no-cache, no-transform` y `X-Accel-Buffering: no`.
Al conectarse llega `: connected`; durante inactividad llega `: heartbeat`.
Ambos son comentarios SSE, no alertas clínicas.

Un evento tiene este formato (datos sintéticos):

```text
id: 00000000-0000-4000-8000-000000000001
event: ALERTA_GUARDIA_EMITIDA
data: {"id":"00000000-0000-4000-8000-000000000001","documento_id":"DOC-PRUEBA","episodio_id":null,"prioridad":"Urgente","fecha":"2026-10-14T12:00:00Z","mensaje":"Documento crítico pendiente de atención del equipo de guardia."}

```

Sin sesión: HTTP 401. Con OPERADOR/AUDITOR: HTTP 403. Si PostgreSQL impide
validar la sesión inicial: HTTP 503. No se admiten tokens en la URL.
En navegador usar `fetch` con Authorization y lectura incremental del cuerpo,
o una biblioteca SSE con soporte de cabeceras. `EventSource` nativo no permite
establecer esa cabecera. Esta tarea no añade una pantalla de alertas al frontend.

## Fallos y límites operativos

Si no se confirma el documento o falla el registro del evento, no se publica
la alerta y el triaje devuelve error. Si se confirma el documento pero falla
el evento, el documento puede quedar guardado: no hay transacción conjunta ni
rollback del procesamiento previo. Un fallo de archivo físico no suprime una
alerta cuyo documento y evento sí se guardaron; el error del archivo se conserva.

Las colas pertenecen a un proceso. Ejecutar con **un worker** para que productores
y suscriptores compartan el broadcaster. Varios workers o réplicas necesitan un
broker compartido; esta implementación no proporciona difusión entre procesos.

La bitácora es duradera; la entrega SSE es en vivo. No hay reproducción automática
con `Last-Event-ID`, confirmación de lectura, deduplicación de reprocesamientos ni
recuperación automática del intervalo entre COMMIT y publicación si el proceso
cae. Un cliente desconectado o lento debe reconectarse y revisar la bandeja
clínica/bitácora existente. El UUID del evento identifica el registro; no promete
entrega exactamente una vez. SSE no sustituye los procedimientos de guardia.

## Validación

Desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_alert_broadcaster.py backend/tests/test_alert_service.py backend/tests/test_alert_repository.py backend/tests/test_alerts_api.py backend/tests/test_triage_alerts.py -v
```

Las pruebas cubren difusión a varios clientes, sobrecarga, cancelación,
transmisión ASGI incremental sin finalizar la respuesta, RBAC, revocación,
mantenimiento, SQL parametrizado, contenido mínimo, cancelación por identidad,
orden de persistencia y errores HTTP. Los repositorios usan dobles de prueba;
estas pruebas no escriben en `mediflow_dev` ni certifican una ejecución sobre
PostgreSQL real. El contrato se mantiene en `specs/openapi.yaml`,
`specs/paths/alerts.yaml` y `specs/components/schemas.yaml`; los tipos de Python
y TypeScript se regeneran con `infrastructure/scripts/generate.py`.

### Comprobación con PostgreSQL real

`backend/tests/test_alerts_postgres.py` levanta la API en un proceso propio,
con archivos en un directorio temporal y credenciales de prueba, sobre una base
PostgreSQL 17 desechable. Aplica las migraciones reales y usa login, sesiones,
repositorios y transmisión HTTP/SSE reales. Solo se simula el proveedor LLM.

La activación requiere `IA08_TEST_DATABASE_URL` e `IA08_SANDBOX_REGISTRATION`.
La URL debe apuntar a `127.0.0.1`, un puerto diferente de 5432, usuario `ia08_test`
y base `mediflow_ia08_test`, sin parámetros que redirijan la conexión. El registro
JSON debe declarar `owned: true`, `purpose: "ia08-check"`, el mismo `port` y un
`name` que empiece por `mediflow-ia08-check-`. Se verifica también la identidad
efectiva de la conexión antes de aplicar migraciones. Sin activación explícita
se omite únicamente la prueba real; las cuatro pruebas de rechazo de destinos
inseguros siguen ejecutándose.

Ejecutar, con esas variables definidas para un contenedor propio y desechable:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_alerts_postgres.py -v
```

La comprobación realizada usó PostgreSQL **17.11**, base `mediflow_ia08_test`,
API en puerto efímero y Alembic head **r1s111855no7**. Se confirmó:

- Recepción del mismo evento en tres conexiones SSE: MEDICO, COORDINADOR y ADMINISTRADOR.
- Rechazo real de OPERADOR/AUDITOR con 403 y de peticiones sin sesión con 401.
- Asociación al episodio existente y relación del evento con el UUID interno del documento.
- Visibilidad del evento confirmado desde otra conexión PostgreSQL.
- JSON mínimo, sin identificadores personales ni diagnóstico.
- Error HTTP 503 y ausencia de alerta SSE al provocar un fallo real de INSERT
  mediante un trigger temporal en la base desechable.
- Configuración de almacenamiento intacta antes y después de la prueba.

El contenedor se elimina después de la verificación. No se conecta ni se escribe
en `mediflow_dev`. La migración MEDICO solo se aplicó en esa base desechable;
queda versionada para su aplicación normal en los demás entornos.

### Resultado local del 14 de octubre de 2026

- Backend completo: **435 aprobadas, 101 omitidas**, sin fallos, con la integración
  PostgreSQL de IA-08 activada. Incluye 34 pruebas específicas previas de alertas,
  tres comprobaciones del contrato y cinco nuevas comprobaciones del sandbox/E2E.
- Frontend: **64 aprobadas**, sin fallos; `npm run build` correcto.
- Ruff de los archivos de implementación y pruebas de alertas: correcto.
- `alembic upgrade head --sql`: correcto, sin conexión ni cambios en la BD.
- `generate.py --check`: tipos sincronizados y cero errores del contrato.
  Se mantienen seis advertencias preexistentes de coordinación: tag no declarado
  globalmente y referencia `bearerAuth` frente al esquema `BearerAuth`.
  La regeneración también incorpora DTO de coordinación ya definidos en el
  contrato de develop, pero ausentes en los tipos generados anteriores.

Las 101 pruebas omitidas pertenecen a integraciones de otras tareas que requieren
sus propios sandboxes explícitos. No se acredita su ejecución. La persistencia
y la entrega SSE de IA-08 sí se comprobaron contra PostgreSQL real.
Esta comprobación se realizó en local, antes de publicar la rama para revisión;
no acredita un despliegue en desarrollo compartido ni en producción.
