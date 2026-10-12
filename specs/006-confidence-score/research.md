# Research & Technical Decisions: Calibrador de Score de Confianza Multimodal y Retención HITL

**Feature**: `006-confidence-score`  (`[IA-04]`, Issue `#31`) 
**Date**: 2026-10-12  
**Status**: Completed  

---

## 1. Ponderación Matemática del Score Multimodal en `confidence.py`

### Contexto
El nodo `confidence` debe consolidar múltiples dimensiones de calidad extraídas del documento para calcular un score unificado delimitado estrictamente en `[0.0, 1.0]`.

### Decisión
Estructurar el cálculo mediante la suma balanceada de un `score_base` (proveniente de la clasificación) más un vector de ajustes granulares clasificados en tres dimensiones:

1. **Dimensión de Calidad Textual y Extracción (OCR / Texto)**:
   - Texto con extensión suficiente (> 100 caracteres): `+0.05`.
   - Texto muy corto (< 20 caracteres) o vacío: `-0.30`.
   - Presencia de error registrado en nodos anteriores: `-0.20`.

2. **Dimensión de Completitud Clínica**:
   - Identificación unívoca del paciente (`paciente.nombre` presente): `+0.10`.
   - Diagnóstico principal identificado: `+0.10`.
   - Código CIE-10 extraído/validado: `+0.05`.
   - Signos vitales o mediciones clínicas presentes en hallazgos: `+0.05`.
   - Hallazgos clínicos clave identificados: `+0.05`.
   - Ausencia total de diagnóstico: `-0.15`.

3. **Normalización y Acotamiento Estricto**:
   - `score_final = max(0.0, min(1.0, round(score_base + ajuste_total, 3)))`.

### Rationale
Garantiza granularidad matemática, predictibilidad y consistencia con las reglas preexistentes de MediFlow sin oscilaciones arbitrarias ni valores fuera de rango.

### Alternativas Consideradas
- **Promedio ponderado rígido (pesos fijos 0-1)**: Descartado porque no permite penalizaciones asimétricas cuando fallan condiciones críticas de seguridad (ej. texto vacío).

---

## 2. Calibración del Umbral de Retención HITL (< 0.75) e Integración con `routing.py`

### Contexto
El Issue #31 exige que cualquier caso con `score < 0.75` sea retenido obligatoriamente para revisión humana (`Cola_Auditoria_Humana` con `requiere_auditoria_humana = True` y `status = "pendiente_auditoria"`). El nodo `routing.py` anteriormente utilizaba un umbral de `0.50`.

### Decisión
1. **Actualizar el umbral de corte** en `backend/app/agent/nodes/routing.py` de `0.50` a `0.75`:
   ```python
   UMBRAL_CONFIANZA_HITL = 0.75
   if score < UMBRAL_CONFIANZA_HITL:
       return (
           "Cola_Auditoria_Humana",
           f"Score de confianza bajo ({score:.2f} < {UMBRAL_CONFIANZA_HITL:.2f}). Requiere revisión del Coordinador Médico.",
           None,
           True,
       )
   ```
2. **Jerarquía y Precedencia Clínica Inquebrantable**:
   - **Precedencia 1**: Discrepancia de Identidad detectada (Issue #29) ➔ `Cola_Revision_Ambigua` (HITL = True).
   - **Precedencia 2**: Nivel de triage "Ambiguo" ➔ `Cola_Revision_Ambigua` (HITL = True).
   - **Precedencia 3**: Nivel de triage "Urgente" ➔ `Cola_Emergencia_Medica` (Alerta inmediata).
   - **Precedencia 4**: `score < 0.75` ➔ `Cola_Auditoria_Humana` (HITL = True).
   - **Precedencia 5**: Recetas o Farmacoterapia (Issue #28) ➔ `Farmacia_Hospitalaria`.
   - **Precedencia 6**: Casos regulares sin banderas ➔ `Cola_Rutina`.

### Rationale
Respeta de forma estricta los principios de seguridad clínica: una emergencia médica o una discrepancia de identidad jamás deben degradarse a una cola general de auditoría. A la vez, cualquier caso rutinario o farmacológico con baja certeza de extracción es oportunamente retenido antes de su dispensación o atención.

---

## 3. Trazabilidad de Factores en `state.metadata`

### Contexto
El Principio V de la Constitución de MediFlow exige trazabilidad médica inmutable y explicabilidad para auditores y coordinadores médicos.

### Decisión
El nodo `confidence` registrará en `state.metadata["factores_confianza"]` un diccionario estructurado:
```python
{
    "score_base": score_base,
    "ajuste_texto": ajuste_texto,
    "ajuste_completitud": ajuste_completitud,
    "penalizaciones": penalizaciones,
    "score_final": score_final,
    "umbral_minimo_requerido": 0.75,
    "retenido_por_confianza": score_final < 0.75,
}
```

### Rationale
Permite a la interfaz del frontend y al visor de auditoría clínica mostrar exactamente qué variables provocaron que el documento fuera retenido.
