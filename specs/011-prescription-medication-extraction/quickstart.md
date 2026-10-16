# Quickstart & Verification Guide: Extracción de Medicamentos Prescritos

**Feature**: `011-prescription-medication-extraction`  
**Prerrequisitos**: Entorno de desarrollo activo con Python 3.12+ y dependencias instaladas en `.venv`.

---

## 1. Validación de Pruebas Unitarias Automatizadas (Pytest)

Ejecutar la suite focalizada en el parsing y modelado de medicamentos en el nodo de extracción:

```bash
pytest backend/tests/test_agent_cases.py -k "medicamento" -v
```

**Resultado esperado**:
- `test_parsear_respuesta_extrae_medicamentos_prescritos`: PASSED
- `test_consolidar_datos_combina_medicamentos_sin_duplicados`: PASSED
- `test_medicamentos_incompletos_o_malformados_no_rompen_el_estado`: PASSED

---

## 2. Validación de Enrutamiento a Farmacia Hospitalaria

Ejecutar la suite de decisiones de enrutamiento:

```bash
pytest backend/tests/test_destinos_triaje_unit.py -k "farmacia" -v
```

**Resultado esperado**:
- `test_enrutamiento_con_medicamentos_deriva_a_farmacia_hospitalaria`: PASSED
- `test_enrutamiento_medicamentos_controlados_activa_auditoria_humana`: PASSED
- `test_urgencia_vital_prevalece_sobre_receta_farmacia`: PASSED

---

## 3. Validación de Regresiones en Toda la Suite de Triaje

Verificar que la totalidad de los tests del backend continúan en verde:

```bash
pytest backend/tests/test_agent_cases.py backend/tests/test_destinos_triaje_unit.py -v
```

**Resultado esperado**: 100% de tests PASSED, 0 fallos, 0 errores.

---

## 4. Ejemplo de Invocación con Python (Smoke Test Manual)

```python
import asyncio
from app.agent.nodes.extraction import _parsear_respuesta
from app.agent.nodes.routing import _calcular_destino

# 1. Simulación de respuesta JSON de LLM con prescripciones
raw_llm = '''{
    "paciente": {"nombre": "Juan Perez", "edad": 45},
    "diagnostico_principal": "Faringoamigdalitis aguda",
    "cie10_sugerido": "J03.9",
    "medicamentos": [
        {"medicamento": "Amoxicilina", "dosis": "500 mg", "frecuencia": "cada 8 horas", "via_administracion": "oral"},
        {"medicamento": "Ibuprofeno", "dosis": "400 mg", "frecuencia": "cada 8 horas", "via_administracion": "oral"}
    ]
}'''

datos = _parsear_respuesta(raw_llm)
assert len(datos.medicamentos) == 2
assert datos.medicamentos[0].medicamento == "Amoxicilina"

# 2. Evaluación de enrutamiento
destino, justificacion, _, requiere_audit = _calcular_destino(
    score=0.92,
    nivel="Rutina",
    diagnostico=datos.diagnostico_principal,
    paciente_nombre=datos.paciente.nombre,
    tipo_documento="Receta Médica",
    medicamentos_controlados=False,
    tiene_medicamentos=True,
)

assert destino == "Farmacia_Hospitalaria"
assert requiere_audit is False
print("✅ Smoke test exitoso: Medicamentos extraídos y enrutados correctamente a Farmacia_Hospitalaria.")
```
