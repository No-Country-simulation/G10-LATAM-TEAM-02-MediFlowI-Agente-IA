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
    """Extrae texto con PyMuPDF y usa OCR sólo para PDFs escaneados."""
    pdf_bytes = base64.b64decode(base64_content)
    texto = _extraer_texto_pdf_pymupdf(pdf_bytes)
    return texto or _extraer_texto_pdf_ocr(pdf_bytes)


def _extraer_texto_pdf_pymupdf(pdf_bytes: bytes) -> str:
    """Obtiene la capa de texto embebida del PDF."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        paginas = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(paginas).strip()
    except ImportError:
        raise RuntimeError("PyMuPDF no está disponible para leer el PDF.") from None
    except Exception as exc:
        raise RuntimeError(f"No se pudo extraer texto del PDF: {exc}") from exc


def _extraer_texto_pdf_ocr(pdf_bytes: bytes) -> str:
    """Renderiza cada página y aplica Tesseract al PDF que no tiene capa textual."""
    try:
        import fitz
        import pytesseract
        from PIL import Image
    except ImportError:
        raise RuntimeError(
            "OCR no disponible: instale pytesseract y el binario Tesseract."
        ) from None

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        textos = []
        for page in doc:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            textos.append(pytesseract.image_to_string(image, lang="spa"))
        doc.close()
        return "\n".join(textos).strip()
    except Exception as exc:
        raise RuntimeError(f"No se pudo realizar OCR del PDF: {exc}") from exc
