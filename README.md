# Master Scraper Hub

Dashboard web simple para ejecutar múltiples scrapers en Python. Los resultados se guardan en SQLite, y se puede generar un reporte con IA y enviarlo por email.

## Arquitectura

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js con Tailwind CSS
- **Base de datos**: SQLite
- **Scrapers**: Funciones Python importables

## Estructura del Proyecto

```
Master Scraper/
├── scrapers/          # Scrapers individuales
├── backend/           # API FastAPI
├── frontend/          # Aplicación Next.js
└── data/              # Base de datos SQLite
```

## Setup

### Configuración de Variables de Entorno

**Opción 1: Script automático (recomendado)**
```powershell
.\setup-env.ps1
```

**Opción 2: Manual**
- Crear archivo `.env` en la raíz con las variables del backend
- Crear archivo `frontend/.env.local` con las variables del frontend
- Ver `SETUP.md` para detalles completos

### Verificación del Setup

Ejecuta el script de verificación:
```bash
python test-setup.py
```

Este script verifica:
- ✅ Archivos del proyecto
- ✅ Variables de entorno configuradas
- ✅ Dependencias instaladas
- ✅ Coincidencia de API keys

### Backend

1. Crear entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # o
   source venv/bin/activate  # Linux/Mac
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno:
   - Crear archivo `.env` en la raíz del proyecto con:
     ```env
     API_SECRET=tu_secreto_aqui
     OPENAI_API_KEY=sk-...
     EMAIL_FROM=tu_email@gmail.com
     EMAIL_TO=destino@gmail.com
     EMAIL_PASSWORD=tu_password_o_app_password
     DB_PATH=data/master_scraper.db
     ```

4. Ejecutar backend:
   ```bash
   uvicorn backend.main:app --reload
   ```

### Frontend

1. Navegar a la carpeta frontend:
   ```bash
   cd frontend
   ```

2. Instalar dependencias:
   ```bash
   npm install
   ```

3. Crear archivo `.env.local` en `frontend/`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_API_KEY=tu_secreto_aqui
   ```

4. Ejecutar frontend:
   ```bash
   npm run dev
   ```

5. Abrir en navegador: http://localhost:3000

## Variables de Entorno

**Backend** - Archivo `.env` en la raíz (ya creado como template):
```env
API_SECRET=tu_secreto_aqui
OPENAI_API_KEY=sk-...
EMAIL_FROM=tu_email@gmail.com
EMAIL_TO=destino@gmail.com
EMAIL_PASSWORD=tu_app_password
DB_PATH=data/master_scraper.db
```

**Frontend** - Archivo `frontend/.env.local` (ya creado como template):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_KEY=tu_secreto_aqui
```

**⚠️ IMPORTANTE**: 
- Edita los archivos `.env` y `frontend/.env.local` con tus valores reales
- Estos archivos NO se suben a GitHub (están en .gitignore)
- El `NEXT_PUBLIC_API_KEY` debe ser igual que `API_SECRET` en `.env`

## Versionado y Git

El proyecto está conectado a GitHub: https://github.com/hatav-jav/masterscraper

**Ver `GIT_WORKFLOW.md` para guía completa de versionado.**

**Resumen rápido:**
- Hacer commits frecuentes en `main` para cambios pequeños
- Crear branches (`feature/nombre`) para cambios grandes
- Hacer push regularmente después de commits importantes
- Usar mensajes descriptivos: `feat(scope): descripción`

## Endpoints de la API

- `POST /scrape/{source}` - Ejecuta un scraper específico (ej: `/scrape/seia`, `/scrape/hechos_esenciales`)
- `POST /report` - Genera reporte con IA y lo envía por email
- `GET /leads` - Obtiene leads recientes (opcional: `?limit=100`)

Todos los endpoints requieren el header `X-API-Key` con el valor configurado en `API_SECRET` (excepto en modo desarrollo sin API_SECRET).

## Estructura de Scrapers

Para agregar un nuevo scraper:

1. Crear archivo `scrapers/{nombre}/scraper.py` con función `run_{nombre}()` que retorne lista de dicts
2. Importar en `backend/main.py`: `from scrapers.{nombre}.scraper import run_{nombre}`
3. Agregar al dict `SCRAPERS` en `backend/main.py`

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'backend'"
- Asegúrate de ejecutar desde la raíz del proyecto
- Verifica que estés usando el entorno virtual correcto

### Error: "CORS" en el frontend
- Verifica que `NEXT_PUBLIC_API_URL` en `.env.local` apunte a `http://localhost:8000`
- Asegúrate de que el backend esté corriendo

### Error: "401 Unauthorized"
- Verifica que `API_SECRET` en `.env` coincida con `NEXT_PUBLIC_API_KEY` en `frontend/.env.local`

### El scraper SEIA tarda mucho
- Es normal, el scraper espera 15 segundos antes de la primera request
- Puedes ajustar `max_paginas` en `scrapers/seia/scraper.py` si quieres menos datos de prueba

