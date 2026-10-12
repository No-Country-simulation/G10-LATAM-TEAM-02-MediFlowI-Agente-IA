# Interface Contract: Calibración de Confianza y Enrutamiento HITL

**Feature**: `006-confidence-score`   (`[IA-04]`, Issue `#31`)
**Date**: 2026-10-12  

---

## 1. Contrato del Nodo `confidence`

### Función: `node_confidence(state: AgentState) -> dict`

#### Entrada (Consumida desde `AgentState`):
- `state.clasificacion.score_confianza_clasificacion` (`float`): Score base provisto por la clasificación del LLM (ej. 0.70).
- `state.datos_extraidos` (`DatosClinicosExtraidos`): Entidades clínicas extraídas (paciente, diagnóstico_principal, signos_vitales, cie10_sugerido, hallazgos_clave).
- `state.texto_extraido` o `state.documento_texto` (`str`): Texto plano obtenido tras la extracción u OCR.
- `state.error_mensaje` (`str | None`): Errores acumulados en nodos precedentes.

#### Salida (`dict` de actualización de estado):
```python
{
    "clasificacion": ClasificacionState(
        tipo_documento=state.clasificacion.tipo_documento,
        especialidad=state.clasificacion.especialidad,
        nivel_prioridad=state.clasificacion.nivel_prioridad,
        score_confianza_clasificacion=round(score_final, 3),  # Float acotado [0.0, 1.0]
    ),
    "metadata": {
        **state.metadata,
        "factores_confianza": {
            "score_base": float,
            "ajuste_texto": float,
            "ajuste_completitud": float,
            "penalizaciones": float,
            "score_final": float,
            "umbral_minimo_requerido": 0.75,
            "retenido_por_confianza": bool,
        }
    },
    "nodos_ejecutados": state.nodos_ejecutados + ["confidence"],
}
```

---

## 2. Contrato de Decisión de Enrutamiento en `routing.py`

### Función: `_calcular_destino(...)`

#### Parámetro de Confianza:
- `score` (`float`): Score calibrado provisto por `node_confidence`.

#### Reglas Contractuales de Decisión:

| Condición Clínica / Señal | Destino Principal | Requiere Auditoría | Notificación | Justificación |
|---|---|---|---|---|
| Discrepancia de Identidad DNI/HC | `Cola_Revision_Ambigua` | `True` | `None` | Discrepancia de identidad detectada. |
| Nivel de prioridad `"Ambiguo"` | `Cola_Revision_Ambigua` | `True` | `None` | Documento ambiguo. Requiere revisión. |
| Nivel de prioridad `"Urgente"` | `Cola_Emergencia_Medica` | `False` | `Alerta_Guardia_Medica` | Hallazgo de alta gravedad detectado. |
| **`score < 0.75`** | **`Cola_Auditoria_Humana`** | **`True`** | **`None`** | **Score de confianza bajo (< 0.75). Requiere revisión del Coordinador.** |
| `score >= 0.75` + Receta Médica | `Farmacia_Hospitalaria` | `False` (o `True` si narcótico) | `None` | Derivación a farmacia para dispensación. |
| `score >= 0.75` + Nivel `"Rutina"` | `Cola_Rutina` | `False` | `None` | Triaje de rutina verificado. |
