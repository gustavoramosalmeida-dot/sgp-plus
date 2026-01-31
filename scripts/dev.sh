#!/bin/bash

set -e

echo "🚀 Iniciando ambiente de desenvolvimento SGP+"

# Subir PostgreSQL
echo "📦 Subindo PostgreSQL..."
cd infra/docker
docker-compose up -d
cd ../..

# Aguardar PostgreSQL estar pronto
echo "⏳ Aguardando PostgreSQL..."
sleep 5

# Rodar migrations
echo "🔄 Rodando migrations..."
cd apps/api
alembic upgrade head
cd ../..

echo "✅ Ambiente pronto!"
echo ""
echo "Para iniciar os serviços:"
echo "  Terminal 1 (API): cd apps/api && uvicorn sgp_plus.main:app --reload --port 8000"
echo "  Terminal 2 (Web): cd apps/web && npm run dev"
