# Implementation Plan: Guardrails de Seguridad Clínica (Filtro Fuera de Dominio, PDFs Asimétricos y Validación Cruzada de Coherencia)

**Branch**: `dev-wilmer-gulcochia` | **Date**: 2026-10-20 | **Spec**: [specs/016-clinical-safety-guardrails/spec.md](file:///home/wigsdev/GitHub/mediflow/specs/016-clinical-safety-guardrails/spec.md)

**Input**: Feature specification from `/specs/016-clinical-safety-guardrails/spec.md`

---

## Summary

Implementar tres guardrails de seguridad clínica deterministas dentro de la arquitectura LangGraph de MediFlow para blindar el triaje contra fallos de dominio, pérdida de información en PDFs multipágina asimétricos y alucinaciones críticas de subestimación de riesgo vital:
1. **Filtro Fuera de Dominio en `routing.py`**: Interceptar documentos clasificados como "No_Clinico", "Otro" o "Desconocido", prohibiendo su ingreso a colas de rutina o emergencia y reteniéndolos en `Cola_Revision_Ambigua` con `status = "pendiente_auditoria"` y `requiere_auditoria_humana = true`.
2. **Inspección de PDFs Asimétricos Página por Página en `ingestion.py`**: Auditar folios individuales de PDFs; si una página carece de texto digital (< 50 caracteres) o incluye imágenes incrustadas de órdenes/urgencias, rasterizar y procesar visualmente hasta 3 páginas clínicas en memoria, combinando su contenido con las páginas digitales.
3. **Guardrail de Coherencia Semántica (Matriz de Red Flags) en `confidence.py`**: Detectar afecciones de riesgo vital (TEP, IAM, Shock, ACV) mediante catálogo determinista; si la prioridad asignada es "Rutina", anular la confianza a `0.0` y forzar derivación a auditoría médica prioritaria en `Cola_Revision_Ambigua`.

---

## Technical Context

**Language/Version**: Python 3.12+ (Backend)  
**Primary Dependencies**: LangGraph, FastAPI, PyMuPDF (fitz), Pillow, Pydantic v2, Google GenAI SDK  
**Storage**: PostgreSQL (`mediflow_dev`) para trazabilidad y metadatos; almacenamiento de archivos en modo `LOCAL`  
**Testing**: pytest (100% pruebas unitarias y de integración pasando en verde)  
**Target Platform**: Linux / Docker  
**Project Type**: Healthcare Clinical Decision Support / Autonomous Triage Agent  
**Performance Goals**: Sobrecarga total de los guardrails < 100 ms; latencia de triaje preservada dentro del SLA (< 8.0s)  
**Constraints**:
- La base de datos `mediflow_dev` no debe mutar durante las pruebas automatizadas.
- 100% compatibilidad con Pipeline Fusion (Spec 015) y liberación estricta de `documento_base64 = None` en LangGraph.
- Las decisiones de los guardrails deterministas tienen prevalencia absoluta sobre las salidas probabilísticas del LLM.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio Constitucional | Estado | Justificación / Cumplimiento |
|---|:---:|---|
| **I. Test-First y Puerta de Calidad Estricta** | ✅ PASS | Se diseñarán suites de pruebas unitarias en `test_clinical_guardrails.py` cubriendo los 3 casos adversarios antes de finalizar la implementación. |
| **II. Consulta Obligatoria ("Pregunte siempre")** | ✅ PASS | Las 3 dudas clínicas y operacionales clave fueron formuladas y aprobadas por el usuario en `/speckit-clarify` (Sesión 2026-10-20). |
| **III. PostgreSQL como Fuente Única de Verdad** | ✅ PASS | Todo motivo de retención (`fuera_de_dominio_clinico`, `discordancia_critica_red_flags`) se almacena en la metadata persistida en PostgreSQL. Modo `LOCAL` intacto. |
| **IV. RBAC Hospitalario y Gobernanza HITL** | ✅ PASS | Los documentos retenidos por los guardrails solo son auditables y descartables por usuarios con rol `COORDINADOR` y `ADMINISTRADOR`. |
| **V. Trazabilidad Médica Inmutable** | ✅ PASS | Cada intervención de los guardrails genera un evento inmutable en `trazabilidad_eventos`. |

---

## Project Structure

### Documentation (this feature)

```text
specs/016-clinical-safety-guardrails/
├── spec.md              # Especificación funcional con clarificaciones aprobadas
├── plan.md              # Este plan de implementación arquitectónica
├── research.md          # Fase 0: Decisiones, catálogo Red Flags y patrones
├── data-model.md        # Fase 1: Esquemas de datos, modelos y metadatos
├── quickstart.md        # Fase 1: Guía de validación y escenarios de prueba
├── contracts/           # Fase 1: Contrato de guardrails y esquemas JSON
│   └── guardrails.contract.json
├── checklists/          # Listas de verificación de calidad de la especificación
│   └── requirements.md
└── tasks.md             # Fase 2: Tareas atómicas ejecutables guiadas por TDD
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── agent/
│   │   ├── clinical_guardrails.py     # NUEVO: Catálogo Red Flags y motor de validación cruzada
│   │   ├── nodes/
│   │   │   ├── ingestion.py           # MODIFICADO: Inspección página por página de PDFs asimétricos
│   │   │   ├── confidence.py          # MODIFICADO: Guardrail de coherencia y anulación a 0.0 de confianza
│   │   │   └── routing.py             # MODIFICADO: Filtro fuera de dominio y derivación forzada a HITL
│   │   └── state.py                   # MODIFICADO: Metadatos tipados para motivos de guardrails
│   └── services/
│       └── image_optimizer.py         # MANTENIDO: Optimización adaptativa de folios rasterizados
└── tests/
    └── test_clinical_guardrails.py    # NUEVO: Suite integral con 100% de cobertura de los 3 guardrails
```

**Structure Decision**: Se encapsulan las reglas deterministas de *Red Flags* y la lógica de validación semántica en un módulo cohesivo `backend/app/agent/clinical_guardrails.py`, inyectando las comprobaciones en los nodos estándar del grafo LangGraph (`ingestion` -> `confidence` -> `routing`) sin alterar el contrato público de la API ni la estructura de 5 nodos.

---

## Complexity Tracking

> Ninguna violación constitucional detectada. La implementación aprovecha la arquitectura existente de LangGraph y PyMuPDF sin agregar dependencias externas ni alterar el esquema relacional.
