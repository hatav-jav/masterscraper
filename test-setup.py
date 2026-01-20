#!/usr/bin/env python3
"""
Script para verificar que el setup está completo y funcionando.
"""
import os
import sys
import subprocess

def check_file(filepath, description):
    """Verifica que un archivo exista."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NO encontrado: {filepath}")
        return False

def check_env_file(filepath, required_vars):
    """Verifica que el archivo .env tenga las variables necesarias."""
    if not os.path.exists(filepath):
        print(f"❌ {filepath} no existe")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_set = True
    for var in required_vars:
        if f"{var}=" in content:
            # Verificar que no sea placeholder
            lines = content.split('\n')
            for line in lines:
                if line.startswith(f"{var}="):
                    value = line.split('=', 1)[1].strip()
                    if 'tu_' in value.lower() or 'sk-tu' in value.lower() or value == '':
                        print(f"⚠️  {var} en {filepath} necesita ser configurado")
                        all_set = False
                    else:
                        print(f"✅ {var} configurado en {filepath}")
                    break
        else:
            print(f"❌ {var} no encontrado en {filepath}")
            all_set = False
    
    return all_set

def check_python_deps():
    """Verifica que las dependencias de Python estén instaladas."""
    try:
        import fastapi
        import uvicorn
        import openai
        print("✅ Dependencias Python principales instaladas")
        return True
    except ImportError as e:
        print(f"❌ Faltan dependencias Python: {e}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False

def check_node_modules():
    """Verifica que node_modules exista en frontend."""
    if os.path.exists("frontend/node_modules"):
        print("✅ node_modules existe en frontend")
        return True
    else:
        print("⚠️  node_modules no encontrado en frontend")
        print("   Ejecuta: cd frontend && npm install")
        return False

def main():
    print("🔍 Verificando setup del proyecto...\n")
    
    all_ok = True
    
    # Verificar archivos principales
    print("=== Archivos del Proyecto ===")
    all_ok &= check_file("backend/main.py", "Backend main.py")
    all_ok &= check_file("frontend/package.json", "Frontend package.json")
    all_ok &= check_file("requirements.txt", "requirements.txt")
    
    # Verificar archivos de entorno
    print("\n=== Variables de Entorno ===")
    backend_env_ok = check_env_file(
        ".env",
        ["API_SECRET", "OPENAI_API_KEY", "EMAIL_FROM", "EMAIL_TO", "DB_PATH"]
    )
    
    frontend_env_ok = check_env_file(
        "frontend/.env.local",
        ["NEXT_PUBLIC_API_URL", "NEXT_PUBLIC_API_KEY"]
    )
    
    all_ok &= backend_env_ok
    all_ok &= frontend_env_ok
    
    # Verificar dependencias
    print("\n=== Dependencias ===")
    all_ok &= check_python_deps()
    node_ok = check_node_modules()  # No crítico para este script
    
    # Verificar que API_SECRET coincida
    if backend_env_ok and frontend_env_ok:
        print("\n=== Verificando Coincidencia de API Keys ===")
        try:
            with open(".env", 'r') as f:
                backend_content = f.read()
            with open("frontend/.env.local", 'r') as f:
                frontend_content = f.read()
            
            backend_secret = None
            frontend_key = None
            
            for line in backend_content.split('\n'):
                if line.startswith("API_SECRET="):
                    backend_secret = line.split('=', 1)[1].strip()
            
            for line in frontend_content.split('\n'):
                if line.startswith("NEXT_PUBLIC_API_KEY="):
                    frontend_key = line.split('=', 1)[1].strip()
            
            if backend_secret and frontend_key:
                if backend_secret == frontend_key:
                    print("✅ API_SECRET y NEXT_PUBLIC_API_KEY coinciden")
                else:
                    print("⚠️  API_SECRET y NEXT_PUBLIC_API_KEY NO coinciden")
                    print(f"   Backend: {backend_secret[:10]}...")
                    print(f"   Frontend: {frontend_key[:10]}...")
        except Exception as e:
            print(f"⚠️  Error verificando keys: {e}")
    
    print("\n" + "="*50)
    if all_ok:
        print("✅ Setup completo y listo para ejecutar!")
        print("\nPara ejecutar:")
        print("  Backend:  uvicorn backend.main:app --reload")
        print("  Frontend: cd frontend && npm run dev")
    else:
        print("⚠️  Hay problemas con el setup")
        print("Revisa los mensajes arriba y corrige los problemas")
        sys.exit(1)

if __name__ == "__main__":
    main()

