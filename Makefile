# MediFlow — Makefile
# Comandos unificados para desarrollo, generación SDD, testing y despliegue.

.PHONY: help validate generate dev dev-docker docker-up docker-down test test-backend test-contract docs build clean

# ── Default ──────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  MediFlow — Comandos disponibles"
	@echo "  ================================"
	@echo ""
	@echo "  SDD (Spec-Driven Development):"
	@echo "    make validate     Valida specs/openapi.yaml con Spectral"
	@echo "    make generate     Genera _generated/ desde el spec"
	@echo ""
	@echo "  Desarrollo:"
	@echo "    make dev          Levanta backend + frontend sin Docker"
	@echo "    make dev-docker   Levanta todo con Docker Compose (hot-reload)"
	@echo "    make docs         Abre Swagger UI en el browser"
	@echo ""
	@echo "  Testing:"
	@echo "    make test         Todos los tests (unit + integration + contract)"
	@echo "    make test-backend Solo tests del backend (pytest)"
	@echo "    make test-contract Contract tests desde OpenAPI spec (schemathesis)"
	@echo ""
	@echo "  Producción:"
	@echo "    make build        Build completo (Docker)"
	@echo "    make docker-up    Construye y levanta el stack completo"
	@echo "    make docker-down  Detiene el stack sin borrar los volúmenes"
	@echo "    make clean        Limpia contenedores y volúmenes"
	@echo ""

# ── SDD ───────────────────────────────────────────────────────────────────────
validate:
	@echo "🔍 Validando specs/openapi.yaml..."
	python infrastructure/scripts/validate_spec.py

generate:
	@echo "⚙️  Generando código desde specs/openapi.yaml..."
	python infrastructure/scripts/generate.py

# ── Desarrollo local (sin Docker) ────────────────────────────────────────────
dev:
	@echo "🚀 Levantando MediFlow en modo desarrollo..."
	@echo "   Backend:  http://localhost:8000"
	@echo "   Frontend: http://localhost:5173"
	@echo "   Docs:     http://localhost:8000/docs"
	@echo ""
	@start cmd /k "cd backend && pip install -e .[dev] -q && uvicorn app.main:app --reload --port 8000"
	@start cmd /k "cd frontend && npm install --silent && npm run dev"

# ── Base de Datos & Migraciones ──────────────────────────────────────────────
db:
	@echo "🐘 Levantando PostgreSQL 17 + pgAdmin..."
	docker compose -f infrastructure/docker/docker-compose.db.yml up -d

migrate:
	@echo "🔄 Aplicando migraciones de Alembic..."
	cd backend && alembic upgrade head

# ── Desarrollo con Docker Compose ────────────────────────────────────────────
dev-docker:
	@echo "🐳 Levantando con Docker Compose (dev)..."
	docker compose -f infrastructure/docker/docker-compose.dev.yml up --build

# ── Abrir Swagger UI ─────────────────────────────────────────────────────────
docs:
	@echo "📚 Abriendo Swagger UI..."
	start http://localhost:8000/docs

# ── Testing ───────────────────────────────────────────────────────────────────
test: test-backend test-contract

test-backend:
	@echo "🧪 Ejecutando tests del backend..."
	cd backend && python -m pytest tests/ -v --tb=short

test-contract:
	@echo "🔗 Ejecutando contract tests (schemathesis)..."
	cd backend && python -m schemathesis.cli run ../specs/openapi.yaml --url http://localhost:8000/api/v1 --header "X-API-Key: mediflow-dev-secret-key-change-in-prod"

# ── Producción ────────────────────────────────────────────────────────────────
build:
	@echo "🏗️  Building producción..."
	docker compose -f infrastructure/docker/docker-compose.yml build

docker-up:
	@echo "🐳 Levantando MediFlow completo..."
	docker compose -f infrastructure/docker/docker-compose.yml up --build -d

docker-down:
	@echo "🛑 Deteniendo MediFlow..."
	docker compose -f infrastructure/docker/docker-compose.yml down

clean:
	@echo "🧹 Limpiando contenedores y volúmenes..."
	docker compose -f infrastructure/docker/docker-compose.dev.yml down -v
	docker compose -f infrastructure/docker/docker-compose.yml down -v
