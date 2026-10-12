"""
MediFlow — Módulo de Resolución de Identidad Clínica de Pacientes.

Responsabilidad:
Coteja identificadores clínicos oficiales (DNI e Historia Clínica) contra PostgreSQL
para validar identidad, prevenir asignación errónea de documentos médicos y detectar
conflictos de identidad clínica (DNI perteneciente a un paciente y HC a otro).
"""

from typing import Any, Literal

from pydantic import BaseModel, Field
import structlog

from app.repositories import patient_repository
from app.repositories.postgres_storage import DatabaseUnavailableError

logger = structlog.get_logger(__name__)


class ResultadoMatchingPaciente(BaseModel):
    """Resultado del cotejo de identificadores clínicos."""

    estado: Literal["asociado", "sin_coincidencia", "conflicto"]
    paciente: dict[str, Any] | None = None
    es_conflicto: bool = False
    motivo: str | None = None
    dni_evaluado: str | None = None
    hc_evaluada: str | None = None


async def verificar_identidad_paciente(
    dni: str | None,
    historia_clinica: str | None,
) -> ResultadoMatchingPaciente:
    """
    Coteja el DNI y la Historia Clínica contra PostgreSQL usando patient_repository.

    Reglas Clínicas:
    1. Si DNI y HC corresponden a diferentes pacientes -> 'conflicto'.
    2. Si DNI o HC corresponden a un único paciente -> 'asociado'.
    3. Si ninguno existe en BD o ambos son None -> 'sin_coincidencia'.
    4. NUNCA inferir identidad basada en nombres si los identificadores oficiales discrepan.
    5. Manejo resiliente de fallos de BD (DatabaseUnavailableError).
    """
    dni_limpio = dni.strip() if isinstance(dni, str) and dni.strip() else None
    hc_limpia = (
        historia_clinica.strip()
        if isinstance(historia_clinica, str) and historia_clinica.strip()
        else None
    )

    if not dni_limpio and not hc_limpia:
        return ResultadoMatchingPaciente(
            estado="sin_coincidencia",
            paciente=None,
            es_conflicto=False,
            motivo="Sin identificadores proporcionados",
            dni_evaluado=None,
            hc_evaluada=None,
        )

    try:
        res = await patient_repository.resolver_paciente_por_identificadores(
            dni_limpio, hc_limpia
        )
        estado = res.get("estado", "sin_coincidencia")
        paciente = res.get("paciente")

        if estado == "conflicto":
            logger.warning(
                "patient_matcher.conflicto_detectado",
                dni=dni_limpio,
                hc=hc_limpia,
            )
            return ResultadoMatchingPaciente(
                estado="conflicto",
                paciente=None,
                es_conflicto=True,
                motivo="Discrepancia entre DNI e Historia Clínica: pertenecen a pacientes distintos.",
                dni_evaluado=dni_limpio,
                hc_evaluada=hc_limpia,
            )

        if estado == "asociado" and paciente:
            logger.info(
                "patient_matcher.paciente_asociado",
                paciente_id=str(paciente.get("id")),
                dni=dni_limpio,
                hc=hc_limpia,
            )
            return ResultadoMatchingPaciente(
                estado="asociado",
                paciente=paciente,
                es_conflicto=False,
                motivo="Paciente asociado unívocamente por identificador oficial.",
                dni_evaluado=dni_limpio,
                hc_evaluada=hc_limpia,
            )

        return ResultadoMatchingPaciente(
            estado="sin_coincidencia",
            paciente=None,
            es_conflicto=False,
            motivo="No se encontró paciente registrado con los identificadores suministrados.",
            dni_evaluado=dni_limpio,
            hc_evaluada=hc_limpia,
        )

    except DatabaseUnavailableError as exc:
        logger.error("patient_matcher.db_error", error=str(exc))
        return ResultadoMatchingPaciente(
            estado="sin_coincidencia",
            paciente=None,
            es_conflicto=False,
            motivo=f"Base de datos no disponible: {exc}",
            dni_evaluado=dni_limpio,
            hc_evaluada=hc_limpia,
        )
    except Exception as exc:
        logger.error("patient_matcher.error_inesperado", error=str(exc))
        return ResultadoMatchingPaciente(
            estado="sin_coincidencia",
            paciente=None,
            es_conflicto=False,
            motivo=f"Error inesperado al cotejar paciente: {exc}",
            dni_evaluado=dni_limpio,
            hc_evaluada=hc_limpia,
        )
