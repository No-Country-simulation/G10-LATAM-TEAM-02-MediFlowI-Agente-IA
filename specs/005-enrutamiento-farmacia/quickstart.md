# Phase 1: Quickstart & Validation

Para validar el enrutamiento sin depender de la UI o de la base de datos PostgreSQL, se utilizará el framework de pruebas automatizadas (pytest) siguiendo la Constitución de MediFlow (Zero Regressions).

## Ejecución de Pruebas Unitarias
El componente se puede probar de forma aislada corriendo las pruebas del triaje:

```bash
pytest backend/tests/test_destinos_triaje_unit.py -v -k "farmacia"
```

## Escenarios de Validación Esperados

1. **Receta Estándar**: Se pasa un estado mockeado con `tipo_documento="Receta_Medica"` y `metadata={"medicamentos_controlados": False}`. Debe afirmar que el destino es `Farmacia_Hospitalaria` y auditoría es `False`.
2. **Receta de Control Especial**: Se pasa un estado con `metadata={"medicamentos_controlados": True}`. Debe afirmar que el destino es `Farmacia_Hospitalaria` y auditoría es `True`.
3. **Urgencia + Receta**: Se prueba la precedencia. Si el documento tiene `nivel_prioridad="Urgente"`, debe ignorar Farmacia y enrutar a `Cola_Emergencia_Medica`.
