# PowerShell script para desenvolvimento

Write-Host "🚀 Iniciando ambiente de desenvolvimento SGP+" -ForegroundColor Green

# Subir PostgreSQL
Write-Host "📦 Subindo PostgreSQL..." -ForegroundColor Yellow
Set-Location infra/docker
docker-compose up -d
Set-Location ../..

# Aguardar PostgreSQL estar pronto
Write-Host "⏳ Aguardando PostgreSQL..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Rodar migrations
Write-Host "🔄 Rodando migrations..." -ForegroundColor Yellow
Set-Location apps/api
alembic upgrade head
Set-Location ../..

Write-Host "✅ Ambiente pronto!" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar os serviços:" -ForegroundColor Cyan
Write-Host "  Terminal 1 (API): cd apps/api && uvicorn sgp_plus.main:app --reload --port 8000"
Write-Host "  Terminal 2 (Web): cd apps/web && npm run dev"
