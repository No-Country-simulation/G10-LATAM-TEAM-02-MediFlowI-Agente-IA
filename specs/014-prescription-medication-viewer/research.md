# Phase 0: Research & Technical Decisions — Prescripciones Médicas y Visor Clínico

**Feature**: [014-prescription-medication-viewer](spec.md)  
**Date**: 2026-10-20  
**Status**: Completed  

---

## Decision 1: Contrato de Tipado y Deserialización Defensiva de Farmacoterapia en Frontend

### Contexto
El pipeline de extracción clínica (Pipeline Fusion / Gemini) extrae prescripciones con las propiedades `medicamento` (o `nombre`), `dosis`, `frecuencia` y `via_administracion`. En entornos clínicos reales, una receta médica puede omitir la frecuencia o la vía de administración si es sobreentendida (ej. "Amoxicilina 500mg"), o presentar nombres genéricos versus comerciales.

### Decisión
Definir la interfaz TypeScript `Medication` en `frontend/src/types/documents.ts`:
```typescript
export interface Medication {
  nombre?: string
  medicamento?: string
  dosis?: string
  frecuencia?: string
  via_administracion?: string
}
```
En la capa de API (`frontend/src/api/documentsApi.ts`), implementar una normalización defensiva con fallback bidireccional (`m.medicamento || m.nombre || ''`), garantizando que cualquier formato emitido por los modelos del backend se mapee limpiamente a propiedades consumibles por los componentes React.

### Alternativas Evaluadas
- **Validación estricta con lanzamiento de error**: Descartada porque causaría fallos de renderizado en documentos con prescripciones parciales o recetas manuscritas de emergencia.
- **Visualización en texto plano sin normalizar**: Descartada porque no permite filtrar ni presentar badges clínicos por vía de administración.

---

## Decision 2: Presentación Visual Estructurada de Medicamentos (Ficha de Detalle, Triaje y Auditoría)

### Contexto
La información de medicamentos debe ser accesible en tres puntos neurálgicos de la aplicación:
1. `ExtractedData.tsx`: Componente modular de ficha clínica (`/documentos/:id`).
2. `TriageConsoleView.tsx`: Consola operativa de triaje en tiempo real (`/triaje`).
3. `AuditDetail.tsx`: Bandeja de resolución médica manual *Human-in-the-Loop* (`/auditoria/:id`).

### Decisión
- Incorporar una sección dedicada con icono de farmacoterapia (`FaPills` / `Pill`) y tabla con columnas: *Medicamento*, *Dosis*, *Frecuencia* y *Vía de Administración*.
- Estilizar la vía de administración con insignias (`badges`) visualmente diferenciadas (ej. `bg-secondary-subtle text-secondary`) para acelerar el escaneo visual del personal médico.
- Ocultar la sección o mostrar estado "No identificado / No aplica" cuando no existan medicamentos prescritos, preservando la sobriedad visual clínica y evitando tablas vacías.

### Alternativas Evaluadas
- **Tarjeta independiente flotante**: Descartada porque rompe la jerarquía Bento de la ficha clínica de datos extraídos.
- **Mostrar tabla vacía siempre**: Descartada porque añade ruido cognitivo innecesario en documentos que no son recetas (ej. informes ecográficos, analíticas de sangre).

---

## Decision 3: Desacoplamiento Semántico y Accesibilidad en `DocumentViewer.tsx`

### Contexto
Cuando un archivo PDF o imagen clínica falla al cargarse o decodificarse en el navegador, el panel de contingencia clínica debe alertar al usuario y proporcionar alternativas operativas (descarga directa o visualización en pestaña nueva). Anteriormente, el encabezado `<h3>` utilizaba el mismo texto exacto que el párrafo `<p>`, generando colisiones en las consultas de Testing Library (`getByText`) y confusión en lectores de pantalla (redundancia para usuarios con discapacidad visual).

### Decisión
Desacoplar explícitamente el encabezado del cuerpo explicativo:
- **Encabezado `<h3>`**: Conciso, tipificado según el formato:
  - PDF: `"Error de visualización del documento PDF"`
  - Imagen: `"Error de decodificación de imagen clínica"`
- **Cuerpo descriptivo `<p>`**: Explicativo, indicando causas técnicas y acciones de contingencia:
  - PDF: `"No fue posible renderizar el documento PDF embebido en el navegador. Puede deberse a restricciones de seguridad, red o formato del archivo."`
  - Imagen: `"No fue posible decodificar o cargar la imagen clínica. El archivo podría estar dañado o el formato no es compatible con el navegador."`

### Alternativas Evaluadas
- **Modificar solo las pruebas unitarias para usar `getAllByText`**: Descartada porque enmascara una deficiencia de accesibilidad semántica en el código de producción.

---

## Decision 4: Persistencia y Proyección en Backend (`postgres_storage.py` y `documents.py`)

### Contexto
La tabla `documentos_triaje` en PostgreSQL 17 almacena metadatos clínicos y el resultado estructurado de la IA. Los endpoints `/api/v1/documents` y `/api/v1/documents/{id}` serializan las filas para consumo del frontend.

### Decisión
- Almacenar la lista estructurada de medicamentos extraídos dentro de `metadata["medicamentos"]` durante el `UPSERT` en `PostgresStorageRepository`.
- En `_format_document_row()` (`documents.py`), proyectar `medicamentos` dentro de `datos_extraidos["medicamentos"]`, asegurando que tanto las consultas individuales como los listados provean la farmacoterapia sin requerir migraciones DDL destructivas previas a la migración unificada de base de datos.

### Alternativas Evaluadas
- **Crear tabla relacional dedicada `medicamentos_recetados` de inmediato**: Postergada a la implementación de la nueva arquitectura de base de datos (`Docs/PROPUESTA_NUEVA_BASE_DE_DATOS.md`), ya que requiere migración coordinada con el equipo de infraestructura.
