"""
MediFlow — Entry point de la aplicación FastAPI.

Configura la app, registra routers y define middlewares.
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1 import triage, documents, health

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
    app.include_router(health.router)                           # GET /health
    app.include_router(health.router, prefix=api_prefix)        # GET /api/v1/health
    app.include_router(triage.router, prefix=api_prefix)       # POST /api/v1/triage
    app.include_router(documents.router, prefix=api_prefix)    # GET|PATCH /api/v1/documents

    return app


app = create_app()
