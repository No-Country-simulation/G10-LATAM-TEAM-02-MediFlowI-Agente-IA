# 🏥 MediFlow — Resumen Arquitectónico y Flujos de Triaje del Sistema

Este documento proporciona la especificación completa, diagramas de secuencia y flujos de trabajo detallados de **todos los procesos de negocio, técnicos y clínicos de Triaje Autónomo** que componen el sistema **MediFlow (Agente Autónomo de Triaje Clínico Multimodal)** (RF-01 al RF-20).

---

## 📌 1. Mapa Global del Agente Autónomo de Triaje (LangGraph)

```mermaid
flowchart TD
    Start(["📥 Ingesta de Documento (PDF, Imagen, Texto, JSON)"]) --> Node1

    subgraph LangGraph ["🤖 Grafo de Estado del Agente (5 Nodos LangGraph)"]
        Node1["1. Nodo Ingestion\n(OCR / Visión LLM / Extraer Texto Raw)"] --> Node2["2. Nodo Extraction\n(Extracción Paciente, Médico, Diagnóstico, CIE-10)"]
        Node2 --> Node3["3. Nodo Classification\n(Tipo Doc, Especialidad, Nivel Prioridad)"]
        Node3 --> Node4["4. Nodo Confidence\n(Cálculo Score Confianza 0.0 - 1.0)"]
        Node4 --> Node5["5. Nodo Routing\n(Lógica de Enrutamiento & Justificación)"]
    end

    Node5 --> ScoreCheck{"¿Score Confianza >= 0.85?"}

    ScoreCheck -- "Sí (Certeza Alta)" --> PriorityCheck{"¿Nivel de Prioridad?"}
    ScoreCheck -- "No (Confianza Baja)" --> AuditQueue["👨‍⚕️ Cola Auditoría Humana\n(status: pendiente_auditoria, HITL=True)"]

    PriorityCheck -- "Urgente" --> EmergencyQueue["🚨 Cola Emergencia Médica\n(Notificación Inmediata, HITL=False)"]
    PriorityCheck -- "Rutina" --> RoutineQueue["📋 Cola Rutina\n(Procesado Automático, HITL=False)"]
    PriorityCheck -- "Ambiguo" --> AuditQueue

    EmergencyQueue & RoutineQueue & AuditQueue --> DBStore[("🗄️ Persistencia en PostgreSQL\ndocumentos_triaje + cola_procesamiento")]
    DBStore --> LinkPatient["👤 Asociación Automática a Paciente por DNI / HC (RF-08 / RF-09)"]
    LinkPatient --> End(["🏁 Fin del Triaje"])
```

---

## 🔬 2. Detalle Profundo Nodo por Nodo del Grafo de Triaje

### 1️⃣ Nodo 1: `ingestion` (Normalización y Visión Multimodal)
- **Entrada**: Archivo subido (PDF, Imagen PNG/JPG, Texto plano, o JSON) y `canal_origen`.
- **Lógica**:
  - Si es texto plano o JSON, extrae directamente la cadena de caracteres.
  - Si es PDF o Imagen, ejecuta el módulo de visión multimodal (Gemini / Claude OCR) para convertir el documento clínico manuscrito o escaneado en `texto_extraido`.
- **Salida en AgentState**: `texto_extraido`, `nodos_ejecutados = ["ingestion"]`.

### 2️⃣ Nodo 2: `extraction` (Extracción de Entidades Médicas & CIE-10)
- **Entrada**: `texto_extraido`.
- **Lógica Prompt Médica**: El LLM analiza el texto clínico y genera un JSON Pydantic estructurado:
  - `paciente`: `{nombre, edad, id_externo (DNI/HC)}`.
  - `medico_solicitante`: `{nombre, matricula}`.
  - `estudio_realizado`: Descripción del análisis o prueba.
  - `diagnostico_principal`: Hallazgo patológico o motivo de consulta.
  - `cie10_sugerido`: Código estándar de clasificación internacional de enfermedades (ej. `D64.9 Anemia`, `J18.9 Neumonía`, `Z01.8`).
  - `hallazgos_clave`: Lista de observaciones o constantes vitales alteradas.
- **Salida en AgentState**: `datos_extraidos`, `nodos_ejecutados = ["ingestion", "extraction"]`.

### 3️⃣ Nodo 3: `classification` (Especialidad y Prioridad Clínica)
- **Entrada**: `datos_extraidos` y `texto_extraido`.
- **Lógica de Clasificación**:
  - `tipo_documento`: Receta Médica, Informe de Laboratorio, Radiografía/Imagen, Epicrisis, Carta de Derivación.
  - `especialidad`: Cardiología, Neumología, Hematología, Medicina General, Traumatología, etc.
  - `nivel_prioridad`:
    - **`Urgente`**: Valores críticos de laboratorio, riesgo vital, infartos, neumonías graves, hemorragias o alteraciones severas.
    - **`Rutina`**: Controles periódicos, recetas estándar, análisis de seguimiento normal.
    - **`Ambiguo`**: Múltiples diagnósticos contradictorios, falta de datos críticos o texto parcialmente ilegible.
- **Salida en AgentState**: `clasificacion`, `nodos_ejecutados = ["ingestion", "extraction", "classification"]`.

### 4️⃣ Nodo 4: `confidence` (Score Multivariante de Confianza)
- **Entrada**: `clasificacion` y `datos_extraidos`.
- **Algoritmo de Scoring**: Evalúa 4 factores ponderados:
  $$\text{Score} = 0.35 \cdot C_{\text{paciente}} + 0.25 \cdot C_{\text{diagnostico}} + 0.20 \cdot C_{\text{cie10}} + 0.20 \cdot C_{\text{claridad}}$$
  - Si faltan datos clave (ej. sin diagnóstico o sin paciente), el score penaliza por debajo de `0.70`.
  - Si todos los campos son coherentes y claros, el score alcanza valores entre `0.85` y `1.00`.
- **Salida en AgentState**: `score_confianza_clasificacion`, `nodos_ejecutados = ["ingestion", "extraction", "classification", "confidence"]`.

### 5️⃣ Nodo 5: `routing` (Enrutamiento Autónomo & Justificación)
- **Entrada**: Estado consolidado del agente.
- **Matriz de Reglas de Enrutamiento**:

| Nivel de Prioridad | Score de Confianza | Destino Principal | Requiere Auditoría Humana (`HITL`) | Estado del Documento |
| :--- | :--- | :--- | :--- | :--- |
| **Urgente** | $\ge 0.85$ | `Cola_Emergencia_Medica` | `False` | `procesado` (Notificación Urgente) |
| **Rutina** | $\ge 0.85$ | `Cola_Rutina` | `False` | `procesado` |
| **Ambiguo** | Cualquier Score | `Cola_Auditoria_Humana` | `True` | `pendiente_auditoria` |
| Cualquier Prioridad | $< 0.85$ | `Cola_Auditoria_Humana` | `True` | `pendiente_auditoria` |

- **Salida en AgentState**: `decision_enrutamiento` con `destino_principal`, `requiere_auditoria_humana`, `justificacion_enrutamiento` y `notificacion_generada`.

---

## 🔄 3. Diagramas de Secuencia Detallados por Flujo

### 🔐 Flujo A: Autenticación, Login y Control de Acceso RBAC (RF-01 al RF-05)

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario (Personal Clínico)
    participant UI as React UI (/login)
    participant API as FastAPI (/api/v1/auth)
    participant Sec as Security (PBKDF2)
    participant DB as PostgreSQL (mediflow_dev)

    U->>UI: Ingresa DNI (8 cifras) y Contraseña
    UI->>API: POST /api/v1/auth/login {documento_identidad, password}
    API->>DB: Consulta usuario por documento_identidad
    DB-->>API: Retorna hash, salt, rol y estado_usuario
    API->>Sec: verify_password(password, stored_hash, salt)
    
    alt Credenciales Inválidas o Usuario Inactivo
        Sec-->>API: False
        API-->>UI: HTTP 401 Unauthorized / Credenciales inválidas
        UI-->>U: Muestra alerta de error
    else Credenciales Válidas
        Sec-->>API: True
        API->>Sec: create_access_token(user_data)
        Sec-->>API: Retorna access_token (mf_session_...)
        API-->>UI: HTTP 200 OK {access_token, user, mensaje}
        UI->>UI: Guarda token en AuthContext / localStorage
        UI-->>U: Redirecciona al Dashboard / Consola según Rol
    end
```

---

### 📥 Flujo B: Ingesta Multicanal y Triaje Autónomo en LangGraph (RF-10 al RF-13)

```mermaid
sequenceDiagram
    autonumber
    actor Op as Operador / Recepcionista
    participant UI as React UI (/triaje o /documentos/nuevo)
    participant API as FastAPI (/api/v1/triage)
    participant LG as LangGraph Agent (5 Nodos)
    participant LLM as LLM Multimodal (Gemini / Claude)
    participant DB as PostgreSQL (tabla documentos_triaje)
    participant Storage as Almacenamiento Físico (LOCAL / OCI)

    Op->>UI: Sube documento (PDF / Imagen / Texto)
    UI->>API: POST /api/v1/triage (Multipart/Form-Data)
    API->>Storage: Guarda archivo físico según modo configurado (LOCAL u OCI)
    API->>LG: Invoca ejecutor ejecutor.ainvoke(initial_state)

    rect rgb(240, 248, 255)
        note over LG,LLM: Ejecución del Grafo de Estado de 5 Nodos
        LG->>LG: 1. Nodo Ingestion (OCR / Extracción limpia)
        LG->>LLM: 2. Nodo Extraction (Extrae paciente, médico, estudio, diagnóstico, CIE-10)
        LLM-->>LG: Retorna JSON estructurado de datos extraídos
        LG->>LLM: 3. Nodo Classification (Categoriza especialidad y nivel de prioridad)
        LLM-->>LG: Retorna especialidad y prioridad (Urgente / Rutina / Ambiguo)
        LG->>LG: 4. Nodo Confidence (Calcula score multivariante de 0.0 a 1.0)
        LG->>LG: 5. Nodo Routing (Determina destino y si requiere auditoría HITL)
    end

    LG-->>API: Retorna Estado Final del Agente (AgentState)
    API->>DB: Guarda resultado en documentos_triaje y cola_procesamiento (ON CONFLICT UPSERT)
    API-->>UI: HTTP 200 OK {documento_id, clasificacion, datos_extraidos, decision_enrutamiento}
    UI-->>Op: Despliega tarjeta visual de triaje con prioridad y justificación
```

---

### 👤 Flujo C: Registro, Búsqueda y Asociación de Pacientes (RF-06 al RF-09)

```mermaid
sequenceDiagram
    autonumber
    actor Op as Operador / Trabajador
    participant UI as React UI (/pacientes)
    participant API as FastAPI (/api/v1/patients)
    participant Repo as PatientRepository (Asyncpg)
    participant DB as PostgreSQL (tablas pacientes y documentos_triaje)

    rect rgb(255, 250, 240)
        note over Op,DB: RF-06 & RF-07 — Registro y Búsqueda de Pacientes
        Op->>UI: Ingresa DNI, HC o Nombres en la barra de búsqueda
        UI->>API: GET /api/v1/patients?search=789456
        API->>Repo: list_patients(search="789456")
        Repo->>DB: SELECT * FROM pacientes WHERE numero_documento ILIKE '%789456%'...
        DB-->>Repo: Retorna registros encontrados
        Repo-->>API: Lista de pacientes
        API-->>UI: HTTP 200 OK {total, items}
        UI-->>Op: Muestra resultados filtrados en tiempo real
    end

    rect rgb(240, 255, 240)
        note over Op,DB: RF-08 & RF-09 — Expediente y Asociación Documental (Search Select)
        Op->>UI: Haz clic en "Documentos" del paciente
        UI->>API: GET /api/v1/patients/{id}/documents
        API->>DB: Consulta documentos asociados + unlinked documents (WHERE paciente_id IS NULL)
        DB-->>API: Retorna expediente documental + metadatos IA conservados (RF-09)
        API-->>UI: HTTP 200 OK {documentos, datos_extraidos_ia}
        UI-->>Op: Abre modal con Search Select interactivo filtrado solo con no asociados
        Op->>UI: Selecciona un documento del buscador y clic en "Vincular Documento"
        UI->>API: POST /api/v1/patients/{id}/documents/{doc_id}/associate
        API->>DB: UPDATE documentos_triaje SET paciente_id = $1 WHERE documento_id = $2
        DB-->>API: Confirma actualización (UPDATE 1)
        API-->>UI: HTTP 200 OK {message}
        UI-->>Op: Actualiza el expediente del paciente al instante
    end
```

---

### 🩺 Flujo D: Auditoría Médica e Intervención Humana (HITL) (RF-14)

```mermaid
sequenceDiagram
    autonumber
    actor Aud as Auditor Médico
    participant UI as React UI (/auditoria)
    participant API as FastAPI (/api/v1/documents)
    participant DB as PostgreSQL (tablas auditorias_hitl y documentos_triaje)

    Aud->>UI: Ingresa a la consola de Auditoría (/auditoria)
    UI->>API: GET /api/v1/documents?estado=pendiente_auditoria
    API->>DB: SELECT * FROM documentos_triaje WHERE status = 'pendiente_auditoria'
    DB-->>API: Lista de casos pendientes
    API-->>UI: HTTP 200 OK {items}
    UI-->>Aud: Muestra tabla de documentos que requieren revisión humana
    Aud->>UI: Selecciona un caso y revisa la sugerencia del Agente IA
    Aud->>UI: Registra decisión (Aprobar / Reclasificar / Rechazar) + Comentario
    UI->>API: PATCH /api/v1/documents/{id} {decision, auditor_id, comentario, nueva_clasificacion}
    API->>DB: INSERT INTO auditorias_hitl (...) & UPDATE documentos_triaje SET status = 'procesado'
    DB-->>API: Confirma transacción
    API-->>UI: HTTP 200 OK {mensaje}
    UI-->>Aud: Notifica aprobación y remueve el caso de la cola de pendientes
```

---

### ⚙️ Flujo E: Configuración del Modo de Almacenamiento Dual (RF-15 al RF-17)

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Administrador
    participant UI as React UI (/configuracion)
    participant API as FastAPI (/api/v1/settings)
    participant DB as PostgreSQL (tabla configuracion_sistema)

    Admin->>UI: Ingresa a Configuración (/configuracion)
    UI->>API: GET /api/v1/settings
    API->>DB: SELECT valor FROM configuracion_sistema WHERE clave = 'modo_almacenamiento'
    DB-->>API: Retorna 'LOCAL' o 'OCI'
    API-->>UI: HTTP 200 OK {modo_almacenamiento, oci_configurado}
    UI-->>Admin: Despliega banner informativo "PostgreSQL es la Fuente Única de Verdad"
    Admin->>UI: Cambia el selector a 'OCI' (o 'LOCAL') y clic en "Guardar Configuración"
    UI->>API: POST /api/v1/settings {modo_almacenamiento: "OCI"}
    
    alt Credenciales OCI Incompletas en .env
        API-->>UI: HTTP 400 Bad Request / Faltan variables OCI en .env
        UI-->>Admin: Muestra error y revierte selección a 'LOCAL'
    else Credenciales Válidas
        API->>DB: UPDATE configuracion_sistema SET valor = 'OCI' WHERE clave = 'modo_almacenamiento'
        DB-->>API: Confirma actualización
        API-->>UI: HTTP 200 OK {message: "Configuración actualizada correctamente"}
        UI-->>Admin: Muestra notificación de éxito
    end
```

---

## 📋 Resumen Sintético de Módulos y Flujos

| Módulo | Nombre del Módulo | Requerimientos | Principales Entidades / Tablas | Componentes Frontend Clave |
| :--- | :--- | :--- | :--- | :--- |
| **Módulo 1** | Autenticación y RBAC | RF-01 al RF-05 | `usuarios`, `rol_enum`, `estado_usuario_enum` | `/login`, `/usuarios` (`UsersManagementView.tsx`) |
| **Módulo 2** | Pacientes y Expedientes | RF-06 al RF-09 | `pacientes`, `documentos_triaje.paciente_id` | `/pacientes` (`PatientsManagementView.tsx` + `SearchableDocSelect`) |
| **Módulo 3** | Ingesta y Triaje LangGraph | RF-10 al RF-13 | `documentos_triaje`, `cola_procesamiento` | `/triaje` (`TriageConsoleView.tsx`), `/documentos/nuevo` |
| **Módulo 4** | Auditoría Médica HITL | RF-14 | `auditorias_hitl` | `/auditoria` (`Audit.tsx`), `/auditoria/:id` (`AuditDetail.tsx`) |
| **Módulo 5** | Configuración & Almacenamiento | RF-15 al RF-17 | `configuracion_sistema` | `/configuracion` (`StorageSettingsView.tsx`) |
| **Módulo 6** | Dashboard y Documentación | RF-18 al RF-20 | `documentos_triaje`, `notificaciones` | `/dashboard` (`Dashboard.tsx`), `/documentos`, `/documentacion` |
