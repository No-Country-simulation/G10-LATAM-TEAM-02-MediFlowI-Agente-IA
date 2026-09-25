# Integridad documental y clasificación clínica

## Objetivo

Procesar documentos clínicos extensos sin perder información, asociarlos con seguridad a pacientes registrados y dejar evidencia de cada fase del triaje.

## Clasificación incremental

La clasificación reutilizará bloques de 4 000 caracteres. Cada bloque producirá una clasificación y la consolidación seguirá estas reglas: `Urgente` prevalece; una clasificación `Ambiguo`, resultados incompatibles o baja confianza producen `Ambiguo`; `Rutina` sólo se asigna cuando no existe ninguna señal anterior. Así se elimina `texto[:3000]` sin ampliar el contrato HTTP.

## Asociación de paciente

El texto extraído aporta DNI y/o historia clínica. La resolución consulta coincidencias exactas en `pacientes`:

- Una coincidencia única por DNI o HC asocia `documentos_triaje.paciente_id`.
- DNI y HC que identifican al mismo paciente se asocian.
- Identificadores contradictorios o sin una coincidencia única no asocian automáticamente; el documento permanece en `Cola_Revision_Ambigua`.

La asociación nunca crea pacientes ni infiere identidad por nombre.

## Historial funcional

`historial_documento` registrará: `OCR_COMPLETADO` o `OCR_FALLIDO`, `EXTRACCION_IA_COMPLETADA`, `CLASIFICACION_COMPLETADA`, `ENRUTAMIENTO_COMPLETADO`, `PACIENTE_ASOCIADO` y `CONFLICTO_PACIENTE`. Cada evento conserva el estado anterior/nuevo y metadatos mínimos de la operación; no almacena texto clínico completo.

## Catálogo clínico

El catálogo permitido por clasificación y presentado en la interfaz incorporará: informe por imágenes, laboratorio, receta, informe quirúrgico, orden de procedimiento, evolución clínica, interconsulta, alta/epicrisis, consentimiento informado, anatomopatología, electrocardiograma y nota de enfermería, además de `Otro`.

## Seguridad y validación

PostgreSQL conserva la fuente de verdad. Las pruebas usan repositorios en memoria o mocks y no modifican `mediflow_dev`. Una migración Alembic agregará solamente los campos o comentarios necesarios, con `COMMENT ON` para todo elemento nuevo.

## Criterios de aceptación

- Un hallazgo crítico situado después del carácter 3 000 puede producir prioridad `Urgente`.
- Un conflicto DNI/HC no asocia paciente y queda trazable.
- Cada fase del documento queda visible en el historial.
- El frontend muestra los nuevos tipos clínicos sin tipos TypeScript inconsistentes.
