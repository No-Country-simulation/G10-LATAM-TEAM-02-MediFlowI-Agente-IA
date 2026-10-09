# Specification Quality Checklist: BD-04 — Datos semilla hospitalarios de desarrollo

**Purpose**: Validar completitud y calidad de la especificación antes de planificar.
**Created**: 2026-10-07
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] Sin diseño de implementación nuevo (lenguajes, frameworks o APIs); solo restricciones técnicas exigidas por el usuario y fuentes vigentes.
- [x] Centrada en valor para el desarrollador de pruebas y necesidades de datos ficticios reproducibles.
- [x] Escenarios y resultados expresados en lenguaje comprensible para interesados no técnicos.
- [x] Todas las secciones obligatorias completadas, preservando el orden de la plantilla activa.

## Requirement Completeness

- [x] No quedan marcadores NEEDS CLARIFICATION.
- [x] Requisitos verificables y sin ambigüedades de episodios, cuarta especialidad o colores.
- [x] Cuatro médicos con rol existente OPERADOR y especialidades distintas; no se crea MEDICO.
- [x] Cinco documentos definidos como registros ficticios en PostgreSQL, sin generación de archivos físicos.
- [x] Validación separada en pruebas automáticas con PostgreSQL aislado y ejecución manual posterior en desarrollo con Scalar.
- [x] Criterios de éxito medibles.
- [x] Criterios de éxito independientes de tecnologías y mecanismos de implementación.
- [x] Escenarios de aceptación definidos para las tres historias.
- [x] Casos límite identificados: carga parcial, colisiones, cumpleaños, indisponibilidad, salt y triggers.
- [x] Alcance limitado a Tarea 1.4 / BD-04, sin implementación ni carga en esta fase.
- [x] Dependencias y decisiones explícitas identificadas y respaldadas por fuentes.

## Feature Readiness

- [x] Requisitos funcionales con criterios de aceptación: FR-001–006 y FR-011 en historia 1; FR-007–008 en historia 2; FR-009–010 en historia 3; FR-012 en escenarios 6–8 de la historia 1; FR-013 en pruebas independientes, errores y restricciones de validación.
- [x] Escenarios cubren preparación, repetición y consulta segura del conjunto.
- [x] Resultados SC-001–008 cubren cantidad, no duplicación, rol, seguridad, edad, conservación, ausencia de archivos físicos y evidencias de los dos momentos de validación.
- [x] No se introduce diseño de implementación ajeno a restricciones expresas.

## Notes

- Validación documental completada tras recibir las tres respuestas: sin episodios, Traumatología, solo Urgente/Rutina/Ambiguo almacenados. Q3 incorpora la precisión del usuario: rojo, verde y amarillo/ámbar son únicamente la presentación visual existente de Urgente, Rutina y Ambiguo, respectivamente; Ambiguo sigue significando incertidumbre, no gravedad intermedia. No se resolvieron preguntas por suposición.
- La precisión de Q3 se refleja consistentemente en los escenarios 3 y 5 de la historia 1, FR-006, SC-005 y las decisiones confirmadas; se revisó `frontend/src/components/triage/PriorityBadge.tsx` sin modificarlo. No se amplía BD-04 a cambios de frontend, esquema o clasificación clínica.
- Decisiones adicionales incorporadas en escenarios, FR-003–004, entidades y criterios de éxito: los cuatro médicos tienen rol OPERADOR y especialidades distintas; los cinco documentos son registros ficticios de documentos_triaje en PostgreSQL, sin PDF, imágenes ni archivos físicos.
- Validación futura dividida explícitamente en dos momentos en User Scenarios & Testing y FR-013: pruebas automáticas con PostgreSQL real aislado, incluyendo dos ejecuciones consecutivas sin borrar ni revertir la primera antes de verificar la segunda; luego, una vez terminado y verificado el script, ejecución manual en mediflow_dev y comprobación visual en Scalar. Ninguna prueba automática usa desarrollo y ninguna carga manual se ejecuta durante esta especificación.
- Aceptación manual posterior en desarrollo explicitada en la historia 1: escenario 6 ejecuta manualmente el script terminado y verifica los 10 pacientes semilla y sus edades calculadas mediante `GET /api/v1/patients`, identificándolos dentro de `items` por sus números de documento y comparando edad con años cumplidos desde fecha de nacimiento; escenario 7 comprueba separadamente los 4 médicos con rol OPERADOR mediante `GET /api/v1/users`, usando una sesión ADMINISTRADOR existente para consultar, no para asignar ese rol a las cuentas semilla; escenario 8 comprueba los 5 registros documentales mediante cinco consultas `GET /api/v1/documents/{documento_id}` sin descargas físicas. Se distinguen los conteos semilla de totales generales y listas limitadas; no se atribuye al endpoint de pacientes la verificación de médicos o documentos.
- Esta revisión de `/speckit-specify` modifica únicamente `spec.md` y esta checklist. Los escenarios de Scalar se documentaron, no se ejecutaron; no se escribió código, no se cargó `mediflow_dev` y no se avanzó a `/speckit-plan`.
- Excepción explícita a la regla genérica «sin detalles de implementación»: se conservan la ruta del script del plan/backlog, `app.core.security.hash_password` solicitado por el usuario y campos/restricciones existentes como dependencias de compatibilidad. No se propone arquitectura ni código nuevo.
- La plantilla efectiva es `.specify/templates/spec-template.md`, resuelta mediante la función vigente `Resolve-Template`; numeración secuencial 005 sin sobrescribir las carpetas 001–004.
- No existe `.specify/extensions.yml`; no hay hooks previos o posteriores que ejecutar.
- Esta checklist valida el documento, no certifica la implementación ni la ejecución de las futuras pruebas de aceptación BD-04. La especificación permanece en borrador para revisión humana; no se inicia `/speckit-plan`, `/speckit-tasks` ni `/speckit-implement`.
- Verificación de referencia: `check-prerequisites.ps1 -Json -PathsOnly` resuelve la carpeta y el archivo de esta feature correctamente.
- Verificaciones del repositorio intentadas el 2026-10-07, bloqueadas por el entorno: `python -m pytest` no encuentra pytest; `python -m alembic upgrade head --sql` no encuentra un módulo ejecutable de Alembic; `npm test` (`vitest run`) no puede iniciar por ausencia de jsdom; `npm run build` falla por ausencia de tipos de `@testing-library/jest-dom`. No se afirma que las puertas de calidad estén en verde ni que BD-04 esté completada como implementación.
- Los comandos backend se intentaron sin conexión a desarrollo: DATABASE_URL vacía para pytest y URL ficticia de pruebas para generación SQL offline. No se ejecutó carga de datos ni migración online. No se instalaron dependencias o corrigieron archivos fuera del alcance documental.
