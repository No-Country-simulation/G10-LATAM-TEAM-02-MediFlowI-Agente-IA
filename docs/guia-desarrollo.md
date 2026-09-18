# 🛠️ MediFlow — Guía de Desarrollo y Recetario Técnico
**Manual de Referencia y Snippets para Desarrolladores del Equipo**  
*Hackathon ONE Grupo 10 (Oracle Next Education & Alura)*  
*Versión:* 2.0.0  

---

## 🎯 Propósito de este Documento

Este manual acompaña al [Backlog Unificado (`docs/backlog.md`)](backlog.md). Si estás trabajando en una tarea técnica (`T-01` a `T-13`), consulta esta guía para:
1. Copiar fragmentos de código listos para usar (*snippets* probados y alineados a la arquitectura).
2. Entender cómo conectar tu módulo con el resto del sistema sin romper contratos.
3. Conocer exactamente qué archivos te corresponde `[CREAR]` o `[MODIFICAR]`.
4. Resolver dudas frecuentes de forma autónoma sin bloqueos.

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
# Levanta la API en el puerto 8000
docker compose up -d

# Verificar salud de la API
curl http://localhost:8000/health
# {"status":"ok","version":"1.0.0","services":{"gemini_llm":"connected","oci_object_storage":"mock_mode"}}
```

---

## 2. Guía por Tareas Técnicas del Backlog

---

### 🧪 [T-02] Datasets Clínicos de Prueba (`datasets/`)
* **Rol:** QA & Datasets Engineer
* **Acción:** `[CREAR]` `datasets/caso_1_estandar_receta.json`, `datasets/caso_2_urgencia_tep.json`, `datasets/caso_3_ambiguo_hitl.json`

Los datasets son archivos JSON que simulan las solicitudes de entrada a la API. Deben colocarse en la carpeta `datasets/`:

#### Estructura Canónica de Entrada (`DocumentoClinicoInput`):
```json
{
  "documento_id": "DOC-CLIN-2026-8942",
  "tipo_archivo": "PDF",
  "documento_texto": "HOSPITAL SANTA LUCIA - INFORME RADIOLOGICO. Paciente: Carlos Eduardo Mendes, 52 anos. Medico Solicitante: Dra. Renata Silveira MP 145892. Estudio: Tomografia de Torax con contraste. CONCLUSION: Cuadro compatible con Tromboembolismo Pulmonar Agudo (TEP). Se sugiere correlacion clinica urgente.",
  "canal_origen": "Guardia_Emergencias"
}
```

* **Caso 1 (Rutina - `caso_1_estandar_receta.json`):** Simula receta de consulta externa:
  * Paciente: *María López, 45 años*.
  * Medicamento: *Enalapril 10 mg cada 12 horas por 30 días*.
  * Diagnóstico: *Hipertensión arterial primaria*.
  * Resultado esperado: Deriva a `Farmacia_Hospitalaria` con prioridad `Rutina` y `requiere_auditoria_humana: false`.
* **Caso 2 (Urgencia - `caso_2_urgencia_tep.json`):** Informe tomográfico oficial del pliego:
  * Paciente: *Carlos Eduardo Mendes, 52 años*.
  * Diagnóstico: *Tromboembolismo Pulmonar Agudo (TEP / CIE-10: I26.9)*.
  * Resultado esperado: Deriva a `Cola_Emergencia_Medica` con prioridad `Urgente` y objeto `notificacion_generada`.
* **Caso 3 (Ambiguo HITL - `caso_3_ambiguo_hitl.json`):** Documento borroso o incompleto:
  * Texto: `"Paciente: Juan P... [manuscrito ilegible]. Rx de torax... dudoso infiltrado. Firma no legible."`
  * Resultado esperado: Deriva a `Cola_Auditoria_Humana` con `requiere_auditoria_humana: true` y `score_confianza < 0.85`.

---

### 🧠 [T-03 & T-04] Modelos Pydantic y Agente Gemini Multimodal
* **Rol:** AI & Prompt Engineer / Backend
* **Acción:**
  - `[ESTADO: DONE]` `backend-api/app/models/schemas.py` (Modelos Pydantic v2 sincronizados con OpenAPI)
  - `[CREAR]` `backend-api/app/agent/prompts.py`
  - `[MODIFICAR]` `backend-api/app/services/gemini.py`

#### 1. Prompt de Sistema Médico (`backend-api/app/agent/prompts.py`):
```python
PROMPT_SISTEMA_MEDICO = """
Eres un Agente Médico Experto en Triaje Documental Hospitalario y Codificación CIE-10.
Tu tarea es analizar el documento clínico recibido (texto o imagen escaneada) y extraer estructuradamente:
1. Datos del paciente (nombre completo, edad estimada o exacta).
2. Médico solicitante (nombre, matrícula o registro profesional).
3. Diagnóstico principal y sospecha diagnóstica.
4. Código CIE-10 / ICD-10 más específico (ejemplo: I26.9 para Tromboembolismo Pulmonar Agudo, I10 para Hipertensión, E11 para Diabetes).
5. Medicamentos prescritos con posología.
6. Nivel de gravedad sugerido (Rutina, Prioritario, Urgente).

DIRECTIVAS CRÍTICAS:
- Cero alucinación: Si un dato no figura o es ilegible, coloca null o indica 'No especificado'.
- Si el documento contiene hallazgos críticos de riesgo vital (TEP, infarto, shock), el nivel de gravedad DEBE ser 'Urgente'.
- Responde ÚNICAMENTE en formato JSON plano compatible con el esquema DatosClinicosExtraidos.
"""
```

#### 2. Invocación de Google Gemini (`backend-api/app/services/gemini.py`):
```python
import os
import json
import google.generativeai as genai
from app.agent.prompts import PROMPT_SISTEMA_MEDICO

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def invocar_gemini_multimodal(texto_documento: str, imagen_bytes: bytes = None):
    modelo = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    
    contenidos = [PROMPT_SISTEMA_MEDICO]
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

### 🔄 [T-05] Lógica del Grafo Condicional (`backend-api/app/agent/graph.py`)
* **Rol:** Backend Engineer
* **Acción:** `[MODIFICAR]` `backend-api/app/agent/graph.py`

El grafo de decisión toma la extracción del LLM y ejecuta tres bifurcaciones clave:

```python
# Lógica de bifurcación condicional en app/agent/graph.py
if es_urgente and score_confianza >= 0.85:
    # Ruta Urgencias Vitales
    destino = DestinoPrincipalEnum.Cola_Emergencia_Medica
    prioridad = NivelPrioridadEnum.Urgente
    requiere_hitl = False
    alerta = {
        "canal": "Alerta_Guardia_Medica",
        "mensaje": "🚨 ALERTA CRÍTICA: Tromboembolismo Pulmonar Agudo detectado. Requiere atención inmediata."
    }
    subcarpeta_oci = "procesados/urgentes"

elif score_confianza < 0.85:
    # Ruta Human-in-the-Loop (Auditoría Médica)
    destino = DestinoPrincipalEnum.Cola_Auditoria_Humana
    prioridad = NivelPrioridadEnum.Prioritario
    requiere_hitl = True
    alerta = {
        "canal": "Alerta_Auditoria_Clinica",
        "mensaje": "⚠️ REVISIÓN REQUERIDA: Documento con baja legibilidad o datos incompletos."
    }
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

### ⚙️ [T-06] Automatización y Alertas Hospitalarias en n8n
* **Rol:** Workflow & DevOps Engineer
* **Acción:** `[MODIFICAR]` `docker-compose.yml`, `[CREAR]` `workflows/mediflow_triaje_workflow.json`

#### 1. Servicio n8n en `docker-compose.yml`:
```yaml
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: mediflow-n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=America/Lima
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

#### 2. Workflow n8n (`workflows/mediflow_triaje_workflow.json`):
* **Webhook Node:** `POST /webhook/triaje-clinico`.
* **HTTP Request Node:** Llama a `http://backend-api:8000/api/v1/triaje`.
* **IF Switch Node:** Evalúa `json.clasificacion.nivel_prioridad === 'Urgente'`.
* **Alert Node:** Despacha mensaje a canal Slack / Discord o webhook de guardia hospitalaria.

---

### 🎨 [T-11 & T-07] Frontend en React 18 + Vite (Dashboard y HITL)
* **Rol:** Frontend Engineer
* **Acción:**
  - `[MODIFICAR]` `frontend/package.json`, `frontend/vite.config.ts`
  - `[CREAR]` `frontend/src/App.tsx`, `frontend/src/index.css` (T-11)
  - `[CREAR]` `frontend/src/components/PanelHITL.tsx` (T-07)

#### 1. Inicialización y Autogeneración de Tipos
```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install lucide-react

# Autogenerar los tipos TypeScript desde el contrato OpenAPI
./scripts/generate-api.sh
```

#### 2. Proxy de Desarrollo (`frontend/vite.config.ts`)
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

#### 3. Panel Human-in-the-Loop (`frontend/src/components/PanelHITL.tsx`)
```tsx
import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, XCircle } from 'lucide-react';

interface PanelHITLProps {
  documentoId: string;
  motivoAmbiguedad?: string;
  onResuelto: () => void;
}

export const PanelHITL: React.FC<PanelHITLProps> = ({ documentoId, motivoAmbiguedad, onResuelto }) => {
  const [enviando, setEnviando] = useState(false);

  const resolverAuditoria = async (resolucion: 'Aprobado' | 'Rechazado') => {
    setEnviando(true);
    try {
      await fetch(`/api/v1/auditoria/${documentoId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          auditor_id: 'AUDITOR-MED-01',
          resolucion: resolucion,
          motivo: resolucion === 'Aprobado' ? 'Validado por auditoría médica 1-clic' : 'Documento rechazado por ilegibilidad'
        })
      });
      onResuelto();
    } catch (e) {
      console.error(e);
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div style={{ marginTop: '20px', padding: '16px', background: '#451A03', border: '1px solid #F59E0B', borderRadius: '6px' }}>
      <h4 style={{ color: '#F59E0B', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <ShieldAlert size={18} /> Requiere Auditoría Médica (HITL)
      </h4>
      <p style={{ fontSize: '14px', marginBottom: '12px' }}>{motivoAmbiguedad || 'Documento derivado para validación clínica manual.'}</p>
      <div style={{ display: 'flex', gap: '10px' }}>
        <button onClick={() => resolverAuditoria('Aprobado')} disabled={enviando} style={{ flex: 1, padding: '10px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
          ✅ Aprobar Extracción (1-clic)
        </button>
        <button onClick={() => resolverAuditoria('Rechazado')} disabled={enviando} style={{ flex: 1, padding: '10px', background: '#DC2626', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
          ❌ Rechazar
        </button>
      </div>
    </div>
  );
};
```

---

### ☁️ [T-09] Persistencia en OCI Object Storage (`backend-api/app/services/oci.py`)
* **Rol:** Cloud & OCI Engineer
* **Acción:** `[MODIFICAR]` `backend-api/app/services/oci.py`

El servicio de OCI soporta tres modos de trabajo:
1. **Modo Mock (por defecto en local):** Si `OCI_MOCK_MODE=true` en `.env`, los archivos se guardan localmente en `data_mock_oci/` replicando la jerarquía del bucket:
   - `data_mock_oci/recibidos/`
   - `data_mock_oci/procesados/urgentes/`
   - `data_mock_oci/procesados/farmacia/`
   - `data_mock_oci/auditoria_humana/`
2. **Modo Instance Principal (para la VM de OCI Always Free):**  
   No requiere claves en disco. La VM se autentica mediante su rol IAM:
   ```python
   import oci
   signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
   client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
   ```

---

### ☁️ [T-10] Despliegue en OCI Compute VM Ampere A1 (Always Free)
* **Rol:** Cloud & DevOps Engineer
* **Acción:** `[CREAR]` `docs/oci_deployment_guide.md`, `[CREAR]` `scripts/deploy-oci.sh`

#### Recursos Always Free de Oracle Cloud:
* **VM Compute:** VM.Standard.A1.Flex (4 OCPU, 24 GB RAM, Ubuntu 22.04 LTS).
* **Puertos a Abrir en Ingress Rules (VCN Security List):**
  - `8000` (FastAPI backend)
  - `8501` (React Frontend)
  - `5678` (n8n Automation)
* **IAM Dynamic Group:** Regla de coincidencia `instance.compartment.id = '<compartment_ocid>'` con política `Allow dynamic-group <group_name> to manage objects in compartment <compartment_name>`.

---

### 🚦 [T-08] Ejecución de Pruebas de Contrato Automatizadas
* **Rol:** QA & Datasets Engineer / Backend
* **Acción:** `[MODIFICAR]` `backend-api/tests/test_contract.py`

Para verificar que el sistema cumple la especificación formal y las reglas clínicas:

```bash
# Ejecutar todas las pruebas con reporte detallado
python3 -m pytest backend-api/tests/ -v
```

Debe mostrar:
```text
backend-api/tests/test_contract.py::test_health_check_contract PASSED
backend-api/tests/test_contract.py::test_triaje_urgencia_tep_contract PASSED
backend-api/tests/test_contract.py::test_triaje_hitl_ambiguo_contract PASSED
```

---

### 📚 [T-12 & T-13] Documentación Final, Pitch y Video Demo
* **Rol:** Team Leader, QA & Equipo Completo
* **Acción:** `[MODIFICAR]` `README.md`, `[CREAR]` `docs/pitch_demo_script.md`

1. **`README.md`:** Debe sintetizar el impacto clínico, badges de CI, arquitectura visual en Mermaid, instrucciones de un solo comando (`docker compose up -d`) y evidencia de los 3 casos clínicos.
2. **`docs/pitch_demo_script.md`:** Estructura del video de 5 minutos:
   - *Minuto 0:00 - 1:00:* El problema del triaje hospitalario y cuello de botella documental.
   - *Minuto 1:00 - 2:30:* Demo del Caso 2 (Urgencia TEP en vivo con alerta crítica inmediata).
   - *Minuto 2:30 - 3:30:* Demo del Caso 3 (Caso ambiguo con validación médica HITL en 1-clic).
   - *Minuto 3:30 - 4:30:* Demostración de persistencia y segregación en OCI Object Storage.
   - *Minuto 4:30 - 5:00:* Cierre, impacto y stack tecnológico.

---

## 3. Checklist de Entrega para el Desarrollador (Antes de hacer PR)

Antes de hacer `git push` y abrir tu Pull Request:
1. [ ] Mi código sigue la especificación formal en [`specs/openapi.yaml`](file:///home/wigsdev/GitHub/mediflow/specs/openapi.yaml).
2. [ ] Ejecuté `pytest backend-api/tests/` y todas las pruebas pasaron sin advertencias.
3. [ ] No dejé contraseñas, secretos ni API keys en el código (usé variables en `.env`).
4. [ ] Mi commit sigue el formato Conventional Commits (ej. `feat(T-04): prompt de extraccion multimodal`).
5. [ ] Sincronicé mi rama con la rama base antes de abrir el PR (`git merge develop`).
