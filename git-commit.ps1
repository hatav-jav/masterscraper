# Script para hacer commit después de configurar Git
Write-Host "Verificando configuración de Git..." -ForegroundColor Green

# Verificar que Git está configurado
$email = git config user.email
$name = git config user.name

if (-not $email -or -not $name) {
    Write-Host "Configurando Git..." -ForegroundColor Yellow
    git config user.email "jamenabar92@gmail.com"
    git config user.name "Jeronimo Amenabar"
    Write-Host "✅ Git configurado" -ForegroundColor Green
} else {
    Write-Host "✅ Git ya está configurado:" -ForegroundColor Green
    Write-Host "   Email: $email" -ForegroundColor Cyan
    Write-Host "   Name: $name" -ForegroundColor Cyan
}

Write-Host "`nVerificando archivos del proyecto..." -ForegroundColor Green
if (Test-Path "backend/main.py") {
    Write-Host "✅ Estás en el directorio correcto del proyecto" -ForegroundColor Green
    
    Write-Host "`nAgregando archivos..." -ForegroundColor Yellow
    git add .
    
    Write-Host "Creando commit..." -ForegroundColor Yellow
    git commit -m "chore: configuración inicial del proyecto"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Commit creado exitosamente!" -ForegroundColor Green
        Write-Host "`nPróximos pasos:" -ForegroundColor Yellow
        Write-Host "1. Crear repositorio en GitHub" -ForegroundColor White
        Write-Host "2. Ejecutar: git remote add origin https://github.com/[tu-usuario]/[nombre-repo].git" -ForegroundColor White
        Write-Host "3. Ejecutar: git push -u origin main" -ForegroundColor White
    }
} else {
    Write-Host "❌ No estás en el directorio correcto del proyecto" -ForegroundColor Red
    Write-Host "Por favor, navega al directorio Master Scraper y ejecuta este script nuevamente" -ForegroundColor Yellow
}
