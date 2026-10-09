import json
import re
from pathlib import Path

import pytest

from app.agent.clinical_catalog import (
    TIPOS_DOCUMENTO_CLINICO,
    normalizar_tipo_documento,
    validar_y_completar_cie10,
)


def test_catalogo_clinico_es_amplio_y_sin_duplicados():
    assert len(TIPOS_DOCUMENTO_CLINICO) >= 12
    assert len(TIPOS_DOCUMENTO_CLINICO) == len(set(TIPOS_DOCUMENTO_CLINICO))


def test_normaliza_aliases_y_contexto_del_llm():
    assert normalizar_tipo_documento("Analítica de Laboratorio") == "Informe de Laboratorio"
    assert (
        normalizar_tipo_documento("informe de estudio por imagenes")
        == "Informe de Estudio por Imágenes"
    )
    assert normalizar_tipo_documento("Receta Médica - Consulta Externa") == "Receta Médica"
    assert normalizar_tipo_documento(None) == "Otro"


@pytest.mark.parametrize(
    "codigo, descripcion",
    [
        ("I21.9", "Infarto agudo del miocardio, sin otra especificación"),
        ("I26.9", "Embolia pulmonar sin mención de corazón pulmonar agudo"),
        ("J18.9", "Neumonía, no especificada"),
    ],
)
def test_cie10_completa_descripcion_del_catalogo(codigo, descripcion):
    assert validar_y_completar_cie10(codigo) == {
        "valido": True,
        "codigo": codigo,
        "descripcion": descripcion,
    }


@pytest.mark.parametrize("codigo", ["I219", "i21.9", " i219 ", "I21.9"])
def test_cie10_normaliza_solo_variaciones_sintacticas(codigo):
    assert validar_y_completar_cie10(codigo)["codigo"] == "I21.9"


def test_cie10_admite_categorias_de_tres_caracteres():
    assert validar_y_completar_cie10("i10") == {
        "valido": True,
        "codigo": "I10",
        "descripcion": "Hipertensión esencial (primaria)",
    }


@pytest.mark.parametrize(
    "codigo",
    [None, "", "  ", 219, "I21.99", "I2.19", "I21-9", "I 219", "I21.9 / J18.9", "A00.8", "ZZZ"],
)
def test_cie10_rechaza_codigos_invalidos_sin_inventar_un_reemplazo(codigo):
    assert validar_y_completar_cie10(codigo) == {
        "valido": False,
        "codigo": None,
        "descripcion": None,
    }


def test_cie10_no_expone_un_resultado_mutable_compartido():
    first = validar_y_completar_cie10("I219")
    first["descripcion"] = "Descripción adulterada"
    assert validar_y_completar_cie10("I219")["descripcion"] != first["descripcion"]


def test_catalogo_cie10_completo_tiene_codigos_y_descripciones_consistentes():
    path = Path(__file__).parents[1] / "app/agent/data/cie10_catalog.json"
    pares = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=list)
    assert len(pares) == 11008
    assert len(pares) == len({codigo for codigo, _ in pares})
    for codigo, descripcion in pares:
        assert re.fullmatch(r"[A-Z][0-9]{2}(?:\.[0-9])?", codigo)
        assert descripcion.strip() and "\ufffd" not in descripcion
        assert validar_y_completar_cie10(codigo) == {
            "valido": True,
            "codigo": codigo,
            "descripcion": descripcion,
        }
        assert validar_y_completar_cie10(codigo.replace(".", "").lower())["codigo"] == codigo
