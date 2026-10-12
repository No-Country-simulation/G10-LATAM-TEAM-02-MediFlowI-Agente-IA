# Interface Contract: Patient Matcher & Pipeline Decision

**Feature**: `004-patient-matcher-conflicts` (`[IA-02]`, Issue `#29`)  
**Date**: 2026-10-05  

---

## 1. Módulo `patient_matcher.py`

### Función: `verificar_identidad_paciente`

```python
async def verificar_identidad_paciente(
    dni: str | None,
    historia_clinica: str | None,
) -> ResultadoMatchingPaciente:
    """
    Coteja el DNI y la Historia Clínica contra PostgreSQL usando patient_repository.
    
    Args:
        dni: Número de documento extraído (o None).
        historia_clinica: Código de historia clínica extraído (o None).
        
    Returns:
        ResultadoMatchingPaciente con:
          - estado: 'asociado' | 'sin_coincidencia' | 'conflicto'
          - paciente: dict del paciente si asociado, None en otro caso
          - es_conflicto: True si estado == 'conflicto'
          - motivo: Explicación de la discrepancia si aplica
    """
```

---

## 2. Contrato de Decisión en `routing.py`

### Regla de Precedencia Clínica (Discrepancia de Identidad)

1. Si `state.metadata.get("discrepancia_identidad_detectada") is True`:
   - `destino_principal`: `"Cola_Revision_Ambigua"`
   - `requiere_auditoria_humana`: `True`
   - `justificacion_enrutamiento`: `"Discrepancia detectada entre DNI y HC: requiere revisión de ambigüedad."`
   - `notificacion_generada`: `None`
   - `status`: `"pendiente_auditoria"`

2. Si no hay discrepancia de identidad, se aplican las reglas normales de score, nivel de prioridad (`Urgente`, `Rutina`, `Ambiguo`) y especialidad.
