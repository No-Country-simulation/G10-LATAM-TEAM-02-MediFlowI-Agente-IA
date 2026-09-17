# 🛠️ MediFlow — Guía de Desarrollo y Recetario Técnico
**Manual de Referencia y Snippets para Desarrolladores del Equipo**  
*Hackathon ONE Grupo 10 (Oracle Next Education & Alura)*  
*Versión:* 1.0.0  

---

## 🎯 Propósito de este Documento

Este manual acompaña al [Backlog Unificado (`docs/backlog.md`)](backlog.md). Si estás trabajando en una tarea técnica (`T-XX`), consulta esta guía para:
1. Copiar fragmentos de código listos para usar (*snippets* probados).
2. Entender cómo conectar tu módulo con el resto del sistema sin romper contratos.
3. Resolver dudas frecuentes sin esperar una reunión.

---

## 1. Configuración del Entorno de Desarrollo Local

### 1.1 Clonado y Activación del Entorno
```bash
# 1. Clonar el repositorio
git clone https://github.com/No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA.git
cd G10-LATAM-TEAM-02-MediFlowI-Agente-IA

# 2. Crear y activar entorno virtual Python (Recomendado 3.11 o 3.12)
python3 -m venv venv
source venv/bin/activate      # En Linux/macOS
# .\venv\Scripts\activate     # En Windows

# 3. Instalar dependencias del backend
pip install -r backend-api/requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
```

### 1.2 Levantar los Servicios Locales con Docker
```bash
# Levanta la API en el puerto 8000 y n8n en el puerto 5678
docker compose up -d

# Verificar salud de la API
curl http://localhost:8000/health
# {"status":"ok","version":"1.0.0","services":{"gemini_llm":"connected","oci_object_storage":"mock_mode"}}
```

---

## 2. Guía por Tareas y Módulos del Backlog

---

### 🧪 [T-02, T-03, T-04] Datasets Clínicos de Prueba (`datasets/`)

Los datasets son archivos JSON que simulan las solicitudes de entrada a la API. Deben colocarse en la carpeta `datasets/`:

#### Estructura Canónica de Entrada:
```json
{
  "documento_id": "DOC-CLIN-2026-8942",
  "tipo_archivo": "PDF",
  "documento_texto": "HOSPITAL SANTA LUCIA - INFORME RADIOLOGICO. Paciente: Carlos Eduardo Mendes, 52 anos. Medico Solicitante: Dra. Renata Silveira MP 145892. Estudio: Tomografia de Torax con contraste. CONCLUSION: Cuadro compatible con Tromboembolismo Pulmonar Agudo (TEP). Se sugiere correlacion clinica urgente.",
  "canal_origen": "Guardia_Emergencias"
}
```

* **Caso 1 (Rutina - T-02):** Usa un texto de receta ambulatoria:
  * Medicamento: *Enalapril 10 mg cada 12 horas*.
  * Diagnóstico: *Hipertensión arterial*.
  * Debe derivar a `Farmacia_Hospitalaria` con prioridad `Rutina`.
* **Caso 2 (Urgencia - T-03):** El informe tomográfico de TEP arriba mostrado.
  * Debe derivar a `Cola_Emergencia_Medica` con prioridad `Urgente` y alerta.
* **Caso 3 (Ambiguo HITL - T-04):** Texto escaneado borroso:
  * `"Texto borroso ilegible. Prescripcion no identificable. Firma médica no visible."`
  * Debe derivar a `Cola_Auditoria_Humana` con `requiere_auditoria_humana: true`.

---

### 🧠 [T-05 & T-06] IA con Google Gemini Multimodal (`backend-api/app/services/gemini.py`)

Para invocar el modelo Gemini usando la librería oficial `google-generativeai`:

```python
import os
import json
import google.generativeai as genai
from app.models.schemas import DatosClinicosExtraidos, Paciente, MedicoSolicitante

# Configurar API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT_SISTEMA = """
Eres un Agente Médico Experto en Triaje Documental Hospitalario.
Tu tarea es analizar el documento clínico recibido y extraer:
1. Datos del paciente (nombre, edad)
2. Médico solicitante (nombre, matrícula)
3. Diagnóstico principal y sospecha clínica
4. Código CIE-10 / ICD-10 correspondiente más exacto (ej. I26.9 para TEP)
5. Medicamentos prescritos con dosis
6. Nivel de gravedad (Rutina, Prioritario, Urgente)

Responde ÚNICAMENTE en formato JSON con la estructura solicitada.
"""

def invocar_gemini_multimodal(texto_documento: str, imagen_bytes: bytes = None):
    modelo = genai.GenerativeModel("gemini-1.5-flash")
    
    contenidos = [PROMPT_SISTEMA]
    if imagen_bytes:
        contenidos.append({"mime_type": "image/jpeg", "data": imagen_bytes})
    contenidos.append(f"DOCUMENTO CLÍNICO A ANALIZAR:\n{texto_documento}")
    
    respuesta = modelo.generate_content(
        contenidos,
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(respuesta.text)
```

---

### 🔄 [T-07] Lógica del Grafo Condicional (`backend-api/app/agent/graph.py`)

El grafo de decisión toma la extracción del LLM y ejecuta tres bifurcaciones clave:

```python
# Lógica de bifurcación condicional
if es_urgente and score_confianza >= 0.85:
    # Ruta Urgencias
    destino = DestinoPrincipalEnum.Cola_Emergencia_Medica
    prioridad = NivelPrioridadEnum.Urgente
    requiere_hitl = False
    alerta = {"canal": "Alerta_Guardia_Medica", "mensaje": "ALERTA CRÍTICA..."}
    subcarpeta_oci = "procesados/urgentes"

elif score_confianza < 0.85:
    # Ruta Human-in-the-Loop
    destino = DestinoPrincipalEnum.Cola_Auditoria_Humana
    prioridad = NivelPrioridadEnum.Prioritario
    requiere_hitl = True
    alerta = {"canal": "Alerta_Auditoria_Clinica", "mensaje": "CASO AMBIGUO..."}
    subcarpeta_oci = "auditoria_humana"

else:
    # Ruta Rutina
    destino = DestinoPrincipalEnum.Farmacia_Hospitalaria if es_receta else DestinoPrincipalEnum.Historia_Clinica_Electronica
    prioridad = NivelPrioridadEnum.Rutina
    requiere_hitl = False
    alerta = None
    subcarpeta_oci = "procesados/farmacia" if es_receta else "procesados/hce"
```

---

### ☁️ [T-08] Integración con OCI Object Storage (`backend-api/app/services/oci.py`)

El servicio de OCI soporta tres modos de trabajo para máxima flexibilidad:

1. **Modo Mock (por defecto en local):**  
   Si `OCI_MOCK_MODE=true` en `.env`, los archivos se guardan automáticamente en la carpeta local `data_mock_oci/`. ¡No necesitas cuenta de Oracle Cloud para programar!
2. **Modo Instance Principal (para la VM de OCI Always Free):**  
   No requiere archivo de claves. El código se autentica solo a través de la identidad de la VM de OCI:
   ```python
   import oci
   signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
   client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
   ```
3. **Modo Archivo Local (`~/.oci/config`):**  
   Si tienes credenciales personales de OCI configuradas en tu laptop.

---

### 🎨 [T-12, T-13, T-14] Frontend en React 18 + Vite (TypeScript)

El frontend de MediFlow está estandarizado en **React 18 con Vite y TypeScript** siguiendo la metodología Spec-First.

#### 1. Inicialización y Generación de Tipos
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install lucide-react

# Autogenerar los tipos TypeScript desde el contrato OpenAPI
./scripts/generate-api.sh
```

#### 2. Configurar Proxy de Desarrollo (`frontend/vite.config.ts`)
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 8501,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

#### 3. Implementación de la UI Clínica Split-Screen (`frontend/src/App.tsx`)
```tsx
import React, { useState } from 'react';
import { Activity, AlertOctagon, CheckCircle2, FileText, Send, ShieldAlert } from 'lucide-react';
import { components } from './types/api';

type TriajeResponse = components['schemas']['RespuestaTriaje'];

export default function App() {
  const [textoDoc, setTextoDoc] = useState('');
  const [resultado, setResultado] = useState<TriajeResponse | null>(null);
  const [cargando, setCargando] = useState(false);

  // Selector de Casos Demo Oficiales (T-12)
  const cargarCasoDemo = (caso: string) => {
    if (caso === 'tep') {
      setTextoDoc("HOSPITAL SANTA LUCIA - INFORME RADIOLOGICO\nPaciente: Carlos Eduardo Mendes, 52 años.\nEstudio: AngioTC de Torax con contraste.\nHallazgos: Defecto de llenado intraluminal bilateral oclusivo en ramas principales de arteria pulmonar.\nConclusion: Tromboembolismo Pulmonar Agudo (TEP) con signos de sobrecarga ventricular derecha.");
    } else if (caso === 'rutina') {
      setTextoDoc("CENTRO MEDICO SAN MARTIN - RECETA MEDICA\nPaciente: Maria Lopez, 45 años.\nDiagnostico: Hipertension Arterial Primaria (I10).\nPrescripcion: Enalapril 10mg comprimidos - Tomar 1 por la mañana por 30 dias.");
    } else if (caso === 'hitl') {
      setTextoDoc("CONSULTORIO PARTICULAR\nPaciente: Juan P... [manuscrito borroso]\nRx de... infiltrado dudoso en base... correlacionar con clinica.");
    }
  };

  // Enviar a la API FastAPI
  const ejecutarTriaje = async () => {
    setCargando(true);
    try {
      const res = await fetch('/api/v1/triaje', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          documento_id: `DOC-DEMO-${Date.now()}`,
          tipo_archivo: 'TEXTO',
          documento_texto: textoDoc,
          canal_origen: 'Portal_Web'
        })
      });
      const data: TriajeResponse = await res.json();
      setResultado(data);
    } catch (err) {
      console.error("Error al conectar con la API:", err);
    } finally {
      setCargando(false);
    }
  };

  // Acción Human-in-the-Loop 1-clic (T-14)
  const resolverHITL = async (aprobado: boolean) => {
    if (!resultado) return;
    await fetch(`/api/v1/auditoria/${resultado.documento_id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        auditor_id: "MED-AUDITOR-01",
        resolucion: aprobado ? "Aprobado" : "Rechazado",
        motivo: "Validado por médico auditor en panel HITL 1-clic"
      })
    });
    alert(aprobado ? "✅ Caso aprobado y archivado en OCI" : "❌ Caso rechazado");
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'Inter, sans-serif', backgroundColor: '#0F172A', color: '#F8FAFC', minHeight: '100vh' }}>
      {/* Cabecera y Métricas */}
      <header style={{ borderBottom: '1px solid #334155', paddingBottom: '16px', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px' }}>
          🏥 MediFlow — Triaje y Enrutamiento Clínico Autónomo
        </h1>
      </header>

      {/* Selector de Casos Demo (T-12) */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
        <button onClick={() => cargarCasoDemo('rutina')} style={{ padding: '8px 16px', borderRadius: '6px', background: '#1E293B', color: '#10B981', border: '1px solid #334155', cursor: 'pointer' }}>
          Caso 1: Receta Rutinaria
        </button>
        <button onClick={() => cargarCasoDemo('tep')} style={{ padding: '8px 16px', borderRadius: '6px', background: '#1E293B', color: '#DC2626', border: '1px solid #334155', cursor: 'pointer' }}>
          🚨 Caso 2: Urgencia Médica (TEP)
        </button>
        <button onClick={() => cargarCasoDemo('hitl')} style={{ padding: '8px 16px', borderRadius: '6px', background: '#1E293B', color: '#F59E0B', border: '1px solid #334155', cursor: 'pointer' }}>
          ⚠️ Caso 3: Ambiguo (HITL)
        </button>
      </div>

      {/* Layout Split-Screen (T-13) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Panel Izquierdo: Documento Fuente */}
        <div style={{ background: '#1E293B', padding: '20px', borderRadius: '8px', border: '1px solid #334155' }}>
          <h2 style={{ fontSize: '18px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={20} /> Documento Fuente
          </h2>
          <textarea
            value={textoDoc}
            onChange={(e) => setTextoDoc(e.target.value)}
            rows={12}
            style={{ width: '100%', background: '#0F172A', color: '#F8FAFC', border: '1px solid #334155', borderRadius: '6px', padding: '12px' }}
            placeholder="Pega el informe médico o selecciona un caso demo..."
          />
          <button
            onClick={ejecutarTriaje}
            disabled={cargando || !textoDoc}
            style={{ marginTop: '12px', width: '100%', padding: '12px', background: '#06B6D4', color: '#0F172A', fontWeight: 'bold', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
          >
            {cargando ? "Procesando con IA..." : "🚀 Ejecutar Triaje Clínico"}
          </button>
        </div>

        {/* Panel Derecho: Extracción y Triaje */}
        <div style={{ background: '#1E293B', padding: '20px', borderRadius: '8px', border: '1px solid #334155' }}>
          <h2 style={{ fontSize: '18px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={20} /> Diagnóstico y Enrutamiento
          </h2>
          {resultado ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <span style={{
                  padding: '6px 12px', borderRadius: '20px', fontWeight: 'bold',
                  background: resultado.clasificacion.nivel_prioridad === 'Urgente' ? '#DC2626' : resultado.clasificacion.nivel_prioridad === 'Prioritario' ? '#F59E0B' : '#10B981'
                }}>
                  {resultado.clasificacion.nivel_prioridad.toUpperCase()}
                </span>
                <span style={{ color: '#94A3B8' }}>Confianza: {(resultado.clasificacion.score_confianza_clasificacion * 100).toFixed(0)}%</span>
              </div>

              <p><strong>Paciente:</strong> {resultado.datos_extraidos?.paciente?.nombre || 'No identificado'}</p>
              <p><strong>Diagnóstico:</strong> {resultado.datos_extraidos?.diagnostico_principal || 'Pendiente'}</p>
              <p><strong>Código CIE-10:</strong> <code style={{ background: '#0F172A', padding: '2px 6px', borderRadius: '4px', color: '#06B6D4' }}>{resultado.datos_extraidos?.cie10_sugerido || 'N/A'}</code></p>
              <p><strong>Destino Asignado:</strong> {resultado.decision_enrutamiento.destino_principal}</p>

              {/* Panel Human-in-the-Loop si el caso es ambiguo (T-14) */}
              {resultado.decision_enrutamiento.requiere_auditoria_humana && (
                <div style={{ marginTop: '20px', padding: '16px', background: '#451A03', border: '1px solid #F59E0B', borderRadius: '6px' }}>
                  <h4 style={{ color: '#F59E0B', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <ShieldAlert size={18} /> Requiere Auditoría Médica (HITL)
                  </h4>
                  <p style={{ fontSize: '14px', marginBottom: '12px' }}>{resultado.decision_enrutamiento.justificacion_enrutamiento}</p>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={() => resolverHITL(true)} style={{ flex: 1, padding: '8px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                      ✅ Aprobar Extracción (1-clic)
                    </button>
                    <button onClick={() => resolverHITL(false)} style={{ flex: 1, padding: '8px', background: '#DC2626', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                      ❌ Rechazar
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p style={{ color: '#94A3B8', textAlign: 'center', marginTop: '40px' }}>Selecciona un caso y presiona "Ejecutar Triaje" para ver el resultado.</p>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

### 🚦 [T-15] Ejecución de Pruebas de Contrato Automatizadas

Para verificar que tus cambios respetan la especificación de la API:

```bash
# Ejecutar todas las pruebas de contrato de FastAPI
python3 -m pytest backend-api/tests/ -v
```

Debe mostrar:
```text
backend-api/tests/test_contract.py::test_health_check_contract PASSED
backend-api/tests/test_contract.py::test_triaje_urgencia_tep_contract PASSED
backend-api/tests/test_contract.py::test_triaje_hitl_ambiguo_contract PASSED
```

---

## 3. Checklist de Entrega para el Desarrollador (Antes de hacer PR)

Antes de hacer `git push` y abrir tu Pull Request:
1. [ ] Mi código sigue la especificación formal en [`specs/openapi.yaml`](file:///home/wigsdev/GitHub/mediflow/specs/openapi.yaml).
2. [ ] Ejecuté `pytest backend-api/tests/` y todas las pruebas pasaron.
3. [ ] No dejé contraseñas, secretos ni API keys en el código (usé variables en `.env`).
4. [ ] Mi commit sigue el formato Conventional Commits (ej. `feat(T-06): prompt de extraccion multimodal`).
5. [ ] Sincronicé mi rama con `main` antes de abrir el PR (`git merge main`).
