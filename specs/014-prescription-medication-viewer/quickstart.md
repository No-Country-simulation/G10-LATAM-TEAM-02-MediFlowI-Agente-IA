# Quickstart Validation Guide: Prescripciones Médicas y Visor Clínico

**Feature**: [014-prescription-medication-viewer](spec.md)  
**Date**: 2026-10-20  

---

## Prerrequisitos

- Entorno de desarrollo activo con Node.js 20+ y Python 3.12+
- Dependencias de frontend y backend instaladas:
  ```bash
  cd frontend && npm install
  cd ../backend && poetry install
  ```

---

## Escenarios de Validación Rápida

### Escenario 1: Validación de Tipos y Pruebas Unitarias de Frontend

Verificar que los componentes y contratos de datos compilen limpiamente sin errores de TypeScript y que las 94 pruebas unitarias pasen en verde:

```bash
# 1. Ejecutar suite de pruebas de frontend (Vitest)
npm --prefix frontend test -- --run

# 2. Compilar bundle de producción (TypeScript estricto)
npm --prefix frontend run build
```

**Resultado Esperado**:
- Vitest: `13 passed (13)` archivos de prueba, `94 passed (94)` tests en verde.
- Build: Compilación limpia (`tsc -b && vite build`) en menos de 5 segundos con 0 errores de tipos.

---

### Escenario 2: Validación de Integración y Extracción Backend (Pytest)

Comprobar que el endpoint de documentos y el pipeline multimodal extraen y formatean correctamente los medicamentos prescritos:

```bash
# Ejecutar pruebas del pipeline de extracción y API de documentos
backend/.venv/bin/pytest backend/tests/test_pipeline_fusion.py backend/tests/test_documents_api.py
```

**Resultado Esperado**:
- `test_pipeline_fusion.py`: 32 tests aprobados en verde.
- `test_documents_api.py`: 17 tests aprobados en verde.

---

### Escenario 3: Verificación Visual en Interfaz de Usuario (End-to-End)

1. **Ficha de Detalle Clínico (`/documentos/:id`)**:
   - Abrir un caso clínico con prescripción médica (ej. receta médica procesada).
   - Verificar la presencia de la tarjeta con encabezado `Medicamentos Prescritos` e icono `FaPills`.
   - Comprobar que cada fármaco muestra: Nombre, Dosis, Frecuencia y la insignia de `Vía de Administración`.

2. **Consola de Triaje (`/triaje`)**:
   - Cargar un caso de triaje con receta.
   - En el panel de resultados extraídos, constatar la tabla `💊 Medicamentos Prescritos Extraídos:`.

3. **Bandeja de Auditoría (`/auditoria/:id`)**:
   - Acceder como usuario con rol `COORDINADOR` a una auditoría pendiente.
   - Constatar la tabla de `Medicamentos Prescritos Detectados` como soporte de validación clínica.

4. **Panel de Contingencia del Visor Clínico (`DocumentViewer.tsx`)**:
   - Simular un error de carga de imagen o PDF.
   - Verificar que el `<h3>` muestre un título unívoco ("Error de decodificación de imagen clínica") separado de la descripción explicativa en el `<p>`.
