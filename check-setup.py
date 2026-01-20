#!/usr/bin/env python3
"""
Script de verificación rápida para verificar que el setup está correcto.
"""
import os
import sys

def check_file(filepath, description):
    """Verifica que un archivo exista."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NO encontrado: {filepath}")
        return False

def check_directory(dirpath, description):
    """Verifica que un directorio exista."""
    if os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description} NO encontrado: {dirpath}")
        return False

def main():
    print("🔍 Verificando estructura del proyecto...\n")
    
    all_ok = True
    
    # Verificar estructura de carpetas
    all_ok &= check_directory("backend", "Carpeta backend")
    all_ok &= check_directory("frontend", "Carpeta frontend")
    all_ok &= check_directory("scrapers", "Carpeta scrapers")
    all_ok &= check_directory("data", "Carpeta data")
    
    # Verificar archivos principales backend
    all_ok &= check_file("backend/main.py", "Archivo main.py del backend")
    all_ok &= check_file("backend/database.py", "Archivo database.py")
    all_ok &= check_file("backend/config.py", "Archivo config.py")
    all_ok &= check_file("backend/auth.py", "Archivo auth.py")
    all_ok &= check_file("backend/report.py", "Archivo report.py")
    
    # Verificar scrapers
    all_ok &= check_file("scrapers/seia/scraper.py", "Scraper SEIA")
    all_ok &= check_file("scrapers/hechos_esenciales/scraper.py", "Scraper Hechos Esenciales")
    
    # Verificar frontend
    all_ok &= check_file("frontend/package.json", "package.json del frontend")
    all_ok &= check_file("frontend/app/page.tsx", "Página principal del frontend")
    
    # Verificar archivos de configuración
    all_ok &= check_file("requirements.txt", "requirements.txt")
    all_ok &= check_file(".gitignore", ".gitignore")
    all_ok &= check_file("README.md", "README.md")
    
    # Verificar .env (opcional)
    if os.path.exists(".env"):
        print("✅ Archivo .env encontrado")
    else:
        print("⚠️  Archivo .env NO encontrado (necesario para ejecutar)")
        print("   Crea un archivo .env basado en .env.example")
    
    print("\n" + "="*50)
    if all_ok:
        print("✅ Estructura del proyecto correcta!")
        print("\nPróximos pasos:")
        print("1. Crear archivo .env con tus credenciales")
        print("2. Instalar dependencias: pip install -r requirements.txt")
        print("3. Instalar dependencias frontend: cd frontend && npm install")
        print("4. Ejecutar backend: uvicorn backend.main:app --reload")
        print("5. Ejecutar frontend: cd frontend && npm run dev")
    else:
        print("❌ Hay problemas con la estructura del proyecto")
        sys.exit(1)

if __name__ == "__main__":
    main()

