# Research & Technical Decisions: Extracción Estructurada de Medicamentos y Enrutamiento a Farmacia Hospitalaria

**Feature**: `011-prescription-medication-extraction`  
**Date**: 2026-10-15  
**Status**: Completed  

---

## 1. Modelado de Medicamentos con Pydantic v2

- **Decision**: Crear el modelo `MedicamentoPrescritoState(BaseModel)` en `backend/app/agent/state.py` con los siguientes campos estrictamente tipados:
  ```python
  class MedicamentoPrescritoState(BaseModel):
      medicamento: str
      dosis: str | None = None
      frecuencia: str | None = None
      via_administracion: str | None = None
  ```
  E integrar en `DatosExtraidosState`:
  ```python
  medicamentos: list[MedicamentoPrescritoState] = Field(default_factory=list)
  ```
- **Rationale**: 
  - Cumple rigurosamente el Principio I de la Constitución (tipado estricto con Pydantic v2 sin `Any` no controlado).
  - La inicialización por defecto con `default_factory=list` garantiza compatibilidad hacia atrás: todo documento sin prescripciones o previamente serializado tendrá `medicamentos = []` en lugar de `None`, erradicando errores de tipo `AttributeError` o `TypeError` en el pipeline.
- **Alternatives Considered**:
  - `list[dict]`: Descartado por violar la política constitucional de modelos tipados.
  - Tupla de cadenas `tuple[str, ...]`: Descartado por falta de introspección semántica y dificultad de serialización JSON/OpenAPI.

---

## 2. Enriquecimiento del Prompt de Extracción (`_EXTRACTION_PROMPT`)

- **Decision**: Modificar la plantilla `_EXTRACTION_PROMPT` en `backend/app/agent/nodes/extraction.py` para incluir la clave `"medicamentos"` dentro del esquema JSON esperado por el LLM:
  ```json
  "medicamentos": [
    {
      "medicamento": "Nombre del fármaco prescrito",
      "dosis": "Dosis y unidad (ej. 500 mg, o null)",
      "frecuencia": "Frecuencia/intervalo (ej. cada 8 horas, o null)",
      "via_administracion": "Vía anatómica (ej. oral, intravenosa, o null)"
    }
  ]
  ```
  Se añade instrucción explícita de devolver arreglo vacío `[]` si el texto no describe prescripciones farmacológicas activas.
- **Rationale**:
  - Unificar la extracción de medicamentos en la misma llamada del nodo `extraction` aprovecha la ventana de contexto del LLM y minimiza latencia y costos operativos en comparación con añadir un nodo LLM adicional.
- **Alternatives Considered**:
  - Crear un nodo independiente `node_medications`: Descartado por añadir latencia innecesaria (~1.5s por inferencia) y complejidad al grafo de LangGraph.

---

## 3. Deserialización y Consolidación Defensiva

- **Decision**: 
  - En `_parsear_respuesta(raw)`: Extraer `data.get("medicamentos")`. Si es una lista, iterar cada elemento verificando que sea un diccionario con clave `"medicamento"` (cadena no vacía tras `.strip()`). Construir instancias de `MedicamentoPrescritoState`. Ignorar silenciosamente elementos malformados.
  - En `_consolidar_datos(acumulado, nuevo)`: Combinar `acumulado.medicamentos` y `nuevo.medicamentos` eliminando duplicados mediante una clave de unicidad basada en `(item.medicamento.strip().lower(), (item.dosis or "").strip().lower(), (item.frecuencia or "").strip().lower(), (item.via_administracion or "").strip().lower())`.
- **Rationale**:
  - En documentos médicos largos que se dividen en bloques (`dividir_texto_en_bloques`), asegura que los medicamentos de todas las páginas se acumulen sin multiplicarse si un fármaco se repite en el solapamiento o encabezado.
- **Alternatives Considered**:
  - Mantener solo los medicamentos del último bloque: Descartado porque perdería prescripciones contenidas en las primeras páginas de recetas multipágina.

---

## 4. Enrutamiento a `Farmacia_Hospitalaria` y Detección de Fármacos Controlados

- **Decision**: 
  - En `backend/app/agent/nodes/routing.py`, definir una lista canónica de principios activos controlados (`MEDICAMENTOS_CONTROLADOS`):
    ```python
    MEDICAMENTOS_CONTROLADOS = {
        "morfina", "fentanilo", "oxicodona", "metadona", "tramadol", "buprenorfina",
        "clonazepam", "alprazolam", "lorazepam", "diazepam", "midazolam",
        "fenobarbital", "metilfenidato", "codeina", "codeína"
    }
    ```
  - En `node_routing`:
    1. Si `state.datos_extraidos and state.datos_extraidos.medicamentos`:
       - Verificar si alguno de los fármacos coincide (parcial o totalmente) con `MEDICAMENTOS_CONTROLADOS`. Si es así, activar `meds_controlados = True`.
    2. Pasar `tiene_medicamentos = bool(state.datos_extraidos and state.datos_extraidos.medicamentos)` a `_calcular_destino`.
    3. Si la prioridad es `Urgente`, prevalece `Cola_Emergencia_Medica`.
    4. Si `score < 0.75`, prevalece `Cola_Auditoria_Humana`.
    5. Si `tipo_documento == "Receta Médica"` o `tiene_medicamentos` o diagnóstico de farmacoterapia no descompensada:
       - Si `meds_controlados == True`: Derivar a `Farmacia_Hospitalaria` con `requiere_auditoria_humana = True` (alerta de sustancias controladas).
       - Si `meds_controlados == False`: Derivar a `Farmacia_Hospitalaria` con `requiere_auditoria_humana = False`.
- **Rationale**:
  - Garantiza cumplimiento estricto con las regulaciones de fiscalización de estupefacientes (HITL asistencial), mientras automatiza el flujo de farmacia estándar para recetas ordinarias con alta confianza.
- **Alternatives Considered**:
  - Enrutar fármacos controlados a `Cola_Auditoria_Humana`: Descartado porque el servicio de destino operativo sigue siendo Farmacia Hospitalaria; la auditoría médica actúa como bandera (`requiere_auditoria_humana = True`) dentro de la misma derivación.

---

## 5. Actualización de OpenAPI Contract y Compatibilidad

- **Decision**:
  - Incorporar el esquema `MedicamentoPrescrito` en `specs/components/schemas.yaml` y referenciarlo en `DatosExtraidos.properties.medicamentos`.
  - Asegurar que la serialización en `triage_service.py` y `postgres_storage.py` preserve el arreglo `medicamentos` dentro del JSON almacenado en `documentos_triaje.resultado_json`.
- **Rationale**:
  - Cumple con la sincronización obligatoria de OpenAPI estipulada en `AGENTS.md` y la Constitución del proyecto.
