# Constitución del Proyecto MediFlow
<!-- Versión Oficial del Ecosistema Hospitalario de Agente IA MediFlow -->

## Principios Fundamentales (Core Principles)

### I. Test-First y Puerta de Calidad Estricta en Verde (NON-NEGOTIABLE)
**El flujo de trabajo exige que antes de dar por implementada cualquier funcionalidad o cambio, TODAS las pruebas deben pasar al 100% en verde.**
- El ciclo Red-Green-Refactor es obligatorio.
- Antes de entregar cualquier funcionalidad o corrección, se deben ejecutar y verificar empíricamente tanto las pruebas unitarias como las pruebas End-to-End (E2E) en backend (`pytest`) y frontend (`vitest run` y `npm run build`).
- Cero tolerancia a regresiones o pruebas salteadas ("skipped" sin justificación formal).
- Si una prueba falla, el código NO está listo para producción ni para revisión.

### II. Consulta Obligatoria ante Dudas o Ambigüedades ("Si no sabe, pregunte siempre")
**Queda terminantemente prohibido asumir, inventar o tomar decisiones arbitrarias a ciegas cuando un requisito, regla clínica, parámetro técnico o diseño no esté completamente claro.**
- Si el agente o desarrollador encuentra un caso de uso no especificado, una discrepancia en la base de datos o cualquier incertidumbre sobre el comportamiento esperado, **DEBE PREGUNTAR SIEMPRE** al usuario antes de proceder.
- Se debe emplear la herramienta de preguntas directas (`ask_question` o comunicación explícita) exponiendo las opciones consideradas y su impacto.

### III. PostgreSQL como Fuente Única de Verdad Clínica
- Toda la persistencia clínica (pacientes, documentos de triaje, auditorías HITL, trazabilidad de eventos y episodios clínicos) reside en PostgreSQL bajo esquemas relacionales estrictos y versionados mediante migraciones de Alembic.
- La edad de los pacientes nunca se persiste como columna física estática para evitar desincronizaciones en el tiempo; se calcula dinámicamente en tiempo de ejecución a partir de `fecha_nacimiento`.
- El control de almacenamiento físico de archivos (LOCAL vs OCI) es 100% manual y se rige por la configuración del sistema.

### IV. Seguridad y Control de Acceso por Roles (RBAC Hospitalario)
- La pantalla y operaciones de Auditoría Médica / Human-in-the-Loop (HITL) son **exclusivas** para usuarios con rol `COORDINADOR` y `ADMINISTRADOR`. Ningún operador, recepcionista o médico no coordinador puede aprobar o alterar auditorías HITL.
- Todo usuario médico y coordinador debe contar con su campo `especialidad_medica` para la asignación y trazabilidad de responsabilidades clínicas.

### V. Trazabilidad Médica y Auditoría E2E
- Cada evento dentro del ciclo de vida del triaje (ingesta, extracción, clasificación por agente IA, revisión HITL, enrutamiento a destinos como `Farmacia_Hospitalaria` o `Observacion_Urgencias`, y derivación a episodios clínicos) debe quedar registrado de manera inmutable en las tablas de auditoría y trazabilidad.

---

## Estándares de Prueba y Verificación

1. **Pruebas Unitarias**:
   - Cobertura de funciones de cálculo (edad dinámica, formateadores de confianza, mapeo de diagnósticos CIE-10).
   - Validación de restricciones de entrada (roles válidos, género `FEMENINO` / `MASCULINO`, canales de origen).
2. **Pruebas de Integración y Contrato**:
   - Pruebas de endpoints FastAPI asegurando códigos de estado HTTP correctos (200, 201, 400, 403, 404, 409, 422).
   - Verificación de migraciones offline con Alembic (`alembic upgrade head --sql`).
3. **Pruebas End-to-End (E2E)**:
   - Flujo de triaje completo: Registro de Paciente → Ingesta de Documento → Evaluación IA → Retención HITL → Decisión de Coordinador → Generación de Episodio Clínico y Trazabilidad.

---

## Gobernanza y Reglas de Desarrollo

- Esta Constitución rige para todos los desarrolladores humanos y agentes de Inteligencia Artificial (Antigravity, Claude, Copilot, etc.).
- Ningún Pull Request o tarea se considerará aprobada sin el cumplimiento estricto del Principio I (100% pruebas en verde) y el Principio II (consulta oportuna ante cualquier duda).

**Version**: 1.0.0 | **Ratified**: 2026-09-30 | **Last Amended**: 2026-09-30
