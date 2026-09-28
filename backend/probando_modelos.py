"""
Script ejecutable para probar los modelos Pydantic auto-generados (US-01).

Uso:
    cd backend
    python probando_modelos.py
"""

import sys
from pathlib import Path

# Garantizar que el directorio backend esté en el PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from app._generated.models import (
    Clasificacion,
    DatosExtraidos,
    DecisionEnrutamiento,
    DiagnosticoEntidad,
    DocumentoClinico,
    EntidadesMedicas,
    Paciente,
    ResultadoTriaje,
)


def probar_modelos():
    print("=" * 60)
    print("[+] PROBANDO MODELOS PYDANTIC GENERADOS DESDE OPENAPI 3.1")
    print("=" * 60)

    # 1. Crear Entidades Médicas (NER clínico)
    entidades = EntidadesMedicas(
        diagnosticos=[
            DiagnosticoEntidad(
                texto="Sindrome Coronario Agudo",
                cie10="I24.9",
                es_principal=True,
            )
        ],
        hallazgos_criticos=["Elevacion ST en ECG", "Troponinas elevadas"],
        score_ner=0.95,
    )

    # El schema independiente no se envía como campo de DatosExtraidos.
    serializado = entidades.model_dump_json()
    assert EntidadesMedicas.model_validate_json(serializado) == entidades
    print("EntidadesMedicas independiente:", serializado)

    # 2. Crear Resultado de Triaje completo
    triaje = ResultadoTriaje(
        status="procesado",
        documento_id="DOC-CLIN-2026-0001",
        clasificacion=Clasificacion(
            tipo_documento="Informe Clínico",
            especialidad="Cardiologia",
            nivel_prioridad="Urgente",
            score_confianza_clasificacion=0.96,
        ),
        datos_extraidos=DatosExtraidos(
            paciente=Paciente(nombre="Juan Perez", edad=65),
            diagnostico_principal="Sindrome Coronario Agudo",
            cie10_sugerido="I24.9",
        ),
        decision_enrutamiento=DecisionEnrutamiento(
            destino_principal="Cola_Emergencia_Medica",
            requiere_auditoria_humana=False,
            justificacion_enrutamiento="Gravedad alta asignada por riesgo coronario.",
        ),
        tiempo_procesamiento_ms=1150,
    )

    print("\n[OK] 1. Objeto ResultadoTriaje creado exitosamente:")
    print(f"   * Documento ID: {triaje.documento_id}")
    print(f"   * Status: {triaje.status}")
    print(f"   * Prioridad: {triaje.clasificacion.nivel_prioridad.root}")
    print(
        f"   * Confianza Clasificacion: {triaje.clasificacion.score_confianza_clasificacion * 100}%"
    )
    print(f"   * Destino: {triaje.decision_enrutamiento.destino_principal}")
    print(f"   * Diagnostico: {triaje.datos_extraidos.diagnostico_principal}")

    # 3. Crear una solicitud de documento clínico
    doc_req = DocumentoClinico(
        documento_id="DOC-REQ-2026-0001",
        tipo_archivo="PDF",
        documento_base64="JVBERi0xLjQKJ...",
        canal_origen="Guardia_Emergencias",
        metadata={"paciente_id": "PAC-9988"},
    )

    print("\n[OK] 2. Objeto DocumentoClinico creado exitosamente:")
    print(f"   * ID Documento: {doc_req.documento_id}")
    print(f"   * Tipo Archivo: {doc_req.tipo_archivo}")
    print(f"   * Canal Origen: {doc_req.canal_origen}")
    print(f"   * ID Paciente: {doc_req.metadata.get('paciente_id')}")

    # 4. Exportar a JSON (como lo enviaría la API REST)
    print("\n[OK] 3. Serializacion a JSON valida:")
    print(triaje.model_dump_json(indent=2))

    print("\n[OK] Ejemplos de triaje y entidades serializados correctamente.")
    print("=" * 60)


if __name__ == "__main__":
    probar_modelos()
