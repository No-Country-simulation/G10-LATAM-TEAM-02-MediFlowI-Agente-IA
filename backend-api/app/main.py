"""
Aplicación Principal FastAPI para MediFlow
Expone la API REST definida estrictamente en specs/openapi.yaml
"""
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import (
    DocumentoClinicoInput,
    RespuestaTriaje,
    AlmacenamientoOCI,
    StatusTriajeEnum,
    StatusBackupEnum
)
from app.agent.graph import extraer_entidades_clinicas, evaluar_grafo_decision
from app.services.oci import oci_service

app = FastAPI(
    title="MediFlow API - Agente Autónomo para Triaje Clínico",
    description="API REST desarrollada para la Hackathon ONE Grupo 10 (Oracle & Alura)",
    version="1.0.0"
)

# Habilitar CORS para permitir llamadas desde la UI de React (Vite en puerto 8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Métricas en memoria para el dashboard
METRICAS = {
    "total_documentos_procesados": 0,
    "urgencias_criticas_detectadas": 0,
    "casos_derivados_hitl": 0
}

@app.get("/health", tags=["Monitoreo"])
def health_check():
    """Endpoint de verificación de salud (Smoke check en CI/CD y despliegue OCI)."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "services": {
            "gemini_llm": "connected",
            "oci_object_storage": "connected" if not oci_service.mock_mode else "mock_mode"
        }
    }

@app.post("/api/v1/triaje", response_model=RespuestaTriaje, status_code=status.HTTP_200_OK, tags=["Triaje Clínico"])
def procesar_triaje(doc: DocumentoClinicoInput):
    """
    Ingesta y triaje de documento clínico.
    Ejecuta el grafo de agentes y persiste en OCI Object Storage Always Free.
    """
    try:
        # 1. Extracción de entidades
        datos_extraidos = extraer_entidades_clinicas(doc)

        # 2. Grafo de decisión condicional
        clasificacion, decision, status_triaje, subcarpeta = evaluar_grafo_decision(doc, datos_extraidos)

        # 3. Persistencia segregada en OCI Object Storage
        ruta_oci = f"{subcarpeta}/{doc.documento_id}.json"
        
        # Construir payload de respuesta
        respuesta = RespuestaTriaje(
            status=status_triaje,
            documento_id=doc.documento_id,
            clasificacion=clasificacion,
            datos_extraidos=datos_extraidos,
            decision_enrutamiento=decision,
            almacenamiento_oci=AlmacenamientoOCI(
                bucket=oci_service.bucket_name,
                ruta_objeto=ruta_oci
            )
        )

        # Subir a OCI
        oci_res = oci_service.subir_documento(ruta_oci, respuesta.model_dump())
        respuesta.almacenamiento_oci.status_backup = StatusBackupEnum(oci_res.get("status_backup", "exito"))

        # Actualizar métricas
        METRICAS["total_documentos_procesados"] += 1
        destino_val = decision.destino_principal.value if hasattr(decision.destino_principal, "value") else str(decision.destino_principal)
        if destino_val == "Cola_Emergencia_Medica":
            METRICAS["urgencias_criticas_detectadas"] += 1
        if decision.requiere_auditoria_humana:
            METRICAS["casos_derivados_hitl"] += 1

        return respuesta

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el procesamiento del triaje: {str(e)}"
        )

@app.post("/api/v1/auditoria/{documento_id}", tags=["Human-in-the-Loop"])
def resolver_auditoria(documento_id: str, payload: dict):
    """
    Resolución médica Human-in-the-Loop para documentos en revisión.
    """
    nueva_ruta = f"procesados/auditados/{documento_id}.json"
    oci_service.subir_documento(nueva_ruta, payload)
    return {
        "status": "auditoria_completada",
        "documento_id": documento_id,
        "nueva_ruta_oci": nueva_ruta
    }

@app.get("/api/v1/metricas", tags=["Monitoreo"])
def obtener_metricas():
    """Obtiene estadísticas de triaje para la barra superior del Dashboard."""
    total = METRICAS["total_documentos_procesados"]
    hitl = METRICAS["casos_derivados_hitl"]
    pct_auto = round(((total - hitl) / total * 100), 1) if total > 0 else 100.0
    return {
        **METRICAS,
        "porcentaje_automatizacion": pct_auto
    }
