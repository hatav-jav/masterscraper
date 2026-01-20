# Script para inicializar Git en el proyecto
Write-Host "Inicializando Git repository..." -ForegroundColor Green

# Inicializar Git
git init
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al inicializar Git" -ForegroundColor Red
    exit 1
}

# Cambiar branch a main
git branch -M main

# Agregar todos los archivos
Write-Host "Agregando archivos..." -ForegroundColor Green
git add .

# Hacer commit inicial
Write-Host "Creando commit inicial..." -ForegroundColor Green
git commit -m "chore: configuración inicial del proyecto"

Write-Host "`n✅ Git inicializado correctamente!" -ForegroundColor Green
Write-Host "`nPróximos pasos:" -ForegroundColor Yellow
Write-Host "1. Crear repositorio en GitHub" -ForegroundColor White
Write-Host "2. Ejecutar: git remote add origin https://github.com/[tu-usuario]/[nombre-repo].git" -ForegroundColor White
Write-Host "3. Ejecutar: git push -u origin main" -ForegroundColor White

