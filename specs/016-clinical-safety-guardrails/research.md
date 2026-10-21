# Phase 0 Research: Guardrails de Seguridad Clínica

**Feature**: [016-clinical-safety-guardrails](file:///home/wigsdev/GitHub/mediflow/specs/016-clinical-safety-guardrails/spec.md)  
**Date**: 2026-10-20  
**Status**: Completed  

---

## Decisiones Técnicas y Arquitectónicas

### 1. Filtro Fuera de Dominio (Out-of-Domain Gate)

- **Decisión**: Interceptar en el nodo `routing.py` antes de cualquier cálculo de destino convencional. Si `tipo_documento` es `"No_Clinico"`, `"Otro"`, `"Desconocido"` o cualquier valor no contenido en las categorías clínicas admitidas:
  - Destino forzado: `"Cola_Revision_Ambigua"`.
  - Requisito de auditoría: `requiere_auditoria_humana = True`.
  - Estado operacional: `status = "pendiente_auditoria"`.
  - Metadatos: `"motivo_retencion": "fuera_de_dominio_clinico"`, `"tipo_documento_rechazado": tipo_documento`.
- **Razón de la elección**: Protege las colas clínicas operativas (`Cola_Rutina`, `Cola_Emergencia_Medica`, `Farmacia_Hospitalaria`) contra saturación por documentos ajenos (revistas, afiches musicales, publicidad), garantizando al mismo tiempo que el Coordinador Médico pueda auditar y descartar el archivo de forma transparente (gobernanza *Human-in-the-Loop*).
- **Alternativas evaluadas y descartadas**:
  - *Rechazar con HTTP 400 en API*: Descartado porque impediría que el personal clínico revise si se trata de un documento médico legítimo con formato atípico.
  - *Descarte automático silencioso a la papelera*: Descartado porque violaría el principio constitucional de trazabilidad inmutable de documentos hospitalarios.

---

### 2. Inspección Página por Página de PDFs Asimétricos e Híbridos

- **Decisión**: En `ingestion.py`, analizar individualmente cada folio del documento PDF mediante PyMuPDF (`doc[i]`):
  - Evaluar la longitud de texto vectorial de cada página: `texto_pagina = page.get_text().strip()`.
  - Identificar si la página contiene imágenes incrustadas: `tiene_imagenes = len(page.get_images()) > 0`.
  - Si una página tiene `< 50 caracteres` o contiene imágenes sin texto digital significativo, clasificarla como página visual.
  - Para PDFs asimétricos (mezcla de páginas digitales y visuales):
    - Extraer el texto nativo de las páginas digitales directamente con PyMuPDF.
    - Rasterizar hasta un máximo de **3 páginas visuales** en memoria (`fitz.Matrix(1.5, 1.5)` a JPEG optimizado < 350 KB).
    - Ejecutar visión multimodal con Gemini Vision para transcribir/extraer los folios visuales.
    - Consolidar en memoria el texto digital y la transcripción visual en `state["texto_extraido"]` antes de la fase de extracción clínica.
- **Razón de la elección**: Resuelve la vulnerabilidad donde la página 1 contiene texto digital rutinario pero la página 2 contiene una orden escaneada de urgencia. Respeta el límite acordado en clarificación de hasta 3 páginas visuales para preservar el presupuesto de memoria (< 350 KB) y la latencia hospitalaria (< 8s).
- **Alternativas evaluadas y descartadas**:
  - *Rasterizar siempre todo el PDF a imágenes*: Descartado porque duplica el consumo de cuota y añade de 3 a 5 segundos innecesarios a páginas que ya tienen texto digital perfecto.
  - *OCR local con Tesseract*: Descartado porque presenta altas tasas de error en texto manuscrito y recetas médicas frente a la visión artificial.

---

### 3. Matriz de Red Flags Clínicas y Validación Cruzada de Coherencia

- **Decisión**: Crear el módulo `backend/app/agent/clinical_guardrails.py` con una matriz determinista inmutable de patologías y síntomas de riesgo vital inminente (*Red Flags*):
  - **Términos de riesgo vital**:
    - `"tromboembolismo pulmonar"`, `"tep"`, `"embolia pulmonar"`.
    - `"infarto agudo de miocardio"`, `"iam"`, `"sindrome coronario agudo"`, `"elevacion del st"`.
    - `"shock septico"`, `"shock cardiogenico"`, `"shock hipovolemico"`.
    - `"paro cardiorrespiratorio"`, `"pcr"`, `"asistolia"`.
    - `"accidente cerebrovascular"`, `"acv"`, `"ictus isquemico"`, `"hemorragia subaracnoidea"`.
    - `"hemorragia masiva"`, `"shock hemorragico"`.
    - `"neumotorax a tension"`.
  - **Códigos CIE-10 críticos**: `I21` (IAM), `I26` (TEP), `R57` (Shock), `I46` (Paro cardíaco), `I63`/`I64` (ACV/Ictus), `J93.0` (Neumotórax a tensión).
  - **Contexto de negación defensiva**: Si el término está precedido por frases de descarte como `"se descarta"`, `"sin signos de"`, `"descarte de"`, `"no presenta"`, no se activa la bandera de discordancia.
  - **Acción ante discordancia crítica**: Si se confirma un *Red Flag* activo y la clasificación del modelo es `"Rutina"`:
    - Reducir el puntaje de confianza final a **`0.0`** (`score_final = 0.0`).
    - Marcar `requiere_auditoria_humana = True` y `status = "pendiente_auditoria"`.
    - Asignar destino forzado: `"Cola_Revision_Ambigua"`.
    - Registrar metadatos: `"discordancia_critica_red_flags": True`, `"red_flag_detectada": <termino_o_codigo>`, `"motivo_retencion": "discordancia_critica_red_flags"`.
- **Razón de la elección**: Proporciona una red de seguridad infalible contra subestimaciones de riesgo vital causadas por fallos estocásticos de modelos de lenguaje. Respeta la decisión de la Sesión 2026-10-20 de derivar a auditoría humana con confianza 0.0 para cumplimiento estricto de la Regla de Oro.
- **Alternativas evaluadas y descartadas**:
  - *Reclasificación automática silenciosa a Urgente*: Descartada por el usuario en `/speckit-clarify` para no sustituir el criterio de los médicos de guardia sin revisión.
