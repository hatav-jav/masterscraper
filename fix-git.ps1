# Script para solucionar problemas de Git y hacer el commit inicial
Write-Host "=== Solucionando problemas de Git ===" -ForegroundColor Cyan

# 1. Verificar que estamos en el directorio correcto
if (-not (Test-Path "backend\main.py")) {
    Write-Host "❌ Error: No estás en el directorio correcto del proyecto" -ForegroundColor Red
    Write-Host "Por favor, navega al directorio Master Scraper primero" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Directorio correcto verificado" -ForegroundColor Green

# 2. Configurar Git si no está configurado
$email = git config user.email
$name = git config user.name

if (-not $email -or -not $name) {
    Write-Host "Configurando Git..." -ForegroundColor Yellow
    git config user.email "jamenabar92@gmail.com"
    git config user.name "Jeronimo Amenabar"
}

Write-Host "✅ Git configurado: $email / $name" -ForegroundColor Green

# 3. Verificar o actualizar remote origin
$remote = git remote get-url origin 2>$null
if ($remote) {
    Write-Host "Remote origin existe: $remote" -ForegroundColor Yellow
    Write-Host "¿Quieres actualizarlo? (S/N)" -ForegroundColor Yellow
    $update = Read-Host
    if ($update -eq "S" -or $update -eq "s") {
        git remote set-url origin https://github.com/hatav-jav/masterscraper.git
        Write-Host "✅ Remote actualizado" -ForegroundColor Green
    }
} else {
    Write-Host "Agregando remote origin..." -ForegroundColor Yellow
    git remote add origin https://github.com/hatav-jav/masterscraper.git
    Write-Host "✅ Remote agregado" -ForegroundColor Green
}

# 4. Agregar archivos
Write-Host "`nAgregando archivos al staging area..." -ForegroundColor Yellow
git add .

# 5. Verificar qué archivos se agregaron
Write-Host "`nArchivos agregados:" -ForegroundColor Cyan
git status --short | Select-Object -First 10

# 6. Hacer commit
Write-Host "`nCreando commit inicial..." -ForegroundColor Yellow
git commit -m "chore: configuración inicial del proyecto"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Commit creado exitosamente!" -ForegroundColor Green
    
    # 7. Cambiar a branch main
    Write-Host "`nCambiando a branch main..." -ForegroundColor Yellow
    git branch -M main
    
    # 8. Push
    Write-Host "`nHaciendo push a GitHub..." -ForegroundColor Yellow
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🎉 ¡Todo listo! El código está en GitHub." -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  Error al hacer push. Verifica tus credenciales de GitHub." -ForegroundColor Yellow
    }
} else {
    Write-Host "`n❌ Error al crear commit. Revisa los mensajes arriba." -ForegroundColor Red
}
