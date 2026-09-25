"""
MediFlow — Entry point de la aplicación FastAPI.

Configura la app, registra routers y define middlewares.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import auth, documents, health, patients, triage, users
from app.api.v1 import settings as settings_router
from app.core.config import get_settings
from app.repositories.postgres_storage import DatabaseUnavailableError

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y cierre de la aplicación."""
    settings = get_settings()
    logger.info(
        "mediflow.inicio",
        version=settings.app_version,
        env=settings.app_env,
        llm=settings.llm_configured,
        oci=settings.oci_configured,
    )
    yield
    logger.info("mediflow.cierre")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="MediFlow — Agente Autónomo de Triaje Clínico",
        description=(
            "API REST del agente autónomo MediFlow para clasificación, extracción "
            "y enrutamiento de documentos clínicos usando LLMs multimodales y LangGraph.\n\n"
            "**Hackathon ONE G10 · Oracle Next Education & Alura**"
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    @app.exception_handler(DatabaseUnavailableError)
    async def database_unavailable_handler(
        _request: Request, exc: DatabaseUnavailableError
    ) -> JSONResponse:
        """Expone una indisponibilidad explícita sin simular resultados clínicos."""
        logger.error("mediflow.database.unavailable", error=str(exc))
        return JSONResponse(
            status_code=503,
            content={
                "detail": {
                    "error": "POSTGRESQL_NO_DISPONIBLE",
                    "mensaje": "PostgreSQL no está disponible temporalmente.",
                }
            },
        )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    api_prefix = "/api/v1"
    app.include_router(health.router)  # GET /health
    app.include_router(health.router, prefix=api_prefix)  # GET /api/v1/health
    app.include_router(triage.router, prefix=api_prefix)  # POST /api/v1/triage
    app.include_router(documents.router, prefix=api_prefix)  # GET|PATCH /api/v1/documents
    app.include_router(settings_router.router, prefix=api_prefix)  # GET|POST /api/v1/settings
    app.include_router(auth.router, prefix=api_prefix)  # POST /api/v1/auth/login, logout, me
    app.include_router(users.router, prefix=api_prefix)  # GET|POST|PUT /api/v1/users
    app.include_router(patients.router, prefix=api_prefix)  # GET|POST|PUT /api/v1/patients

    return app


app = create_app()
