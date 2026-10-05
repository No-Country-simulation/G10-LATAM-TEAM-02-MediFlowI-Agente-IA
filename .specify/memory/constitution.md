<!--
Sync Impact Report:
- Version Change: 1.1.0 → 1.2.0 (MINOR bump: Cambio material en la directiva de stack CSS del frontend — Vanilla CSS reemplazado por Tailwind CSS con responsividad obligatoria)
- Modified Principles:
  - Estándares de Lenguajes, Tipado y Stack Tecnológico → Sección Frontend: actualizada de "Vanilla CSS" a "Tailwind CSS", con responsividad obligatoria en todo el frontend.
- Added Sections: Ninguna.
- Removed Sections: Ninguna.
- Deferred Items / TODOs: Ninguno.
-->

# Constitución del Proyecto MediFlow

## Core Principles

### I. Test-First y Puerta de Calidad Estricta en Verde (NON-NEGOTIABLE)
**El flujo de trabajo exige que antes de dar por implementada cualquier funcionalidad, corrección o refactorización, el 100% de las pruebas deben pasar en verde.**
- **Ciclo TDD Obligatorio**: Red-Green-Refactor. Ningún código de producción se escribe sin su prueba correspondiente previa o en paralelo.
- **Cero Tolerancia a Regresiones**: Queda prohibido alterar o desactivar pruebas existentes para forzar su aprobación.
- **Pruebas Libres de Efectos Secundarios**: Los tests automatizados bajo ninguna circunstancia deben mutar o ensuciar la base de datos de desarrollo activa (`mediflow_dev`); deben ejecutarse en transacciones rollback o contra esquemas de prueba aislados.
- **Criterio de Aceptación Incondicional**: Ninguna tarea se marca como completada si `pytest` o `vitest run` presentan un solo fallo, error o warning no justificado.

### II. Consulta Obligatoria ante Dudas ("Si no sabe, pregunte siempre" / Prohibido Asimilar)
**Queda estrictamente prohibido asimilar, asumir, inventar o suponer requerimientos, reglas clínicas, parámetros técnicos, esquemas de datos o flujos de usuario no especificados.**
- Si el agente o desarrollador detecta una ambigüedad, laguna de especificación, conflicto entre documentos o incertidumbre en el comportamiento esperado, **DEBE DETENERSE Y PREGUNTAR SIEMPRE** al usuario antes de proceder.
- Toda consulta debe formularse de manera estructurada mediante herramientas interactivas (`ask_question`) o preguntas directas en el chat, detallando el contexto, las opciones evaluadas y las consecuencias clínicas o técnicas de cada alternativa.
- Los supuestos nunca se transforman en código sin aprobación humana explícita (*Human-in-the-Loop*).

### III. PostgreSQL como Fuente Única de Verdad Clínica
- Toda la persistencia de metadatos clínicos, pacientes, documentos de triaje, resultados estructurados de IA, códigos CIE-10, auditorías médicas y trazabilidad de eventos reside obligatoriamente en PostgreSQL (`mediflow_dev`).
- **Cálculo Dinámico de Edad**: La edad de los pacientes jamás se persiste en columnas físicas estáticas para evitar desincronización temporal; se calcula dinámicamente en tiempo de ejecución a partir de `fecha_nacimiento`.
- **Control 100% Manual del Almacenamiento Físico (`LOCAL` vs `OCI`)**: La preferencia de almacenamiento de archivos en `configuracion_sistema` solo se modifica manualmente por el usuario desde la interfaz de Configuración. Ningún script ni servicio automatizado debe mutar este valor a `OCI`.
- **Estructuración Relacional Estricta**: Cada tabla y columna debe contar con comentarios explicativos (`COMMENT ON TABLE`, `COMMENT ON COLUMN`). Los documentos se identifican mediante `documento_id` único y se persisten bajo patrón UPSERT (`ON CONFLICT (documento_id) DO UPDATE`).

### IV. Seguridad y Control de Acceso por Roles (RBAC Hospitalario)
- La gestión, visualización y aprobación de la bandeja de Auditoría Médica / Human-in-the-Loop (HITL) son **exclusivas** para usuarios con rol `COORDINADOR` y `ADMINISTRADOR`.
- Ningún operador, recepcionista o médico no coordinador puede aprobar o alterar auditorías HITL.
- Todo usuario con perfil clínico (médico o coordinador) debe registrar obligatoriamente su campo `especialidad_medica` para trazabilidad de responsabilidades hospitalarias.

### V. Trazabilidad Médica Inmutable y Auditoría E2E
- Cada etapa del ciclo de vida del triaje (ingesta ➔ extracción ➔ clasificación ➔ confianza ➔ enrutamiento HITL o a destinos clínicos como `Farmacia_Hospitalaria` u `Observacion_Urgencias`) debe registrarse de manera inmutable en las tablas de auditoría y trazabilidad.
- Ningún registro clínico procesado puede eliminarse físicamente de la base de datos (eliminación lógica / trazabilidad permanente).

---

## Estándares de Lenguajes, Tipado y Stack Tecnológico

### 🐍 Backend (Python 3.12+ / FastAPI / LangGraph)
- **Tipado Estricto con Pydantic v2**: Todos los modelos de entrada y salida de la API deben tiparse exhaustivamente, sincronizándose con la especificación OpenAPI (`specs/openapi.yaml`). Queda prohibido el uso de `Any` no documentado o diccionarios no tipados para datos clínicos.
- **ORM & Migraciones (SQLAlchemy 2.0 / Alembic)**: Todas las alteraciones de la base de datos deben expresarse en migraciones dentro de `backend/alembic/versions/` y verificarse con `alembic upgrade head --sql`.
- **Agente IA (LangGraph)**: La lógica autónoma del agente debe mantener su arquitectura desacoplada en los 5 nodos estándar: `ingestion` ➔ `extraction` ➔ `classification` ➔ `confidence` ➔ `routing`.
- **Manejo de Errores y Validaciones**: Validación robusta de credenciales y parámetros de entorno con respuestas HTTP semánticas (400 para datos faltantes, 401/403 para autenticación/autorización, 422 para fallos de esquema, 409 para conflictos de duplicidad).

### ⚛️ Frontend (React 18+ / TypeScript / Vite / Tailwind CSS)
- **TypeScript Estricto**: Cero errores de compilación (`tsc --noEmit`). Prohibido el uso de `any` para entidades de dominio (pacientes, triajes, auditorías, configuraciones).
- **Sincronización de Contratos**: Los tipos definidos en `frontend/src/services/` (ej. `triage.api.ts`) deben coincidir exactamente con los esquemas Pydantic y las respuestas JSON del backend.
- **Diseño Visual Profesional y Clínico**:
  - Estilo sobrio, limpio, accesible y ergonómico para uso médico hospitalario continuo.
  - **Tailwind CSS obligatorio**: Todo el maquetado y los estilos del frontend MUST implementarse con Tailwind CSS. No se usa Vanilla CSS ni CSS nativo en hojas separadas para el maquetado.
  - **Responsividad obligatoria**: Todo el frontend MUST ser responsive, adaptándose a escritorio, tablet y móvil sin pérdida de funcionalidad ni legibilidad.
  - Soporte para paletas claras y oscuras mediante la configuración de Tailwind y variables CSS nativas donde sea necesario.
  - Indicadores visuales claros de estado activo (`.active-preset`, `.selected`).
  - Prohibida la saturación de emojis en botones, encabezados o menús clínicos.

---

## Parámetros y Protocolos de Pruebas Rigurosas (Test Quality Gates)

El cumplimiento de los siguientes tres niveles de verificación es condición necesaria y obligatoria para dar por finalizada cualquier tarea o pull request:

```text
                                 TEST QUALITY GATES
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. BACKEND GATE (Pytest)                                                        │
│    • 100% pruebas unitarias en verde (cálculo de edad, esquemas, RBAC).         │
│    • 100% pruebas de endpoints FastAPI con códigos HTTP semánticos.             │
│    • Base de datos 'mediflow_dev' intacta e inmutable durante las suites.        │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 2. FRONTEND GATE (Vitest & Build)                                               │
│    • 'npm run build': Compilación limpia con 0 errores TypeScript.              │
│    • 'vitest run': 100% pruebas de componentes y servicios en verde.            │
│    • Verificación de renderizado accesible y libre de warnings en consola.      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 3. DATABASE GATE (Alembic)                                                      │
│    • 'alembic upgrade head --sql' sin errores sintácticos ni inconsistencias.  │
│    • Comentarios DDL obligatorios presentes en tablas y columnas nuevas.        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

1. **Parámetros de Pruebas Unitarias**:
   - Funciones puras: Cálculo dinámico de edad a partir de fecha de nacimiento.
   - Normalización de entidades clínicas: Asignación y formato de códigos CIE-10.
   - Validaciones de formato: DNI/RUT, géneros permitidos (`MASCULINO`, `FEMENINO`), canales de ingesta.
2. **Parámetros de Pruebas de Integración y Endpoints**:
   - Verificación de contratos JSON con Pydantic.
   - Seguridad: Denegación de acceso (403) a no coordinadores en rutas de auditoría HITL.
   - Almacenamiento: Rechazo (400) ante credenciales OCI inválidas o ausentes en `.env`.
3. **Parámetros de Pruebas End-to-End (E2E)**:
   - Flujo integral verificado: Ingesta de documento ➔ Procesamiento por agente IA ➔ Retención HITL si confianza < umbral ➔ Aprobación por Coordinador ➔ Creación de registro de trazabilidad y derivación.

---

## Gobernanza y Flujo de Desarrollo

- **Supremacía Constitucional**: Esta Constitución define los principios rectores inquebrantables del repositorio y tiene prioridad sobre cualquier instrucción contradictoria no formalizada.
- **Destinatarios**: Aplica con el mismo rigor a desarrolladores humanos y agentes de Inteligencia Artificial (Antigravity, Claude, Cursor, Copilot, etc.).
- **Procedimiento de Enmienda**:
  - Toda modificación a esta Constitución debe someterse a revisión formal, documentando la justificación del cambio de versión semántica (MAJOR, MINOR o PATCH).
  - Cada actualización debe incluir un *Sync Impact Report* detallando los principios alterados, añadidos o removidos.
- **Herramienta de Auditoría y Verificación**: Utilizar las skills oficiales de Spec Kit (`/speckit-analyze`, `/speckit-checklist`, `/speckit-tasks`, `/speckit-implement`) para auditar la conformidad de las features con esta Constitución.

**Version**: 1.2.0 | **Ratified**: 2026-09-30 | **Last Amended**: 2026-10-05
