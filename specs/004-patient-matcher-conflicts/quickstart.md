# Quickstart & Validation Guide: Resolución de Identidad y Conflictos DNI/HC

**Feature**: `004-patient-matcher-conflicts` (`[IA-02]`, Issue `#29`)  
**Date**: 2026-10-05  

---

## 1. Prerrequisitos

Entorno virtual activo en fish shell con dependencias instaladas:

```fish
source backend/.venv/bin/activate.fish
```

---

## 2. Ejecución de Pruebas Unitarias de Matching

Para validar el funcionamiento del módulo `patient_matcher.py` de forma aislada:

```fish
pytest backend/tests/test_patient_matcher.py -v
```

---

## 3. Ejecución de Pruebas de Integración del Pipeline de Triaje

Para validar que los conflictos de identidad se desvían correctamente a `Cola_Revision_Ambigua` en el flujo completo de LangGraph:

```fish
pytest backend/tests/test_agent_cases.py -v
```

---

## 4. Ejecución de la Suite Completa del Backend

Para asegurar el cumplimiento de la **Regla de Oro** (cero regresiones):

```fish
pytest backend/tests/ -v
```
