# Script para hacer commit de versión 1.0.0-test
Write-Host "=== Commit Versión 1.0.0-test ===" -ForegroundColor Cyan

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend\main.py")) {
    Write-Host "Error: No estas en el directorio correcto del proyecto" -ForegroundColor Red
    Write-Host "Por favor, navega al directorio Master Scraper primero" -ForegroundColor Yellow
    exit 1
}

Write-Host "Agregando archivos del proyecto..." -ForegroundColor Yellow
git add backend/ frontend/ scrapers/ *.py *.md *.txt *.ps1 *.sh data/ .gitignore .gitattributes

Write-Host ""
Write-Host "Estado de los archivos:" -ForegroundColor Cyan
git status --short | Select-Object -First 20

Write-Host ""
Write-Host "Creando commit..." -ForegroundColor Yellow
git commit -m "fix(backend): permitir acceso publico a endpoint raiz y corregir autenticacion

- Agregar endpoint raiz / a rutas publicas
- Corregir middleware de autenticacion
- Hacer playwright opcional en requirements.txt
- Agregar scripts de ejecucion
- Preparar version 1.0.0-test"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Creando tag v1.0.0-test..." -ForegroundColor Yellow
    git tag -a v1.0.0-test -m "Version 1.0.0 de prueba - Backend funcional, Frontend pendiente"
    
    Write-Host ""
    Write-Host "Haciendo push..." -ForegroundColor Yellow
    git push origin main
    git push origin v1.0.0-test
    
    Write-Host ""
    Write-Host "Commit y tag creados exitosamente!" -ForegroundColor Green
} else {
    Write-Host "Error al crear commit" -ForegroundColor Red
}

