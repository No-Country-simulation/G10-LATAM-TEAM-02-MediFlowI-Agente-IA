#!/usr/bin/env bash
# ==============================================================================
# Script para autogenerar interfaces y tipos TypeScript desde specs/openapi.yaml
# Requiere Node.js / npx
# ==============================================================================

set -e

echo "🔄 Generando tipos de TypeScript a partir de specs/openapi.yaml..."
mkdir -p src/types

npx --yes openapi-typescript ../specs/openapi.yaml -o ./src/types/api.ts

echo "✅ Tipos de TypeScript generados exitosamente en src/types/api.ts"
