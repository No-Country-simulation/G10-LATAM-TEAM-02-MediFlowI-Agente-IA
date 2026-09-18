.PHONY: help test dev-backend dev-frontend docker-up docker-down sample-test

help:
	@echo "Comandos disponibles en MediFlow:"
	@echo "  make test          - Ejecutar pruebas de contrato unitarias con Pytest"
	@echo "  make dev-backend   - Levantar FastAPI backend en http://localhost:8000"
	@echo "  make docker-up     - Levantar stack completo con Docker Compose"
	@echo "  make docker-down   - Detener contenedores Docker"
	@echo "  make sample-urgencia - Probar caso 1 (TEP) con curl"

test:
	python3 -m pytest backend-api/tests/ -v

dev-backend:
	cd backend-api && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

docker-up:
	docker compose up -d

docker-down:
	docker compose down

sample-urgencia:
	curl -s -X POST http://localhost:8000/api/v1/triaje \
	  -H "Content-Type: application/json" \
	  -d '{"documento_id":"DOC-CLIN-2026-8942","tipo_archivo":"TEXTO","documento_texto":"$$(cat data/samples/caso_01_urgencia_tep.txt)","canal_origen":"Guardia_Emergencias"}' | jq .
