#!/bin/bash
# Script para inicializar Git en el proyecto

echo "Inicializando Git repository..."

# Inicializar Git
git init || { echo "Error al inicializar Git"; exit 1; }

# Cambiar branch a main
git branch -M main

# Agregar todos los archivos
echo "Agregando archivos..."
git add .

# Hacer commit inicial
echo "Creando commit inicial..."
git commit -m "chore: configuración inicial del proyecto"

echo ""
echo "✅ Git inicializado correctamente!"
echo ""
echo "Próximos pasos:"
echo "1. Crear repositorio en GitHub"
echo "2. Ejecutar: git remote add origin https://github.com/[tu-usuario]/[nombre-repo].git"
echo "3. Ejecutar: git push -u origin main"

