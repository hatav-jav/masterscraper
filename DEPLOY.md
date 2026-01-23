# Guía de Deployment - Master Scraper

Esta guía te llevará paso a paso para desplegar Master Scraper en tu VPS Vultr.

## Requisitos Previos

- VPS con Ubuntu 24.04 LTS
- Docker instalado
- Dominio configurado (DNS apuntando al VPS)

## Datos del Servidor

- **IP**: `155.138.200.98`
- **Dominio**: `controlgastosjero.xyz`

---

## Paso 1: Conectar al VPS

```bash
ssh root@155.138.200.98
```

## Paso 2: Instalar Docker Compose (si no está)

```bash
apt update
apt install -y docker-compose-plugin
```

Verificar instalación:
```bash
docker compose version
```

## Paso 3: Clonar el Repositorio

```bash
git clone https://github.com/hatav-jav/masterscraper.git /opt/masterscraper
cd /opt/masterscraper
```

## Paso 4: Configurar Variables de Entorno

```bash
cp env.production.template .env.production
nano .env.production
```

Completa los siguientes valores:

```env
API_SECRET=<genera con: openssl rand -hex 32>
OPENAI_API_KEY=<tu clave de OpenAI>
EMAIL_FROM=<tu email>
EMAIL_TO=<email destino reportes>
EMAIL_PASSWORD=<app password de Gmail>
ADMIN_USER=admin
ADMIN_PASSWORD=<tu contraseña segura>
JWT_SECRET=<genera con: openssl rand -hex 64>
```

Para generar claves seguras:
```bash
# API_SECRET
openssl rand -hex 32

# JWT_SECRET
openssl rand -hex 64
```

## Paso 5: Configurar Firewall

```bash
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

## Paso 6: Crear Directorios Necesarios

```bash
mkdir -p /opt/masterscraper/certbot/conf
mkdir -p /opt/masterscraper/certbot/www
mkdir -p /opt/masterscraper/data
```

## Paso 7: Obtener Certificado SSL (Primera Vez)

### 7.1 Usar configuración inicial (sin SSL)

```bash
cd /opt/masterscraper
cp nginx/nginx-initial.conf nginx/nginx.conf
```

### 7.2 Iniciar servicios sin SSL

```bash
docker compose up -d backend frontend nginx
```

### 7.3 Obtener certificado con Certbot

```bash
docker run -it --rm \
  -v /opt/masterscraper/certbot/conf:/etc/letsencrypt \
  -v /opt/masterscraper/certbot/www:/var/www/certbot \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d controlgastosjero.xyz \
  -d www.controlgastosjero.xyz \
  --email tu_email@gmail.com \
  --agree-tos \
  --no-eff-email
```

### 7.4 Restaurar configuración con SSL

```bash
# Copiar la configuración completa con SSL
git checkout nginx/nginx.conf

# Reiniciar nginx
docker compose restart nginx
```

## Paso 8: Iniciar Todos los Servicios

```bash
docker compose up -d
```

Verificar que todo está corriendo:
```bash
docker compose ps
```

## Paso 9: Verificar Deployment

1. Abre tu navegador y ve a: `https://controlgastosjero.xyz`
2. Deberías ver la página de login
3. Ingresa con:
   - Usuario: `admin`
   - Contraseña: (la que configuraste en `.env.production`)

---

## Comandos Útiles

### Ver logs de todos los servicios
```bash
docker compose logs -f
```

### Ver logs de un servicio específico
```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx
```

### Reiniciar servicios
```bash
docker compose restart
```

### Parar servicios
```bash
docker compose down
```

### Actualizar a nueva versión
```bash
cd /opt/masterscraper
./deploy.sh
```

---

## Troubleshooting

### Error: "Connection refused" o página no carga
1. Verificar que los servicios estén corriendo: `docker compose ps`
2. Ver logs: `docker compose logs`
3. Verificar firewall: `ufw status`

### Error: Certificado SSL no válido
1. Verificar que el DNS esté propagado: `nslookup controlgastosjero.xyz`
2. Re-ejecutar certbot

### Error: "401 Unauthorized"
1. Verificar que `ADMIN_PASSWORD` esté configurado en `.env.production`
2. Reiniciar el backend: `docker compose restart backend`

### La base de datos está vacía después de redeploy
Los datos se guardan en `/opt/masterscraper/data/`. Asegúrate de no borrar esta carpeta.

---

## Renovación Automática de SSL

El contenedor `certbot` incluido renueva automáticamente los certificados. Para verificar:

```bash
docker compose logs certbot
```

---

## Seguridad Adicional (Recomendado)

### Cambiar puerto SSH
```bash
nano /etc/ssh/sshd_config
# Cambiar: Port 22 -> Port 2222
systemctl restart sshd
ufw allow 2222
```

### Deshabilitar login root con password
```bash
nano /etc/ssh/sshd_config
# PermitRootLogin prohibit-password
```

---

## Contacto

Si tienes problemas, revisa los logs primero:
```bash
docker compose logs --tail=100
```
