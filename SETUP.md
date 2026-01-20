# Instrucciones de Setup

## Configuración Inicial

### 1. Backend (Python)

1. Crear entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Crear archivo `.env` en la raíz del proyecto:
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

### 2. Frontend (Next.js)

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

## Conectar con GitHub

1. Si aún no has inicializado Git en este directorio:
   ```bash
   git init
   git branch -M main
   ```

2. Crear repositorio en GitHub (público o privado)

3. Conectar repositorio local con remoto:
   ```bash
   git remote add origin https://github.com/[tu-usuario]/[nombre-repo].git
   ```

4. Agregar archivos y hacer commit:
   ```bash
   git add .
   git commit -m "chore: configuración inicial del proyecto"
   ```

5. Push al repositorio:
   ```bash
   git push -u origin main
   ```

## Notas Importantes

- No commitees el archivo `.env` (está en .gitignore)
- La base de datos SQLite se creará automáticamente en `data/` al ejecutar el backend
- Para producción, configurar las variables de entorno según tu entorno de despliegue

