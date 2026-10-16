"""El benchmark no acredita latencia con muestras incompletas o credenciales ausentes."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "infrastructure/scripts/benchmark_pipeline_fusion.py"
spec = importlib.util.spec_from_file_location("ia09_benchmark", SCRIPT)
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


def test_percentiles_por_rango_mas_cercano_y_umbral_estricto():
    result = benchmark.resumir_latencias([float(i * 100) for i in range(20)])
    assert result == {
        "p50_ms": 900.0,
        "p95_ms": 1800.0,
        "max_ms": 1900.0,
        "cumple_p95_menor_8s": True,
    }
    assert benchmark.resumir_latencias([8000.0] * 20)["cumple_p95_menor_8s"] is False


def test_benchmark_no_acepta_menos_de_20_muestras():
    with pytest.raises(ValueError):
        benchmark.resumir_latencias([10.0])


@pytest.mark.parametrize("pause", [-1, 61, float("nan"), float("inf")])
async def test_benchmark_rechaza_pausas_invalidas(pause):
    with pytest.raises(ValueError, match="pausa"):
        await benchmark.medir(None, pause)


async def test_sin_clave_no_acredita_el_objetivo_ni_invoca_llm(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "your-test-placeholder")
    result = await benchmark.medir(None)
    assert result["estado"] == "pendiente_credencial"
    assert result["p95_ms"] is None
    assert result["muestras_validas"] == 0
    assert result["cumple_p95_menor_8s"] is False


def test_benchmark_rechaza_prioridad_incorrecta_y_alucinaciones():
    from app.agent.state import AgentState

    result = AgentState(documento_id="SINTETICO", tipo_archivo="IMAGEN")
    result.clasificacion.nivel_prioridad = "Rutina"
    result.datos_extraidos.estudio_realizado = "Hemograma completo"
    benchmark.verificar_caso_sintetico(result, 0)
    with pytest.raises(ValueError, match="prioridad"):
        benchmark.verificar_caso_sintetico(result, 1)
    from app.agent.state import PacienteState

    result.datos_extraidos.paciente = PacienteState(nombre="Inventado")
    with pytest.raises(ValueError, match="inventaron"):
        benchmark.verificar_caso_sintetico(result, 0)
