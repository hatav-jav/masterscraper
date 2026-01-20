# Script para ejecutar el backend sin problemas de reload
Write-Host "Iniciando backend..." -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

# Ejecutar sin --reload para evitar loops, o con reload pero excluyendo venv
.\venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

