# Cierre de backlog clínico Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completar las brechas de OCR, texto extenso, asociación de pacientes, prioridad, seguridad y tipos del diagnóstico técnico.

**Architecture:** Mantener los cinco nodos de LangGraph; ingesta obtiene texto o marca un error explicable y extracción procesa bloques con consolidación. La asociación de paciente se resuelve contra DNI e historia clínica y queda auditada; las validaciones de API son la fuente única para los formularios.

**Tech Stack:** FastAPI, Pydantic, asyncpg/PostgreSQL, PyMuPDF, pytesseract opcional, React/Vite/TypeScript.

**Spec:** Imagen de backlog compartida por el usuario el 2026-09-25.

## Global Constraints

- PostgreSQL `mediflow_dev` es la única fuente de verdad; toda alteración de esquema usa Alembic con comentarios.
- Las pruebas no mutan `mediflow_dev`.
- No cambiar automáticamente el modo LOCAL/OCI.
- Verificar `pytest`, `npm run build` y `alembic upgrade head` antes de declarar terminado.

## Review Focus

- PDF escaneado sin texto embebido debe informar OCR no disponible, no simular texto.
- Texto de más de 4 000 caracteres debe incluir también el tramo final en la extracción.
- DNI e historia clínica que apunten a pacientes distintos deben quedar pendientes de auditoría, nunca asociarse en silencio.
- Una contraseña débil debe recibir 422 tanto al crear como al actualizar.
- Sexo omitido debe conservar `null`, no transformarse en `M`.

### Task 1: OCR y extracción incremental

**Files:** `backend/app/agent/nodes/ingestion.py`, `backend/app/agent/nodes/extraction.py`, `backend/tests/test_agent_cases.py`.

- [ ] Escribir pruebas de PDF sin capa de texto y de texto de más de 4 000 caracteres.
- [ ] Implementar OCR por página con `pytesseract` sólo cuando PyMuPDF no produzca texto; devolver un error explícito si el binario no existe.
- [ ] Implementar `dividir_texto_en_bloques(texto, max_chars=4000)` y consolidar resultados de cada bloque sin perder el final.
- [ ] Ejecutar pruebas del agente y confirmar verde.
- [ ] Commit: `feat: add OCR fallback and chunked extraction`.

### Task 2: Asociación híbrida y prioridad ambigua

**Files:** repositorio de pacientes, servicio de triaje, migración Alembic, pruebas de pacientes y triaje.

- [ ] Escribir pruebas para coincidencia única por DNI/HC y conflicto DNI/HC.
- [ ] Añadir resolución de paciente y registrar el identificador o requerir auditoría por conflicto.
- [ ] Modelar `Ambiguo` como cola/estado distinto de `Rutina` y probar que no comparten destino.
- [ ] Ejecutar pruebas y migración en entorno configurado.
- [ ] Commit: `feat: resolve patients and isolate ambiguous triage`.

### Task 3: Catálogos y privacidad de pacientes

**Files:** nodo de clasificación, esquemas de pacientes, repositorio, formularios React/TypeScript, pruebas.

- [ ] Escribir prueba de sexo ausente y tipos clínicos ampliados.
- [ ] Eliminar defaults `M` de API, repositorio y formularios; preservar valor desconocido como `null`.
- [ ] Ampliar catálogo de tipos clínicos usado por clasificación y UI.
- [ ] Ejecutar pytest y `npm run build`.
- [ ] Commit: `feat: expand clinical catalog and optional patient sex`.

### Task 4: Contraseña y migración JSX

**Files:** API de usuarios, pruebas de auth, formularios de usuarios y archivos `.jsx` del frontend.

- [ ] Escribir prueba que rechace contraseñas sin longitud, mayúscula, minúscula, número y símbolo.
- [ ] Centralizar la validación Pydantic para creación y actualización, con mínimo 12 caracteres.
- [ ] Migrar los componentes JSX restantes a TSX y tipar sus props/datos API.
- [ ] Ejecutar pytest y compilación Vite.
- [ ] Commit: `feat: strengthen passwords and migrate JSX views`.

## Self-review

- Cada punto de la imagen corresponde a una tarea; la trazabilidad del usuario y el historial ya se resolvieron en `07abaf1`.
- Las pruebas de foco están asignadas a las tareas dueñas.
- Las migraciones sólo son necesarias en Task 2 si se agrega la relación de paciente.
