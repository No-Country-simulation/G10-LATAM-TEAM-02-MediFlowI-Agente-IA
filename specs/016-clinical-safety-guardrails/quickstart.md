# Quickstart & Guía de Validación: Guardrails de Seguridad Clínica

**Feature**: [016-clinical-safety-guardrails](file:///home/wigsdev/GitHub/mediflow/specs/016-clinical-safety-guardrails/spec.md)  
**Date**: 2026-10-20  

---

## 🎯 Escenarios de Validación End-to-End

Esta guía detalla los 3 escenarios automatizados que acreditan el blindaje clínico del sistema frente a entradas adversarias y alucinaciones del modelo.

---

### Escenario 1: Documento Fuera de Dominio (Out-of-Domain Gate)
- **Entrada**: Documento no clínico (ej. afiche de concierto, revista o folleto publicitario clasificado como `"Otro"`).
- **Comportamiento esperado**:
  - `decision_enrutamiento.destino_principal == "Cola_Revision_Ambigua"`.
  - `decision_enrutamiento.requiere_auditoria_humana == True`.
  - `status == "pendiente_auditoria"`.
  - Prohibido terminantemente: `Cola_Rutina` o `Cola_Emergencia_Medica`.
  - Metadata: `"fuera_de_dominio_clinico": True`.

---

### Escenario 2: PDF Asimétrico Multipágina (Digital + Imagen Anexa)
- **Entrada**: PDF de 2 páginas (Página 1: texto digital de control rutinario; Página 2: imagen escaneada con orden de urgencia para sospecha de infarto o receta médica).
- **Comportamiento esperado**:
  - Ingesta audita página 1 y extrae texto vectorial.
  - Ingesta detecta que la página 2 es visual y la rasteriza en memoria (< 350 KB).
  - El resultado consolidado contiene la información clínica de ambos folios.
  - La urgencia o receta de la página 2 es evaluada e integrada en la clasificación final.
  - `documento_base64` se libera a `None` para proteger la memoria.

---

### Escenario 3: Validación Cruzada y Red Flags (TEP / Infarto vs Rutina)
- **Entrada**: Hallazgos o diagnóstico con patología de riesgo vital (ej. "Tromboembolismo pulmonar masivo" o código CIE-10 `I26.9`) pero con una clasificación de prioridad simulada como `"Rutina"`.
- **Comportamiento esperado**:
  - `score_final == 0.0` (penalización estricta por discordancia clínica).
  - `decision_enrutamiento.destino_principal == "Cola_Revision_Ambigua"`.
  - `decision_enrutamiento.requiere_auditoria_humana == True`.
  - `status == "pendiente_auditoria"`.
  - Metadata: `"discordancia_critica_red_flags": True`, `"red_flag_detectada": "tromboembolismo pulmonar"`.

---

## 🧪 Comandos de Ejecución de Pruebas

Para validar empíricamente la suite de guardrails una vez implementada:

```bash
cd backend
.venv/bin/pytest tests/test_clinical_guardrails.py -v
```

Para verificar que no existen regresiones con Pipeline Fusion (Spec 015):

```bash
cd backend
.venv/bin/pytest tests/test_clinical_guardrails.py tests/test_pipeline_fusion.py -v
```

---

## 📋 Lista de Comprobación de Aceptación (Quality Gate)

- [ ] Todos los tests de `test_clinical_guardrails.py` pasan al 100% en verde.
- [ ] La base de datos `mediflow_dev` se mantiene intacta durante las pruebas.
- [ ] Ningún documento clasificado como "Otro" se enruta a `Cola_Rutina`.
- [ ] Ninguna página escaneada secundaria en un PDF se descarta sin analizar.
- [ ] Ningún caso con Red Flag clasificado como Rutina obtiene confianza superior a 0.0.
