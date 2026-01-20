# Script para configurar variables de entorno
Write-Host "=== Configuración de Variables de Entorno ===" -ForegroundColor Cyan

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend\main.py")) {
    Write-Host "❌ Error: No estás en el directorio correcto del proyecto" -ForegroundColor Red
    Write-Host "Por favor, navega al directorio Master Scraper primero" -ForegroundColor Yellow
    exit 1
}

# 1. Backend .env
Write-Host "`n1. Configurando .env del backend..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "   ⚠️  El archivo .env ya existe. ¿Sobrescribir? (S/N)" -ForegroundColor Yellow
    $overwrite = Read-Host
    if ($overwrite -ne "S" -and $overwrite -ne "s") {
        Write-Host "   Saltando creación de .env" -ForegroundColor Gray
    } else {
        Copy-Item env.template .env -Force
        Write-Host "   ✅ Archivo .env creado desde template" -ForegroundColor Green
        Write-Host "   📝 Por favor, edita .env y completa con tus credenciales" -ForegroundColor Cyan
    }
} else {
    Copy-Item env.template .env
    Write-Host "   ✅ Archivo .env creado desde template" -ForegroundColor Green
    Write-Host "   📝 Por favor, edita .env y completa con tus credenciales" -ForegroundColor Cyan
}

# 2. Frontend .env.local
Write-Host "`n2. Configurando .env.local del frontend..." -ForegroundColor Yellow

if (Test-Path "frontend\.env.local") {
    Write-Host "   ⚠️  El archivo frontend/.env.local ya existe. ¿Sobrescribir? (S/N)" -ForegroundColor Yellow
    $overwrite = Read-Host
    if ($overwrite -ne "S" -and $overwrite -ne "s") {
        Write-Host "   Saltando creación de frontend/.env.local" -ForegroundColor Gray
    } else {
        Copy-Item frontend\env.local.template frontend\.env.local -Force
        Write-Host "   ✅ Archivo frontend/.env.local creado desde template" -ForegroundColor Green
        Write-Host "   📝 Por favor, edita frontend/.env.local y completa con tus credenciales" -ForegroundColor Cyan
    }
} else {
    Copy-Item frontend\env.local.template frontend\.env.local
    Write-Host "   ✅ Archivo frontend/.env.local creado desde template" -ForegroundColor Green
    Write-Host "   📝 Por favor, edita frontend/.env.local y completa con tus credenciales" -ForegroundColor Cyan
}

Write-Host "`n✅ Archivos de configuración creados!" -ForegroundColor Green
Write-Host "`n📋 Próximos pasos:" -ForegroundColor Yellow
Write-Host "1. Edita .env y completa con tus credenciales reales" -ForegroundColor White
Write-Host "2. Edita frontend/.env.local y completa con tus credenciales" -ForegroundColor White
Write-Host "3. Asegúrate de que NEXT_PUBLIC_API_KEY sea igual a API_SECRET" -ForegroundColor White
Write-Host "`n📖 Para más detalles, consulta CONFIGURACION.md" -ForegroundColor Cyan
