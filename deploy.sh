#!/bin/bash
# Script de deployment para Master Scraper
# Ejecutar desde el directorio del proyecto en el VPS

set -e

echo "🚀 Iniciando deployment de Master Scraper..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: No se encontró docker-compose.yml${NC}"
    echo "Asegúrate de estar en el directorio del proyecto"
    exit 1
fi

# Verificar archivo de entorno
if [ ! -f ".env.production" ]; then
    echo -e "${RED}Error: No se encontró .env.production${NC}"
    echo "Copia .env.production.template a .env.production y completa los valores"
    exit 1
fi

echo -e "${YELLOW}📥 Obteniendo últimos cambios de GitHub...${NC}"
git pull origin main

echo -e "${YELLOW}🔨 Construyendo imágenes Docker...${NC}"
docker compose build --no-cache

echo -e "${YELLOW}🔄 Reiniciando servicios...${NC}"
docker compose down
docker compose up -d

echo -e "${YELLOW}⏳ Esperando que los servicios inicien...${NC}"
sleep 10

# Verificar que los servicios están corriendo
echo -e "${YELLOW}🔍 Verificando servicios...${NC}"
if docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Servicios corriendo correctamente${NC}"
    docker compose ps
else
    echo -e "${RED}❌ Error: Algunos servicios no iniciaron${NC}"
    docker compose logs --tail=50
    exit 1
fi

# Health check del backend
echo -e "${YELLOW}🏥 Verificando health del backend...${NC}"
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Backend healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Backend aún iniciando o no responde${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Deployment completado!${NC}"
echo ""
echo "Accede a tu aplicación en: https://controlgastosjero.xyz"
