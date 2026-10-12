# Quickstart & Verification Guide: Calibrador de Score de Confianza Multimodal y Retención HITL

**Feature**: `006-confidence-score`  (`[IA-04]`, Issue `#31`)
**Date**: 2026-10-12  

---

## 1. Prerrequisitos

- Entorno de desarrollo con Python 3.12+ y `uv` sincronizado:
  ```bash
  cd backend
  uv sync --all-extras
  ```

---

## 2. Escenarios de Validación Rápida

### Escenario A: Calibración con Score Óptimo (≥ 0.75) sin Retención
Documento nítido con paciente, diagnóstico y signos vitales:
- **Esperado**: `score_confianza_clasificacion >= 0.75`.
- **Destino**: `Cola_Rutina` o `Farmacia_Hospitalaria` (según tipo de documento).
- **Auditoría**: `requiere_auditoria_humana = False`.

### Escenario B: Calibración con Score Degradado (< 0.75) con Retención HITL Obligatoria
Documento incompleto o de baja calidad textual (< 20 caracteres) o con score base bajo que da como resultado `0.74`:
- **Esperado**: `score_confianza_clasificacion < 0.75`.
- **Destino**: `Cola_Auditoria_Humana`.
- **Auditoría**: `requiere_auditoria_humana = True`.
- **Estado**: `status = "pendiente_auditoria"`.

### Escenario C: Precedencia de Seguridad Clínica (Urgencia)
Documento con score bajo (ej. 0.60) pero clasificado con nivel `Urgente` (grave):
- **Esperado**: Destino a `Cola_Emergencia_Medica` con alerta inmediata prioritaria sobre la retención general.

---

## 3. Comandos de Validación Automatizada

```bash
# 1. Ejecución de pruebas unitarias específicas de confianza y enrutamiento
uv run pytest tests/test_confidence_calibration.py tests/test_destinos_triaje_unit.py -v

# 2. Verificación global de 0 regresiones en todo el backend (Regla de Oro)
uv run pytest backend/tests/ -v
```
