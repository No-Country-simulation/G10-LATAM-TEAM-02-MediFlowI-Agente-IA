from app.agent.clinical_catalog import TIPOS_DOCUMENTO_CLINICO, normalizar_tipo_documento


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
