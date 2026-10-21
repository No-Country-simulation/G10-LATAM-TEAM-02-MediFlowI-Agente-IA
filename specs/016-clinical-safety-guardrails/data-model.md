# Data Model & Entidades: Guardrails de Seguridad Clínica

**Feature**: [016-clinical-safety-guardrails](file:///home/wigsdev/GitHub/mediflow/specs/016-clinical-safety-guardrails/spec.md)  
**Date**: 2026-10-20  
**Status**: Ready for Implementation  

---

## Entidades y Estructuras de Datos

### 1. `MatrizRedFlagsClinicas` (Configuración Determinista)

Catálogo inmutable en memoria que define las condiciones y códigos de riesgo vital inminente para la validación cruzada.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ReglaRedFlag:
    nombre: str
    terminos_clave: list[str]
    codigos_cie10: list[str]
    prioridad_minima_esperada: str = "Urgente"
    patrones_negacion: list[str] = field(default_factory=lambda: [
        "se descarta", "sin signos de", "descarte de", "no presenta", "descartado"
    ])
```

**Instancias Base en el Sistema**:
- `TEP`: términos `["tromboembolismo pulmonar", "tep", "embolia pulmonar"]`, CIE-10 `["I26", "I26.9"]`.
- `IAM`: términos `["infarto agudo de miocardio", "iam", "sindrome coronario agudo", "elevacion del st"]`, CIE-10 `["I21", "I21.9"]`.
- `SHOCK`: términos `["shock septico", "shock cardiogenico", "shock hipovolemico", "shock anafilactico"]`, CIE-10 `["R57", "R57.0", "R57.1", "R57.2", "R57.9"]`.
- `PARO`: términos `["paro cardiorrespiratorio", "pcr", "asistolia", "fibrilacion ventricular"]`, CIE-10 `["I46", "I46.9"]`.
- `ACV`: términos `["accidente cerebrovascular", "acv", "ictus isquemico", "hemorragia subaracnoidea"]`, CIE-10 `["I63", "I64"]`.
- `HEMORRAGIA`: términos `["hemorragia masiva", "shock hemorragico", "exanguinante"]`, CIE-10 `["R58"]`.

---

### 2. `PaginaEvaluadaPDF` (Inspección Folio por Folio)

Estructura temporal en el nodo `ingestion` para modelar las características de cada folio del PDF antes de decidir su extracción.

| Campo | Tipo | Descripción |
|---|---|---|
| `indice_pagina` | `int` | Índice 0-based de la página dentro del documento PDF |
| `caracteres_texto` | `int` | Cantidad de caracteres de texto vectorial extraídos con PyMuPDF |
| `tiene_imagenes` | `bool` | `True` si la página contiene imágenes incrustadas (`get_images()`) |
| `es_visual` | `bool` | `True` si `caracteres_texto < 50` o si carece de texto significativo |
| `texto_extraido` | `str | None` | Texto extraído directamente si la página es digital |
| `imagen_rasterizada_b64` | `str | None` | Buffer JPEG Base64 optimizado si la página requiere visión |

---

### 3. `ResultadoEvaluacionGuardrail` (Auditoría Semántica)

Estructura de respuesta generada al validar coherencia y pertenencia al dominio.

```python
from pydantic import BaseModel, Field

class ResultadoEvaluacionGuardrail(BaseModel):
    es_fuera_de_dominio: bool = False
    es_discordancia_critica: bool = False
    red_flag_detectada: str | None = None
    motivo_retencion: str | None = None
    score_confianza_ajustado: float | None = None
    destino_recomendado: str | None = None
    requiere_auditoria_humana: bool = False
```

---

## Campos de Metadatos Añadidos en `AgentState.metadata`

Para garantizar la trazabilidad clínica y auditoría hospitalaria inmutable, se incorporan las siguientes claves en el diccionario `metadata`:

| Clave de Metadata | Tipo | Descripción |
|---|---|---|
| `fuera_de_dominio_clinico` | `bool` | `True` si el documento fue catalogado como No Clínico u Otro |
| `tipo_documento_rechazado` | `str` | Nombre de la categoría no clínica detectada (ej. `"Otro"`) |
| `documento_asimetrico_detectado` | `bool` | `True` si el PDF combinó páginas digitales y páginas escaneadas |
| `paginas_visuales_procesadas` | `int` | Cantidad de páginas rasterizadas procesadas con visión (1 a 3) |
| `discordancia_critica_red_flags` | `bool` | `True` si se detectó una patología de riesgo vital clasificada como Rutina |
| `red_flag_detectada` | `str` | Nombre del Red Flag o código CIE-10 que activó la discordancia |
| `motivo_retencion` | `str` | Motivo oficial para la bandeja HITL (`"fuera_de_dominio_clinico"` o `"discordancia_critica_red_flags"`) |
