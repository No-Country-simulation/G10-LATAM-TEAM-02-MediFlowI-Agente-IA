"""Benchmark IA-09 opt-in: 20 imágenes sintéticas y Gemini real, sin PostgreSQL.

Desde la raíz: .venv/Scripts/python infrastructure/scripts/benchmark_pipeline_fusion.py
La clave se lee de GOOGLE_API_KEY del entorno o del .env local, nunca de argumentos.
"""

import argparse
import asyncio
import base64
import io
import json
import math
import os
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = 20


def resumir_latencias(milliseconds: list[float]) -> dict:
    """Percentil por rango más cercano; incluye el primer pase sin calentamiento."""
    if len(milliseconds) != SAMPLES:
        raise ValueError("Se requieren exactamente 20 muestras válidas")
    ordered = sorted(milliseconds)
    p50 = ordered[math.ceil(0.50 * SAMPLES) - 1]
    p95 = ordered[math.ceil(0.95 * SAMPLES) - 1]
    return {
        "p50_ms": round(p50, 3),
        "p95_ms": round(p95, 3),
        "max_ms": round(max(milliseconds), 3),
        "cumple_p95_menor_8s": p95 < 8000,
    }


def imagenes_sinteticas() -> list[str]:
    """Documentos con texto, sin pacientes reales ni identificadores clínicos."""
    from PIL import Image, ImageDraw, ImageFont

    font_path = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/arial.ttf"
    font = (
        ImageFont.truetype(str(font_path), 25)
        if font_path.exists()
        else ImageFont.load_default(size=25)
    )
    cases = [
        [
            "INFORME CLINICO SINTETICO IA09",
            "Hemograma completo.",
            "Resultados dentro de rangos normales.",
            "Sin hallazgos patologicos.",
            "Control de seguimiento. Prioridad: Rutina.",
        ],
        [
            "INFORME CLINICO SINTETICO IA09",
            "Tomografia de torax.",
            "TEP agudo. Tromboembolismo pulmonar.",
            "Se solicita correlacion clinica urgente.",
            "Prioridad consignada: Urgente.",
        ],
        [
            "DOCUMENTO SINTETICO IA09",
            "Informacion clinica insuficiente.",
            "No se consigna diagnostico ni estudio.",
            "Requiere revision humana.",
            "Prioridad consignada: Ambiguo.",
        ],
    ]
    results = []
    for lines in cases:
        with Image.new("RGB", (1600, 1200), "white") as image, io.BytesIO() as buffer:
            draw = ImageDraw.Draw(image)
            for index, line in enumerate(lines):
                draw.text((70, 80 + index * 65), line, font=font, fill="black")
            image.save(buffer, format="PNG")
            results.append(base64.b64encode(buffer.getvalue()).decode())
    return results


class ProveedorMedido:
    def __init__(self, service):
        self.service = service
        self.calls = 0

    async def completar_imagen(self, prompt, imagen_base64):
        self.calls += 1
        return await self.service.completar_imagen(prompt, imagen_base64)

    async def completar(self, prompt):
        raise RuntimeError(
            "El benchmark no admite llamadas LLM adicionales al pase de visión"
        )


def verificar_caso_sintetico(result, index: int) -> None:
    """Comprobaciones mínimas conocidas del corpus, sin confundirlas con validación clínica."""
    expected = ("Rutina", "Urgente", "Ambiguo")[index % 3]
    if result.clasificacion.nivel_prioridad != expected:
        raise ValueError("La prioridad no coincide con el documento sintético")
    data = result.datos_extraidos
    if data.medicamentos or (
        data.paciente
        and any(
            (
                data.paciente.nombre,
                data.paciente.documento_identidad,
                data.paciente.historia_clinica,
                data.paciente.edad,
            )
        )
    ):
        raise ValueError("Se inventaron datos ausentes del corpus sintético")
    if expected == "Urgente":
        diagnostic = (data.diagnostico_principal or "").lower()
        if "tromboembol" not in diagnostic and "tep" not in diagnostic:
            raise ValueError("No se conservó el diagnóstico crítico explícito")
        if result.decision_enrutamiento.destino_principal != "Cola_Emergencia_Medica":
            raise ValueError("La urgencia sintética no llegó a emergencias")
    if (
        expected == "Rutina"
        and "hemograma" not in (data.estudio_realizado or "").lower()
    ):
        raise ValueError("No se conservó el estudio explícito")
    if (
        expected == "Ambiguo"
        and not result.decision_enrutamiento.requiere_auditoria_humana
    ):
        raise ValueError("El caso insuficiente no llegó a revisión humana")


async def medir(model: str | None, pause_seconds: float = 0) -> dict:
    if not math.isfinite(pause_seconds) or not 0 <= pause_seconds <= 60:
        raise ValueError("La pausa entre documentos debe estar entre 0 y 60 segundos")
    # Se ejecuta en un proceso propio: jamás usa la BD de desarrollo ni sus pacientes.
    os.environ["DATABASE_URL"] = ""
    os.environ["LANGSMITH_TRACING"] = "false"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    sys.path.insert(0, str(ROOT / "backend"))
    from app.core.config import Settings

    settings = Settings(_env_file=ROOT / "backend/.env")
    if model:
        settings = settings.model_copy(update={"gemini_model": model})
    report = {
        "fecha_utc": datetime.now(UTC).isoformat(),
        "modelo": settings.gemini_model,
        "muestras_previstas": SAMPLES,
        "muestras_validas": 0,
        "alcance": "grafo completo; incluye compresión; sin persistencia, HTTP ni SSE",
        "corpus": "3 documentos sintéticos legibles, 20 pases secuenciales, sin calentamiento",
        "pausa_entre_documentos_segundos": pause_seconds,
        "langgraph": version("langgraph"),
        "langchain_google_genai": version("langchain-google-genai"),
        "salida_fusion": "JSON Schema nativo",
        "thinking_level_fusion": (
            "low"
            if settings.gemini_model.removeprefix("models/").startswith("gemini-3")
            else "predeterminado"
        ),
        "estado": "pendiente_credencial",
        "latencias_ms": [],
        "errores": [],
        "p50_ms": None,
        "p95_ms": None,
        "max_ms": None,
        "cumple_p95_menor_8s": False,
        "verificaciones_corpus": "prioridad, estudio/diagnóstico explícitos, destino y ausencia de datos inventados",
    }
    if not settings.google_api_key or settings.google_api_key.startswith("your-"):
        return report
    from app.agent.graph import ejecutar_triage
    from app.services.llm_service import LLMService

    settings = settings.model_copy(
        update={"database_url": "", "openai_api_key": "", "allow_mock_llm": False}
    )
    service = LLMService(settings)
    if service.proveedor != "gemini":
        report["estado"] = "gemini_no_disponible"
        return report
    provider = ProveedorMedido(service)
    images = imagenes_sinteticas()
    for index in range(SAMPLES):
        if index and pause_seconds:
            # Respeta la cuota sin descontar tiempo de ninguna ejecución del grafo.
            await asyncio.sleep(pause_seconds)
        before = provider.calls
        start = perf_counter()
        try:
            result = await ejecutar_triage(
                documento_id=f"BENCH-IA09-{index + 1:02d}",
                tipo_archivo="IMAGEN",
                documento_base64=images[index % len(images)],
                llm_service=provider,
            )
            elapsed = (perf_counter() - start) * 1000
            if (
                result.error_mensaje
                or provider.calls - before != 1
                or result.documento_base64 is not None
            ):
                raise RuntimeError("Resultado de fusión inválido")
            verificar_caso_sintetico(result, index)
            report["latencias_ms"].append(round(elapsed, 6))
        except Exception as exc:  # noqa: BLE001 - Un fallo invalida el benchmark y queda registrado sin datos sensibles.
            report["errores"].append({"muestra": index + 1, "tipo": type(exc).__name__})
    report["muestras_validas"] = len(report["latencias_ms"])
    report["invocaciones_vision"] = provider.calls
    if report["errores"]:
        report["estado"] = "fallo_funcional"
        return report
    report.update(resumir_latencias(report["latencias_ms"]))
    report["estado"] = "aprobado" if report["cumple_p95_menor_8s"] else "fuera_objetivo"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", help="Modelo Gemini explícito; por defecto usa la configuración"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / ".venv/ia09-benchmark.json"
    )
    parser.add_argument(
        "--pause-seconds",
        type=float,
        default=0,
        help="Pausa fuera del grafo entre documentos para respetar la cuota",
    )
    args = parser.parse_args()
    report = asyncio.run(medir(args.model, args.pause_seconds))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["estado"] == "aprobado" else 2


if __name__ == "__main__":
    raise SystemExit(main())
