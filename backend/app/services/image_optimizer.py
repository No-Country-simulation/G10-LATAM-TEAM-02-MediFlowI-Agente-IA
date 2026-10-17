"""Compresión del payload que se envía a visión; el original no se modifica."""

import base64
import binascii
import io
from dataclasses import dataclass, field

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BASE64_BYTES = 350_000
MAX_IMAGE_SIDE = 1280
JPEG_QUALITY = 80


@dataclass(frozen=True)
class ImagenOptimizada:
    base64: str = field(repr=False)
    ancho: int
    alto: int


def optimizar_imagen(base64_content: str) -> ImagenOptimizada:
    """Limita el Base64 real, incluyendo el prefijo data URI, a menos de 350 KB."""
    try:
        raw = base64.b64decode(base64_content, validate=True)
        with Image.open(io.BytesIO(raw)) as source:
            if source.format not in {"PNG", "JPEG", "WEBP"}:
                # Conserva los formatos que admite el endpoint de upload de develop.
                raise ValueError("Formato de imagen no admitido")
            with ImageOps.exif_transpose(source) as oriented:
                with oriented.convert("RGBA") as rgba:
                    rgba.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE), Image.Resampling.LANCZOS)
                    image = Image.new("RGB", rgba.size, "white")
                    with rgba.getchannel("A") as alpha:
                        image.paste(rgba, mask=alpha)
        try:
            width, height = image.size
            while True:
                with image.resize((width, height), Image.Resampling.LANCZOS) as candidate:
                    with io.BytesIO() as buffer:
                        candidate.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
                        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
                if len(encoded) + len("data:image/jpeg;base64,") < MAX_BASE64_BYTES:
                    return ImagenOptimizada(encoded, width, height)
                if width == 1 and height == 1:
                    raise ValueError("No se pudo limitar el tamaño de la imagen")
                width, height = max(1, int(width * 0.85)), max(1, int(height * 0.85))
        finally:
            image.close()
    except (binascii.Error, UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("Imagen inválida o no procesable") from exc
