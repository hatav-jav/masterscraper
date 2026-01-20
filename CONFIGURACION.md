# Guía de Configuración - Variables de Entorno

## Paso 1: Configurar Backend (.env)

1. En la raíz del proyecto, crea un archivo llamado `.env`:
   ```bash
   # Windows PowerShell
   Copy-Item env.template .env
   
   # Linux/Mac
   cp env.template .env
   ```

2. Edita el archivo `.env` y completa con tus valores reales:

   ```env
   # API Secret para autenticación
   # Genera uno seguro, por ejemplo: openssl rand -hex 32
   # O simplemente usa una frase larga y segura
   API_SECRET=mi_secreto_super_seguro_123456

   # OpenAI API Key
   # Obtén tu key en: https://platform.openai.com/api-keys
   OPENAI_API_KEY=sk-proj-...

   # Configuración de email
   # Para Gmail, necesitas crear un "App Password"
   # Ve a: https://myaccount.google.com/apppasswords
   EMAIL_FROM=tu_email@gmail.com
   EMAIL_TO=destino@gmail.com
   EMAIL_PASSWORD=tu_app_password_de_16_digitos

   # Base de datos (normalmente no necesitas cambiar esto)
   DB_PATH=data/master_scraper.db
   ```

### ⚠️ Importante: App Password de Gmail

Si usas Gmail, NO uses tu contraseña normal. Debes crear un "App Password":

1. Ve a: https://myaccount.google.com/apppasswords
2. Selecciona "Mail" y tu dispositivo
3. Genera el password
4. Usa ese password de 16 dígitos en `EMAIL_PASSWORD`

## Paso 2: Configurar Frontend (.env.local)

1. En la carpeta `frontend/`, crea un archivo llamado `.env.local`:
   ```bash
   cd frontend
   # Windows PowerShell
   Copy-Item env.local.template .env.local
   
   # Linux/Mac
   cp env.local.template .env.local
   ```

2. Edita `frontend/.env.local`:
   ```env
   # URL del backend (normalmente no cambia)
   NEXT_PUBLIC_API_URL=http://localhost:8000

   # API Key (DEBE ser el mismo valor que API_SECRET en .env del backend)
   NEXT_PUBLIC_API_KEY=mi_secreto_super_seguro_123456
   ```

   ⚠️ **IMPORTANTE**: El valor de `NEXT_PUBLIC_API_KEY` debe ser **exactamente igual** a `API_SECRET` del backend.

## Paso 3: Verificar Configuración

Ejecuta el script de verificación:
```bash
python check-setup.py
```

## Seguridad

- ✅ Los archivos `.env` y `.env.local` están en `.gitignore` y NO se subirán a GitHub
- ✅ Nunca compartas tus credenciales
- ✅ Si accidentalmente commiteaste credenciales, cámbialas inmediatamente
- ✅ Usa valores diferentes para desarrollo y producción

## Prueba Rápida

Después de configurar, prueba que todo funciona:

1. **Backend:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn backend.main:app --reload
   ```
   
   Deberías ver: `Uvicorn running on http://127.0.0.1:8000`

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   
   Deberías ver: `ready - started server on 0.0.0.0:3000`

3. **Abrir en navegador:**
   - Ve a http://localhost:3000
   - Deberías ver el dashboard

## Troubleshooting

### Error: "API_SECRET no configurado"
- Verifica que el archivo `.env` existe en la raíz del proyecto
- Verifica que `API_SECRET=` tiene un valor después del signo igual

### Error: "401 Unauthorized" en frontend
- Verifica que `NEXT_PUBLIC_API_KEY` en `frontend/.env.local` sea igual a `API_SECRET` en `.env`
- Reinicia el servidor frontend después de cambiar `.env.local`

### Error al enviar email
- Verifica que `EMAIL_PASSWORD` es un App Password de Gmail, no tu contraseña normal
- Verifica que la verificación en dos pasos está activada en tu cuenta de Google

