# 🎨 Propuesta de Diseño UI/UX y Sistema de Diseño – MediFlow
**Proyecto:** MediFlow – Agente Autónomo para Triaje Clínico  
**Enfoque:** HealthTech Clinical Experience (Ergonomía Médica y Reducción de Carga Cognitiva)  
**Versión:** 1.0.0  

---

## 1. Filosofía de Diseño: "Claridad Quirúrgica"

En entornos médicos y hospitalarios, una mala interpretación visual puede costar vidas o generar horas de retraso. El diseño de **MediFlow** se rige por tres principios no negociables:

1. **Prioridad Visual Instantánea:** Un médico o auditor debe comprender la gravedad del caso en menos de **2 segundos** mediante códigos cromáticos universales.
2. **Trazabilidad Lado a Lado (Split-Screen):** El documento original (fuente de la verdad) y los datos extraídos por la IA deben verse en paralelo para verificación inmediata sin cambiar de pestaña.
3. **Control Humano sin Fricción (HITL):** Los casos ambiguos destacan de inmediato con acciones claras de aprobación o corrección a un solo clic.

---

## 2. Sistema de Tokens y Paleta de Colores

Diseñado bajo la escala de contraste accesible **WCAG AA** para evitar fatiga visual en turnos médicos prolongados:

### 2.1 Colores Semánticos de Prioridad Clínica

| Nivel de Prioridad | Color HEX | Significado Clínico | Uso en la UI |
|---|---|---|---|
| **Urgente** | `#DC2626` (Rojo Carmesí) | Riesgo vital inmediato (TEP, IAM, ACV) | Badges pulsantes, bordes de tarjeta, alerta de guardia |
| **Prioritario** | `#F59E0B` (Ámbar Clínico) | Cuadros subagudos o revisión requerida | Badges de advertencia, estado de auditoría humana |
| **Rutina** | `#10B981` (Esmeralda Salud) | Flujo normal aprobado hacia farmacia/HCE | Confirmación de guardado, tags estándar |
| **Baja Confianza** | `#8B5CF6` (Púrpura Alerta) | Documento ilegible o incompleto (< 0.85) | Indicador de score de confianza y cola HITL |

### 2.2 Colores Base (Clinical Slate & Dark Medical)
* **Fondo Principal (Modo Oscuro):** `#0F172A` (Slate 900)
* **Superficie de Tarjetas (Cards):** `#1E293B` (Slate 800)
* **Bordes y Divisores:** `#334155` (Slate 700)
* **Acento Primario (HealthTech Cyan):** `#06B6D4` (Cyan 500)
* **Texto Principal:** `#F8FAFC` (Slate 50)
* **Texto Secundario / Metadatos:** `#94A3B8` (Slate 400)

---

## 3. Tipografía y Jerarquía

* **Fuente Principal:** `Inter` o `Outfit` (fuentes sans-serif humanistas con alta legibilidad en números y dosis médicas).
* **Fuente para Códigos y CIE-10:** `JetBrains Mono` o `Fira Code` (para códigos CIE-10 `I26.9`, identificadores `DOC-CLIN-...` y JSONs).

| Elemento | Tamaño / Peso | Aplicación |
|---|---|---|
| **H1 - Título** | `24px` / Bold | Cabecera del Dashboard y Estado General |
| **H2 - Sección** | `18px` / SemiBold | Título de Paneles (Visor, Extracción, Enrutamiento) |
| **Diagnóstico Principal** | `16px` / Bold | Resaltado del cuadro clínico detectado |
| **CIE-10 Badge** | `14px` / Mono Medium | Código de clasificación internacional |
| **Body / Datos** | `14px` / Regular | Paciente, médico, posología de medicamentos |
| **Microdatos** | `12px` / Regular | Timestamps, rutas de OCI Object Storage, matriculas |

---

## 4. Arquitectura de Pantalla (Layout Split-Screen)

```
+---------------------------------------------------------------------------------------------------+
|  🏥 MediFlow HealthTech       [🔴 1 Urgencia Activa]   [⚠️ 2 En Auditoría]   [☁️ OCI Bucket: Activo] |
+---------------------------------------------------------------------------------------------------+
|  [📂 Subir PDF/Imagen]  [⚡ Seleccionar Caso Demo: Caso 1 (Rutina) | Caso 2 (TEP) | Caso 3 (HITL)]  |
+---------------------------------------------------------------------------------------------------+
|                                                 |                                                 |
|  📄 PANEL IZQUIERDO: DOCUMENTO FUENTE (45%)     |  🩺 PANEL DERECHO: TRIAJE CLÍNICO (55%)          |
|                                                 |                                                 |
|  +-------------------------------------------+  |  +-------------------------------------------+  |
|  | Visor Interactivo (PDF / Imagen / Texto)   |  |  | 🚨 PRIORIDAD: [ URGENTE ]  Score: 99%     |  |
|  |                                           |  |  | Destino: [ Cola_Emergencia_Medica ]       |  |
|  | "HOSPITAL SANTA LUCIA                     |  |  +-------------------------------------------+  |
|  |  INFORME DE ESTUDIO RADIOLOGICO...        |  |                                                 |
|  |  Paciente: Carlos Eduardo Mendes...       |  |  👤 PACIENTE: Carlos Eduardo Mendes (52 años)   |
|  |  Hallazgos: Defecto de llenado en arteria |  |  👨‍⚕️ MÉDICO: Dra. Renata Silveira (MP 145892)     |
|  |  pulmonar principal derecha..."           |  |                                                 |
|  |                                           |  |  🔬 DIAGNÓSTICO DETECTADO:                      |
|  |                                           |  |  Tromboembolismo Pulmonar Agudo (TEP)          |
|  |                                           |  |  Código CIE-10 Sugerido: [ I26.9 ]            |
|  |                                           |  |                                                 |
|  |                                           |  |  📦 RESPALDO EN CLOUD:                          |
|  |                                           |  |  OCI: procesados/urgentes/DOC-8942.json  ✅    |
|  +-------------------------------------------+  |  +-------------------------------------------+  |
|                                                 |                                                 |
+---------------------------------------------------------------------------------------------------+
|  BARRA DE ACCIÓN HUMAN-IN-THE-LOOP (Visible si score < 0.85 o caso ambiguo):                      |
|  [⚠️ Este caso requiere revisión]   [✏️ Editar Datos Extraídos]   [✅ Aprobar Triaje]   [❌ Rechazar] |
+---------------------------------------------------------------------------------------------------+
```

---

## 5. Micro-Interacciones y Componentes Clave

### 5.1 Banner de Urgencia Crítica (Alerta Activa)
Cuando el modelo detecta una condición de riesgo vital (ej. TEP agudo):
* Un contorno rojo pulsante (`animate-pulse`) rodea la tarjeta de triaje.
* Aparece un *toast* de notificación: *"🚨 ALERTA EMITIDA: Informe crítico derivado de inmediato a Guardia de Emergencias"*.
* Se reproduce un sutil sonido de aviso (opcional en UI).

### 5.2 Gauge de Confianza de la Extracción
* Un indicador circular porcentual muestra el `score_confianza_clasificacion`:
  * **Verde (90% - 100%):** Alta fidelidad clínica.
  * **Amarillo (85% - 89%):** Confianza moderada, validada automáticamente.
  * **Rojo / Púrpura (< 85%):** Dispara obligatoriamente la barra de auditoría humana.

### 5.3 Panel de Auditoría Human-in-the-Loop (HITL)
* Para documentos con letra manuscrita o datos truncados:
  * Los campos dudosos se iluminan con un halo ámbar.
  * El auditor médico puede hacer clic en cualquier campo para corregirlo directamente en la pantalla antes de pulsar `[Aprobar y Enrutar]`.
  * La aprobación humana actualiza el estado en OCI Object Storage moviéndolo de `/auditoria_humana/` a `/procesados/`.

---

## 6. Implementación en React (Vite + TypeScript)

Esta especificación de diseño se implementa mediante una arquitectura de componentes modulares en React 18:
1. **Componentes Atómicos:** Botones con área táctil (`min-h-[44px]`), badges con paleta clínica (`#DC2626`, `#F59E0B`, `#10B981`) y tarjetas (`bg-slate-800` y borde `slate-700`).
2. **Layout Split-Screen:** Grid responsive de 2 columnas (`lg:grid-cols-2`) con scroll independiente en cada panel.
3. **Panel Human-in-the-Loop:** Barra de aprobación con acción en 1-clic conectada a `POST /api/v1/auditoria/{id}`.
4. **Visor de Documentos:** Componente integrado para renderizar texto, PDF o imágenes médicas con zoom táctil.

---

## 7. Especificación Responsive & Mobile-First (Desktop, Tablet y Mobile)

Para garantizar ergonomía en estaciones médicas fijas, tablets de ronda hospitalaria y smartphones de guardia:

### 7.1 Breakpoints de Pantalla

| Dispositivo | Breakpoint | Distribución del Layout | Comportamiento del Visor Split-Screen |
|---|---|---|---|
| **Desktop / Monitores Médicos** | `≥ 1024px` (`lg`, `xl`) | Split-Screen 2 Columnas (45% doc / 55% triaje) | Visualización simultánea lado a lado con scroll independiente. |
| **Tablets (Ronda en Sala)** | `768px - 1023px` (`md`) | Split-Screen adaptable o Paneles Colapsables | Columnas equilibradas 50/50 con opción de maximizar panel. |
| **Mobile (Guardia Hospitalaria)** | `< 768px` (`sm`, `xs`) | Columna única apilada o Sistema de Pestañas | Pestaña 1: **Triaje & Alerta** · Pestaña 2: **Documento Fuente**. |

### 7.2 Comportamiento Mobile-First (Smartphones de Médicos)
1. **Navegación por Pestañas (Tabs):** En pantallas pequeñas, el Split-Screen se transforma en 2 pestañas principales:
   * **Tab 1: "Diagnóstico & Enrutamiento" (Activa por defecto):** Muestra de inmediato la gravedad (ej. banner rojo pulsante de TEP), el código CIE-10 y el resumen.
   * **Tab 2: "Documento Original":** Muestra la imagen o PDF original con soporte de zoom táctil (*pinch-to-zoom*).
2. **Barra de Acción HITL Flotante (*Sticky Bottom Bar*):**
   * En móviles, los botones de aprobación (`Aprobar Triaje 1-clic` / `Rechazar / Editar`) quedan **fijados en la parte inferior de la pantalla** (`position: sticky; bottom: 0;`).
   * Permite al médico de guardia validar la derivación en menos de 2 segundos con el pulgar, sin necesidad de hacer scroll hasta el final del documento.

### 7.3 Ergonomía Táctil y Accesibilidad
* **Área táctil mínima:** Todos los botones interactivos, selectores y chips tienen un tamaño mínimo de **`44 x 44 px`** para evitar toques accidentales en pantallas táctiles médicas.
* **Mapeo de Iconos Semánticos (`lucide-react`):**
  * `AlertOctagon` / `Flame`: Urgencia crítica de riesgo vital (`#DC2626`).
  * `AlertTriangle` / `Clock`: Caso en auditoría humana HITL (`#F59E0B`).
  * `CheckCircle2` / `Pill`: Caso de rutina aprobado para farmacia (`#10B981`).
  * `FileText` / `Eye`: Visor de documento original y OCR.
  * `ShieldCheck`: Confirmación de auditoría y persistencia OCI.
