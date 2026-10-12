# Technical Research: Resolución de Identidad y Conflictos DNI/HC en Pipeline

**Feature**: `004-patient-matcher-conflicts` (`[IA-02]`, Issue `#29`)  
**Date**: 2026-10-05  

---

## 1. Context & Problem Statement

En el flujo de triaje clínico de MediFlow, la IA extrae entidades a partir de documentos médicos digitalizados (PDFs, imágenes, órdenes médicas). Entre los datos extraídos se encuentran el `documento_identidad` (DNI) y la `historia_clinica` (HC).
Existe un riesgo crítico de seguridad médica si un documento contiene un DNI perteneciente al Paciente A y una Historia Clínica perteneciente al Paciente B (por ejemplo, errores de tipeo en admisión física, reutilización errónea de formatos o ambigüedad documental).

La IA nunca debe inferir la identidad mediante nombres cuando los identificadores estructurados discrepan. Debe existir un mecanismo riguroso que intercepte este escenario y lo derive inmediatamente a la `Cola_Revision_Ambigua` con requerimiento de auditoría médica humana.

---

## 2. Research Decisions & Alternatives

### Decisión 1: Módulo dedicado `patient_matcher.py` vs Lógica inline en `extraction.py`
- **Decisión**: Crear un módulo dedicado `backend/app/agent/patient_matcher.py` con la función `verificar_identidad_paciente(...)` que interactúa con `patient_repository.resolver_paciente_por_identificadores(...)`.
- **Razón**: Permite realizar pruebas unitarias aisladas con 100% de cobertura sin necesidad de instanciar o mockear todo el grafo LangGraph o el LLM. Mantiene el principio de responsabilidad única (SRP).
- **Alternativas consideradas**:
  - *Inline en `extraction.py`*: Mezclaba la llamada al LLM con la consulta a la base de datos relacional y dificultaba testear los casos bordes de coincidencia de forma independiente.

### Decisión 2: Ubicación de la Interceptación del Conflicto en el Pipeline
- **Decisión**: 
  1. En `extraction.py` (o post-extracción): Se ejecuta `verificar_identidad_paciente`. Si el estado es `"conflicto"`, se inyecta en `state.metadata`:
     - `"discrepancia_identidad_detectada": True`
     - `"motivo_ambiguedad": "conflicto_identidad_dni_hc"`
     - `"dni_detectado": dni`
     - `"hc_detectada": hc`
  2. En `routing.py`: Si `state.metadata.get("discrepancia_identidad_detectada")` es `True`, se sobreescribe el destino a `"Cola_Revision_Ambigua"`, asignando `requiere_auditoria_humana = True` y `status = "pendiente_auditoria"`.
- **Razón**: Respeta el flujo desacoplado de LangGraph donde `extraction` detecta/enriquece y `routing` toma la decisión final de despacho.
- **Alternativas consideradas**:
  - *Arista condicional para abortar antes de classification*: Descartado porque MediFlow necesita extraer y clasificar el tipo de documento para que el médico auditor tenga la vista completa del documento en la interfaz HITL.

### Decisión 3: Resiliencia ante Base de Datos No Disponible
- **Decisión**: Si `patient_repository.resolver_paciente_por_identificadores` lanza `DatabaseUnavailableError` o una excepción inesperada durante la ejecución del agente, el matcher captura la excepción, registra un log de advertencia y no aborta el flujo completo con crash no controlado, sino que marca la revisión preventiva.
- **Razón**: Garantiza la estabilidad del servicio cumpliendo la Regla de Oro.

---

## 3. Matriz de Comportamiento del Matcher

| DNI extraído | HC extraída | Coincidencia en BD | Estado Resultante | Destino en Routing | Requiere Auditoría |
|---|---|---|---|---|---|
| `12345678` (Pac A) | `HC-100` (Pac A) | Mismo paciente (ID A) | `asociado` | Según clasificación / score | False (si score ok) |
| `12345678` (Pac A) | `HC-200` (Pac B) | Pacientes distintos (ID A != ID B) | `conflicto` | `Cola_Revision_Ambigua` | True |
| `12345678` (Pac A) | `None` | Existe Paciente A por DNI | `asociado` | Según clasificación / score | False (si score ok) |
| `None` | `HC-100` (Pac A) | Existe Paciente A por HC | `asociado` | Según clasificación / score | False (si score ok) |
| `99999999` (No existe) | `HC-999` (No existe) | No existen en BD | `sin_coincidencia` | Según clasificación / score | Según score |
| `None` | `None` | Sin identificadores | `sin_coincidencia` | Según clasificación / score | Según score |
