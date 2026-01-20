# Script para ejecutar el frontend
Write-Host "Instalando dependencias del frontend..." -ForegroundColor Yellow
cd frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Ejecutando npm install..." -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error al instalar dependencias" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Dependencias ya instaladas" -ForegroundColor Green
}

Write-Host ""
Write-Host "Iniciando servidor de desarrollo..." -ForegroundColor Green
Write-Host "El frontend estara disponible en: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

npm run dev
