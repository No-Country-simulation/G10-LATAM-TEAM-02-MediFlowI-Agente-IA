"""
Nodo: ingestion
Responsabilidad: Extraer texto plano del documento de entrada.
Soporta: texto directo, PDF (PyMuPDF), imagen (Gemini Vision).
"""

import base64
import structlog
from app.agent.state import AgentState

logger = structlog.get_logger(__name__)


async def node_ingestion(state: AgentState) -> dict:
    """
    Extrae texto del documento según su tipo.
    Retorna un dict con los campos a actualizar en el AgentState.
    """
    logger.info("nodo.ingestion.inicio", documento_id=state.documento_id)
    texto_extraido = None

    try:
        if state.documento_texto:
            # Caso más simple: texto ya disponible
            texto_extraido = state.documento_texto.strip()

        elif state.tipo_archivo == "PDF" and state.documento_base64:
            texto_extraido = _extraer_texto_pdf(state.documento_base64)

        elif state.tipo_archivo == "IMAGEN" and state.documento_base64:
            # Para imágenes, la extracción real la hará el LLM en el nodo extraction
            # Aquí solo validamos que el base64 sea válido
            base64.b64decode(state.documento_base64, validate=True)
            texto_extraido = None  # Gemini procesará la imagen directo

        else:
            texto_extraido = ""

        logger.info(
            "nodo.ingestion.completado",
            documento_id=state.documento_id,
            caracteres=len(texto_extraido or ""),
        )

        return {
            "texto_extraido": texto_extraido,
            "nodos_ejecutados": state.nodos_ejecutados + ["ingestion"],
        }

    except Exception as exc:
        logger.error("nodo.ingestion.error", documento_id=state.documento_id, error=str(exc))
        return {
            "texto_extraido": "",
            "error_mensaje": f"Error en ingestion: {exc}",
            "nodos_ejecutados": state.nodos_ejecutados + ["ingestion"],
        }


def _extraer_texto_pdf(base64_content: str) -> str:
    """Extrae texto de un PDF codificado en base64 usando PyMuPDF."""
    try:
        import fitz  # PyMuPDF

        pdf_bytes = base64.b64decode(base64_content)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        paginas = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(paginas).strip()
    except ImportError:
        logger.warning("pymupdf.no_disponible", fallback="texto_vacio")
        return ""
    except Exception as exc:
        raise RuntimeError(f"No se pudo extraer texto del PDF: {exc}") from exc
