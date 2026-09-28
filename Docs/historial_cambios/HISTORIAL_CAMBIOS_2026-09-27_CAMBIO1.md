# Historial de Cambios — 2026-09-27 (CAMBIO1)

**Fecha**: 27/09/2026 (obtenida del sistema)  
**Identificador de Cambio**: CAMBIO1  
**Autor**: Krystopher  
**Sprint / Fase**: Sprint 1 — Verificación Docker y cierre del pendiente Alembic de US-01  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal

## Resumen Ejecutivo

Se construyó y levantó el entorno Docker de desarrollo con la configuración existente del repositorio. Se confirmó la conexión real a PostgreSQL y la coincidencia de la revisión instalada de Alembic con el head del código. Esta comprobación resuelve el pendiente registrado en [la revisión anterior](HISTORIAL_CAMBIOS_2026-09-26_CAMBIO2.md) y actualiza [el documento del PR](../pull_requests/PULL_REQUEST_2026-09-26_PR1.md).

## Detalle de Cambios por Capa Técnica

### 1. Base de Datos & Migraciones

- Se creó `mediflow-postgres-dev` desde `postgres:17-alpine` y su volumen `docker_mediflow-postgres-dev-data`. No se eliminaron volúmenes existentes ni se modificaron otros proyectos Docker.
- El backend ejecutó `alembic upgrade head` como parte de su comando de arranque. `alembic current`, `alembic heads` y la consulta a `alembic_version` confirmaron **`n7o707411jk3`**.
- Se verificaron las tablas `alembic_version`, `auditorias_hitl`, `cola_procesamiento`, `configuracion_sistema`, `documentos_triaje`, `historial_documento`, `notificaciones`, `pacientes`, `sesiones_usuario` y `usuarios`.
- Se consultó `configuracion_sistema`: `modo_almacenamiento = LOCAL`. Las migraciones existentes inicializan esta configuración; no se cambió a OCI.
- No se escribieron nuevas migraciones ni se modificó su código. La base fue inicializada mediante las migraciones existentes, incluidos sus datos iniciales.

### 2. Backend & Agente IA

- Se reconstruyó `docker-backend` y se recreó `mediflow-backend-dev`. El contenedor quedó activo y saludable en el puerto 8000.
- Docker Compose proporciona `DATABASE_URL` dentro del contenedor y usa `postgres` como host de la red interna. La ausencia de esa variable al ejecutar Alembic desde Windows no impide esta configuración Docker.
- La comprobación de salud confirmó `postgres_disponible: true`. Reportó `llm_disponible: false`; no se validó clasificación con un proveedor de IA real.

### 3. Frontend & UX

- Se reconstruyó `docker-frontend` y se recreó `mediflow-frontend-dev`. Vite quedó activo en el puerto 5173.
- El primer intento de construcción falló por un error de red durante `npm ci`; el reintento completó la instalación sin modificar código ni configuración.
- No se cambiaron pantallas, estilos ni lógica de la aplicación.

### 4. Infraestructura, Scripts & Documentación

- Comando ejecutado desde la raíz: `docker compose -f infrastructure/docker/docker-compose.dev.yml up --build -d`.
- Docker Desktop se encontró en la instalación por usuario. Se utilizó su ejecutable por ruta absoluta y se añadió su directorio al PATH del proceso para la construcción, sin cambiar el PATH global.
- Se actualizó el documento local del PR para cerrar el pendiente de Alembic y se añadió este registro al índice. Los registros anteriores conservan los resultados históricos y enlazan a esta verificación posterior.

## Verificación y Pruebas

- **Docker Compose**: comando final con código 0; tres servicios activos, PostgreSQL y backend saludables.
- **Base real**: Alembic en `n7o707411jk3 (head)`, verificado también por SQL; almacenamiento LOCAL.
- **Frontend**: `http://localhost:5173/` devuelve HTTP 200.
- **Backend**: `http://localhost:8000/health` devuelve HTTP 200, `status: ok` y `postgres_disponible: true`.
- **Documentación API**: `http://localhost:8000/docs` devuelve HTTP 200.
- **Pruebas y build previos**: 92 pruebas backend aprobadas y build frontend correcto, registrados en CAMBIO2 del 26/09. No se repitieron en esta actuación de arranque sin cambios de código, ni se ejecutaron pruebas automatizadas contra `mediflow_dev`.
- **Límites**: se verificó disponibilidad HTTP y conexión a la base, no un recorrido funcional completo por la interfaz ni llamadas reales a IA/OCI. El indicador OCI de salud refleja configuración, no una prueba de acceso al servicio.

Los contenedores quedan en ejecución. No se realizó commit, push, publicación del PR ni merge.

## Corrección posterior del volumen de dependencias del frontend

Al abrir la interfaz se detectó `Failed to resolve import bootstrap/dist/css/bootstrap.min.css`. La respuesta HTTP 200 inicial no bastaba para verificar el renderizado: Vite servía el HTML, pero fallaba al resolver una importación del código.

`npm ls bootstrap --depth=0` dentro del contenedor no encontró el paquete. Una comprobación en un contenedor temporal de la imagen recién construida sí resolvió el CSS. La causa fue la reutilización del volumen anónimo antiguo de `/app/node_modules`, que ocultaba las dependencias instaladas en la imagen nueva.

Se recreó únicamente el frontend y su volumen de dependencias con:

```powershell
docker compose -f infrastructure/docker/docker-compose.dev.yml up -d --no-deps --force-recreate --renew-anon-volumes frontend
```

Este comando no recreó PostgreSQL ni modificó sus datos. No se cambió código de la aplicación. Tras la corrección se verificó en el navegador la pantalla de inicio de sesión de MediFlow y no se detectaron errores ni advertencias de consola en esa carga. Esta comprobación de renderizado complementa las comprobaciones HTTP anteriores; no se realizó un recorrido autenticado completo.

La verificación posterior dentro del contenedor confirmó `bootstrap@5.3.8` y `npm run build` con código 0, sin errores TypeScript, 78 módulos y compilación Vite en 2.42 segundos.
