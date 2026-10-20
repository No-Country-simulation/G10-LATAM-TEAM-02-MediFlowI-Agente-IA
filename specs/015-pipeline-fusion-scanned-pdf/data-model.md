# Data Model & Diagrama de Secuencia: Pipeline Fusion para PDFs

**Feature**: `015-pipeline-fusion-scanned-pdf`  
**Referencia**: Tarea 2.9 ([IA-09]) / PR #77  
**Date**: 2026-10-20  

---

## 1. Diagrama de Flujo y Estados en LangGraph

```mermaid
flowchart TD
    Start([Documento PDF en Ingestion]) --> PyMuPDF[PyMuPDF: _extraer_texto_pdf_pymupdf]
    
    PyMuPDF --> CheckLen{len(texto_digital) >= 50 ?}
    
    CheckLen -->|SÍ: Texto Suficiente| TextFlow[Flujo Digital Directo: TEXT_EXTRACTION]
    TextFlow --> DigitalReturn[Retorna texto_extraido y documento_base64 = None]
    DigitalReturn --> StandardExt[extraction.py: LLM estándar o reglas locales]
    StandardExt --> StandardClass[classification.py: LLM estándar]
    
    CheckLen -->|NO: Escaneado / Membrete| RasterFlow[Flujo Pipeline Fusion en Memoria]
    RasterFlow --> Rasterize[Rasterizar página 1 a JPEG en memoria BytesIO]
    Rasterize --> PillowOpt[image_optimizer.py: max 1280px / JPEG 80 / < 350 KB]
    PillowOpt --> VisionCall[Gemini Vision: ainvoke _PROMPT_VISION_FUSION]
    
    VisionCall --> ValidJSON{¿JSON válido y campos presentes?}
    
    ValidJSON -->|SÍ| SetContext[ContextoTriaje.fusion_resultado = fusion]
    SetContext --> FusionReturn[Retorna texto_extraido y documento_base64 = None]
    FusionReturn --> ShortCircuitExt[extraction.py: Cortocircuito con datos de ContextoTriaje]
    ShortCircuitExt --> ShortCircuitClass[classification.py: Cortocircuito con clasificación precalculada]
    
    ValidJSON -->|NO / Error| AuditFallback[Retorna FALLBACK_AUDIT y documento_base64 = None]
    AuditFallback --> DirectToHITL[confidence.py y routing.py: Derivación directa a HITL]
    
    StandardClass --> Confidence[confidence.py: Score de confianza y reglas CIE-10]
    ShortCircuitClass --> Confidence
    DirectToHITL --> Confidence
    
    Confidence --> Routing[routing.py: Destino clínico o Cola_Auditoria_Humana]
    Routing --> End([Estado Final Persistido en PostgreSQL])
```

---

## 2. Entidades de Datos y Contratos de Estado

### A. Contexto de Ejecución Efímero (`ContextoTriaje`)
Ubicación: `backend/app/agent/fusion.py`  
No se persiste en PostgreSQL ni se expone en la API REST pública; vive exclusivamente en memoria durante la ejecución de los 5 nodos:

```python
class ContextoTriaje:
    llm_service: LLMService | None
    fusion_intentada: bool = False
    fusion_resultado: ResultadoFusionVision | None = None
```

### B. Modelo Estructurado de Fusión (`ResultadoFusionVision`)
Ubicación: `backend/app/agent/fusion.py` (sincronizado con `specs/openapi.yaml`):

```python
class ClasificacionFusionVision(BaseModel):
    prioridad: str               # "Urgente" | "Rutina" | "Ambiguo"
    especialidad: str | None     # Especialidad clínica sugerida
    justificacion: str           # Razonamiento clínico del pase único

class ResultadoFusionVision(BaseModel):
    texto_extraido: str          # Transcripción del manuscrito o documento
    datos_extraidos: dict        # Entidades clínicas (paciente, diagnóstico, cie10, medicamentos)
    clasificacion: ClasificacionFusionVision
```

### C. Transición en `AgentState`
- **Entrada a `node_ingestion`**:
  - `state.tipo_archivo`: `"PDF"`
  - `state.documento_base64`: string Base64 del archivo PDF completo.
- **Salida de `node_ingestion`**:
  - `documento_base64`: `None` *(saneamiento de memoria obligatorio)*.
  - `metodo_extraccion`: `"TEXT_EXTRACTION"` (si digital) o `"MULTIMODAL_VISION"` (si escaneado fusionado) o `"FALLBACK_AUDIT"` (si error).
  - `texto_extraido`: cadena de texto extraída o transcrita.
  - `nodos_ejecutados`: `["ingestion"]`.
