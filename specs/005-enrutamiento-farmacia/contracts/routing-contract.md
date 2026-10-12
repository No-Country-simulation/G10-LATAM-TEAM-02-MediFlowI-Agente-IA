# Phase 1: Routing Interface Contract

## Interfaz Interna: `routing.py` (`_calcular_destino`)

### Firma Modificada
La función interna `_calcular_destino` será ampliada para recibir los dos nuevos parámetros clínicos necesarios sin romper las llamadas existentes.

```python
def _calcular_destino(
    score: float,
    nivel: str | None,
    diagnostico: str | None,
    paciente_nombre: str | None,
    tipo_documento: str | None = None,
    es_controlado: bool = False
) -> tuple:
```

### Matriz de Decisión Clínica (Reglas de Negocio)

La lógica de enrutamiento se evaluará en el siguiente orden de precedencia (respetando urgencias médicas sobre dispensación):

1. **Ambigüedad Clínica**: (Sin cambios).
2. **Emergencia Médica**: Si `nivel == "Urgente"`, prioridad absoluta a emergencias independientemente de si es receta o no.
3. **Control Farmacológico Estricto**:
   - **IF** (`tipo_documento == "Receta_Medica"` **OR** "farmacoterapia" en `diagnostico` sin "descompensación aguda") **AND** `es_controlado == True`
   - **Destino**: `"Farmacia_Hospitalaria"`
   - **Auditoría (HITL)**: `True`
   - **Justificación**: `"Receta o farmacoterapia con medicamentos controlados/narcóticos. Requiere revisión estricta de Farmacia/Auditor."`
4. **Dispensación Estándar**:
   - **IF** (`tipo_documento == "Receta_Medica"` **OR** "farmacoterapia" en `diagnostico` sin "descompensación aguda") **AND** `es_controlado == False`
   - **Destino**: `"Farmacia_Hospitalaria"`
   - **Auditoría (HITL)**: `False`
   - **Justificación**: `"Receta o farmacoterapia exclusiva procesada con éxito. Derivada a Farmacia_Hospitalaria."`
5. **Score Bajo**: Si score < 0.5 (Sin cambios).
6. **Rutina**: (Sin cambios).
