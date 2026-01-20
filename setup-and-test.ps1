# Script para setup y prueba del proyecto
Write-Host "=== Setup y Prueba del Proyecto ===" -ForegroundColor Cyan

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend\main.py")) {
    Write-Host "Error: No estas en el directorio correcto del proyecto" -ForegroundColor Red
    Write-Host "Por favor, navega al directorio Master Scraper primero" -ForegroundColor Yellow
    exit 1
}

Write-Host "Directorio correcto verificado" -ForegroundColor Green

# 1. Crear carpeta data si no existe
Write-Host ""
Write-Host "1. Verificando carpeta data..." -ForegroundColor Yellow
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" -Force | Out-Null
    Write-Host "   Carpeta data creada" -ForegroundColor Green
} else {
    Write-Host "   Carpeta data ya existe" -ForegroundColor Green
}

# 2. Crear venv si no existe
Write-Host ""
Write-Host "2. Verificando entorno virtual..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "   Creando entorno virtual..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "   Entorno virtual creado" -ForegroundColor Green
} else {
    Write-Host "   Entorno virtual ya existe" -ForegroundColor Green
}

# 3. Instalar dependencias
Write-Host ""
Write-Host "3. Instalando dependencias Python..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -m pip install --upgrade pip
& .\venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "   Error al instalar dependencias" -ForegroundColor Red
    exit 1
}

# 4. Verificar archivos de configuración
Write-Host ""
Write-Host "4. Verificando configuracion..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "   Archivo .env encontrado" -ForegroundColor Green
} else {
    Write-Host "   Archivo .env NO encontrado" -ForegroundColor Yellow
    Write-Host "   Crea .env desde env.template" -ForegroundColor Yellow
}

if (Test-Path "frontend\.env.local") {
    Write-Host "   Archivo frontend/.env.local encontrado" -ForegroundColor Green
} else {
    Write-Host "   Archivo frontend/.env.local NO encontrado" -ForegroundColor Yellow
    Write-Host "   Crea frontend/.env.local desde frontend/env.local.template" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup completado!" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos pasos:" -ForegroundColor Yellow
Write-Host "1. Para ejecutar el backend:" -ForegroundColor White
Write-Host "   .\venv\Scripts\python.exe -m uvicorn backend.main:app --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Para ejecutar el frontend (en otra terminal):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Cyan
Write-Host "   npm install" -ForegroundColor Cyan
Write-Host "   npm run dev" -ForegroundColor Cyan
