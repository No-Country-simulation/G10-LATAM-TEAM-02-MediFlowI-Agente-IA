"""
Grafo de Decisión Condicional y Agente de Triaje Clínico
Implementa el flujo condicional especificado en el pliego de la hackathon:
1. Nodo de Ingesta & Extracción (Gemini Multimodal / CIE-10)
2. Nodo de Evaluación de Confianza y Urgencia
3. Bifurcación Condicional (Conditional Edges):
   - Urgencia Médica -> Cola_Emergencia_Medica + Alerta
   - Baja Confianza (< 0.85) -> Cola_Auditoria_Humana (HITL)
   - Flujo Estándar -> Farmacia_Hospitalaria / Historia_Clinica_Electronica
"""
import os
import re
from typing import Dict, Any, Tuple
from app.models.schemas import (
    DocumentoClinicoInput,
    DatosClinicosExtraidos,
    ClasificacionDocumento,
    DecisionEnrutamiento,
    DestinoPrincipalEnum,
    NivelPrioridadEnum,
    StatusTriajeEnum,
    NotificacionAlerta,
    Paciente,
    MedicoSolicitante,
    Medicamento
)
from app.services.gemini import gemini_service

# Palabras clave clínicas de alta urgencia que activan el protocolo crítico
PALABRAS_CLAVE_URGENCIA = [
    "tromboembolismo", "tep", "infarto", "iam", "neumotorax", 
    "hemorragia", "shock", "paro", "diseccion aortica", "embolia pulmonar"
]

def extraer_entidades_clinicas(doc: DocumentoClinicoInput) -> DatosClinicosExtraidos:
    """
    Extrae entidades clínicas mediante Google Gemini 1.5 Flash.
    Si Gemini no está configurado o falla, aplica fallback automático a parser determinista.
    """
    # 1. Intentar extracción con Gemini LLM si está activo
    resultado_gemini = gemini_service.extraer_con_gemini(doc)
    if resultado_gemini is not None:
        return resultado_gemini

    # 2. Fallback determinista resiliente
    texto = doc.documento_texto or ""
    
    # Detección de paciente
    nombre_paciente = "Desconocido"
    edad_paciente = None
    match_paciente = re.search(r"Paciente:\s*([^,\.\n]+)(?:,\s*(\d+)\s*a[nñ]os)?", texto, re.IGNORECASE)
    if match_paciente:
        nombre_paciente = match_paciente.group(1).strip()
        if match_paciente.group(2):
            edad_paciente = int(match_paciente.group(2))

    # Detección de médico
    medico_nom = "No especificado"
    medico_mat = "No especificada"
    match_medico = re.search(r"M[eé]dico(?:\s+Solicitante)?:\s*(.*?)(?:\s+(?:MP|Mat|MN)\s*[:#]?\s*(\d+)|\.\s+[A-Z]|\n|$)", texto, re.IGNORECASE)
    if match_medico and match_medico.group(1).strip():
        medico_nom = match_medico.group(1).strip()
        if match_medico.group(2):
            medico_mat = match_medico.group(2).strip()

    # Detección de estudio o diagnóstico
    diagnostico = "Cuadro clínico a evaluar"
    cie10 = None
    if "tromboembolismo" in texto.lower() or "tep" in texto.lower():
        diagnostico = "Tromboembolismo Pulmonar Agudo (TEP)"
        cie10 = "I26.9"
    elif "hipertension" in texto.lower() or "presion" in texto.lower():
        diagnostico = "Hipertension Arterial Esencial"
        cie10 = "I10"
    elif "diabetes" in texto.lower():
        diagnostico = "Diabetes Mellitus Tipo 2"
        cie10 = "E11.9"

    estudio = None
    match_estudio = re.search(r"Estudio:\s*([^,\.\n]+)", texto, re.IGNORECASE)
    if match_estudio:
        estudio = match_estudio.group(1).strip()

    # Medicamentos si es receta
    medicamentos = []
    if "receta" in texto.lower() or "mg" in texto.lower() or "comprimidos" in texto.lower():
        match_meds = re.findall(r"([A-Za-z]+)\s+(\d+\s*mg[^\n,\.]*)", texto, re.IGNORECASE)
        for m_nom, m_dos in match_meds:
            medicamentos.append(Medicamento(nombre=m_nom.strip(), dosis=m_dos.strip()))

    return DatosClinicosExtraidos(
        paciente=Paciente(nombre=nombre_paciente, edad=edad_paciente),
        medico_solicitante=MedicoSolicitante(nombre=medico_nom, matricula=medico_mat),
        estudio_realizado=estudio,
        diagnostico_principal=diagnostico,
        cie10_sugerido=cie10,
        medicamentos=medicamentos if medicamentos else None
    )

def evaluar_grafo_decision(
    doc: DocumentoClinicoInput,
    datos: DatosClinicosExtraidos
) -> Tuple[ClasificacionDocumento, DecisionEnrutamiento, StatusTriajeEnum, str]:
    """
    Grafo de decisión con bifurcaciones condicionales:
    Retorna: (Clasificación, DecisiónEnrutamiento, Status, RutaSubcarpetaOCI)
    """
    texto = (doc.documento_texto or "").lower()
    es_urgente = any(palabra in texto for palabra in PALABRAS_CLAVE_URGENCIA)
    
    # Calcular score de confianza según legibilidad y completitud
    score_confianza = 0.99
    if "borroso" in texto or "ilegible" in texto or len(texto.strip()) < 30:
        score_confianza = 0.62

    # Bifurcación 1: Urgencia Médica Crítica
    if es_urgente and score_confianza >= 0.85:
        clasificacion = ClasificacionDocumento(
            tipo_documento="Informe de Estudio por Imagenes" if datos.estudio_realizado else "Informe Medico de Urgencias",
            especialidad="Radiologia / Neumonologia" if "pulmonar" in texto else "Emergentologia",
            nivel_prioridad=NivelPrioridadEnum.Urgente,
            score_confianza_clasificacion=score_confianza
        )
        decision = DecisionEnrutamiento(
            destino_principal=DestinoPrincipalEnum.Cola_Emergencia_Medica,
            requiere_auditoria_humana=False,
            justificacion_enrutamiento=f"Hallazgo critico de alta gravedad ({datos.diagnostico_principal}) detectado en paciente sintomatico.",
            notificacion_generada=NotificacionAlerta(
                canal="Alerta_Guardia_Medica",
                mensaje=f"ALERTA URGENTE: Informe critico de {datos.diagnostico_principal} para el paciente {datos.paciente.nombre_completo} en {doc.canal_origen}."
            )
        )
        return clasificacion, decision, StatusTriajeEnum.procesado, "procesados/urgentes"

    # Bifurcación 2: Ambigüedad o Baja Confianza (Human-in-the-Loop)
    if score_confianza < 0.85 or "auditoria" in texto:
        clasificacion = ClasificacionDocumento(
            tipo_documento="Documento Clinico Dudoso",
            especialidad="Medicina General / Revision",
            nivel_prioridad=NivelPrioridadEnum.Prioritario,
            score_confianza_clasificacion=score_confianza
        )
        decision = DecisionEnrutamiento(
            destino_principal=DestinoPrincipalEnum.Cola_Auditoria_Humana,
            requiere_auditoria_humana=True,
            justificacion_enrutamiento="Documento con baja legibilidad o datos clinicos incompletos. Derivado a auditoria medica.",
            notificacion_generada=NotificacionAlerta(
                canal="Alerta_Auditoria_Clinica",
                mensaje=f"CASO AMBIGUO: Documento {doc.documento_id} requiere validacion médica humana."
            )
        )
        return clasificacion, decision, StatusTriajeEnum.pendiente_auditoria, "auditoria_humana"

    # Bifurcación 3: Flujo Estándar de Rutina
    tipo_doc = "Receta Medica" if datos.medicamentos or "receta" in texto else "Informe de Estudio de Diagnostico"
    destino = DestinoPrincipalEnum.Farmacia_Hospitalaria if tipo_doc == "Receta Medica" else DestinoPrincipalEnum.Historia_Clinica_Electronica
    subcarpeta = "procesados/farmacia" if tipo_doc == "Receta Medica" else "procesados/hce"

    clasificacion = ClasificacionDocumento(
        tipo_documento=tipo_doc,
        especialidad="Clinica Medica / Farmacologia" if tipo_doc == "Receta Medica" else "Diagnostico General",
        nivel_prioridad=NivelPrioridadEnum.Rutina,
        score_confianza_clasificacion=score_confianza
    )
    decision = DecisionEnrutamiento(
        destino_principal=destino,
        requiere_auditoria_humana=False,
        justificacion_enrutamiento=f"Documento de rutina validado con exito y derivado a {destino.value}.",
        notificacion_generada=None
    )
    return clasificacion, decision, StatusTriajeEnum.procesado, subcarpeta
