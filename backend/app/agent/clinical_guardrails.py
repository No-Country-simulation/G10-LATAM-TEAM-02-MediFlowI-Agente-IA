"""
MediFlow — Guardrails de Seguridad Clínica Hospitalaria.

Define:
1. Filtro Fuera de Dominio (Out-of-Domain Gate).
2. Matriz de Señales de Alarma de Riesgo Vital (Red Flags) determinista.
3. Validación cruzada de coherencia semántica entre hallazgos y prioridad.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

from app.agent.clinical_catalog import normalizar_tipo_documento, TIPOS_DOCUMENTO_CLINICO


@dataclass(frozen=True)
class ReglaRedFlag:
    """Regla determinista para identificar afecciones de riesgo vital inminente."""
    nombre: str
    terminos_clave: tuple[str, ...]
    codigos_cie10: tuple[str, ...]
    prioridad_minima_esperada: str = "Urgente"
    patrones_negacion: tuple[str, ...] = (
        "se descarta",
        "sin signos de",
        "descarte de",
        "no presenta",
        "descartado",
        "negativo para",
        "sin evidencia de",
    )


# Catálogo determinista inmutable de patologías de riesgo vital crítico (Red Flags)
MATRIZ_RED_FLAGS: tuple[ReglaRedFlag, ...] = (
    ReglaRedFlag(
        nombre="Tromboembolismo Pulmonar (TEP)",
        terminos_clave=(
            "tromboembolismo pulmonar",
            "tep",
            "embolia pulmonar",
            "tromboembolia pulmonar",
            "tromboembolismo",
        ),
        codigos_cie10=("I26", "I26.0", "I26.9"),
    ),
    ReglaRedFlag(
        nombre="Infarto Agudo de Miocardio (IAM)",
        terminos_clave=(
            "infarto agudo de miocardio",
            "infarto de miocardio",
            "iam",
            "sindrome coronario agudo",
            "elevacion del st",
            "infarto agudo",
        ),
        codigos_cie10=("I21", "I21.0", "I21.1", "I21.2", "I21.3", "I21.4", "I21.9"),
    ),
    ReglaRedFlag(
        nombre="Shock / Colapso Hemodinámico",
        terminos_clave=(
            "shock septico",
            "shock cardiogenico",
            "shock hipovolemico",
            "shock anafilactico",
            "shock hemorragico",
            "colapso hemodinamico",
        ),
        codigos_cie10=("R57", "R57.0", "R57.1", "R57.2", "R57.8", "R57.9"),
    ),
    ReglaRedFlag(
        nombre="Paro Cardiorrespiratorio (PCR)",
        terminos_clave=(
            "paro cardiorrespiratorio",
            "paro cardiaco",
            "pcr",
            "asistolia",
            "fibrilacion ventricular",
        ),
        codigos_cie10=("I46", "I46.0", "I46.1", "I46.9"),
    ),
    ReglaRedFlag(
        nombre="Accidente Cerebrovascular (ACV / Ictus)",
        terminos_clave=(
            "accidente cerebrovascular",
            "acv",
            "ictus isquemico",
            "hemorragia subaracnoidea",
            "hemorragia intracerebral",
            "ataque cerebrovascular",
        ),
        codigos_cie10=("I63", "I63.9", "I64", "I60"),
    ),
    ReglaRedFlag(
        nombre="Hemorragia Masiva Exanguinante",
        terminos_clave=(
            "hemorragia masiva",
            "shock hemorragico",
            "hemorragia exanguinante",
            "sangrado masivo",
        ),
        codigos_cie10=("R58",),
    ),
    ReglaRedFlag(
        nombre="Neumotórax a Tensión",
        terminos_clave=(
            "neumotorax a tension",
            "neumotorax hipertensivo",
        ),
        codigos_cie10=("J93.0",),
    ),
)


def _normalizar_texto_busqueda(texto: str) -> str:
    """Elimina tildes, signos de puntuación y pasa a minúsculas para comparaciones semánticas."""
    sin_acentos = "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caracter)
    )
    return re.sub(r"[^a-z0-9]+", " ", sin_acentos.lower()).strip()


def es_documento_fuera_de_dominio(tipo_documento: str | None) -> bool:
    """
    Evalúa si un documento es ajeno al ámbito clínico o no debe entrar a colas operativas.
    Categorías consideradas fuera de dominio o ambiguas:
    - 'Otro', 'No_Clinico', 'Desconocido', o cualquier valor fuera del catálogo clínico.
    """
    if not tipo_documento or not isinstance(tipo_documento, str):
        return True

    normalizado = normalizar_tipo_documento(tipo_documento)
    
    # 'Otro' es el comodín para no clínicos, afiches, publicidad o desconocidos
    if normalizado == "Otro":
        return True

    # Comprobación contra catálogo clínico formal
    return normalizado not in TIPOS_DOCUMENTO_CLINICO


def evaluar_red_flags(
    hallazgos: list[str] | None = None,
    diagnostico: str | None = None,
    cie10: str | None = None,
    texto_completo: str | None = None,
) -> tuple[bool, str | None]:
    """
    Comprueba si existe alguna señal de alarma de riesgo vital (Red Flag).
    Retorna (es_red_flag, nombre_o_codigo_detectado).
    Considera el contexto de negación clínica defensiva ("se descarta", "sin signos de", etc.).
    """
    # 1. Verificar coincidencia por código CIE-10 exacto o prefijo
    cie10_clean = (cie10 or "").strip().upper()
    if cie10_clean:
        for regla in MATRIZ_RED_FLAGS:
            for cod in regla.codigos_cie10:
                if cie10_clean == cod or cie10_clean.startswith(f"{cod}."):
                    return True, f"CIE-10 {cie10_clean} ({regla.nombre})"

    # 2. Construir corpus de texto para búsqueda semántica
    corpus_partes = []
    if diagnostico:
        corpus_partes.append(diagnostico)
    if hallazgos:
        corpus_partes.extend(hallazgos)
    if texto_completo:
        corpus_partes.append(texto_completo)

    corpus_unificado = " . ".join(corpus_partes)
    if not corpus_unificado.strip():
        return False, None

    texto_normalizado = f" {_normalizar_texto_busqueda(corpus_unificado)} "

    # 3. Evaluar cada regla de Red Flag
    for regla in MATRIZ_RED_FLAGS:
        for termino in regla.terminos_clave:
            termino_norm = _normalizar_texto_busqueda(termino)
            patron = rf"\b{re.escape(termino_norm)}\b"
            match = re.search(patron, texto_normalizado)
            if match:
                # Verificar si está dentro de una cláusula de negación
                inicio = max(0, match.start() - 50)
                ventana_previa = texto_normalizado[inicio : match.start()]
                
                esta_negado = any(
                    _normalizar_texto_busqueda(neg) in ventana_previa
                    for neg in regla.patrones_negacion
                )
                
                if not esta_negado:
                    return True, f"{regla.nombre} ('{termino}')"

    return False, None


class ResultadoEvaluacionGuardrail(BaseModel):
    """Resultado formal de la evaluación de guardrails clínicos."""
    es_fuera_de_dominio: bool = False
    es_discordancia_critica: bool = False
    red_flag_detectada: str | None = None
    motivo_retencion: str | None = None
    score_confianza_ajustado: float | None = None
    destino_recomendado: str | None = None
    requiere_auditoria_humana: bool = False
