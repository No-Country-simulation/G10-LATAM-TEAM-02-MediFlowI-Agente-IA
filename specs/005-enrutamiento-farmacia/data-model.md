# Phase 1: Data Model Updates

No se requieren cambios estructurales en los esquemas Pydantic de `AgentState` ya que `"Farmacia_Hospitalaria"` ya existe como un destino permitido en el campo literal `DecisionEnrutamientoState.destino_principal`.

## Metadata Injection (Contrato de Datos Implícito)

Para que el enrutamiento funcione correctamente, se define la siguiente convención de datos en memoria para el paso de mensajes entre nodos:

- **Clave de Metadata**: `medicamentos_controlados` (tipo: `bool`).
- **Ubicación**: `AgentState.metadata`.
- **Descripción**: Si es `True`, indica que el documento analizado contiene al menos un medicamento clasificado como estupefaciente, psicotrópico o de control especial.
- **Acción derivada**: El nodo `routing` forzará `requiere_auditoria_humana = True`.
