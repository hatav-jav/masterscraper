from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from backend.config import API_SECRET, ADMIN_USER, ADMIN_PASSWORD, JWT_SECRET, JWT_EXPIRATION_HOURS
from datetime import datetime, timedelta
from typing import Optional
import jwt

security = HTTPBearer(auto_error=False)

def create_access_token(username: str) -> str:
    """Crea un JWT token para el usuario."""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": username,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token: str) -> Optional[str]:
    """Verifica un JWT token y retorna el username si es válido."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def verify_credentials(username: str, password: str) -> bool:
    """Verifica las credenciales del usuario."""
    # En producción con ADMIN_PASSWORD configurado
    if ADMIN_PASSWORD:
        return username == ADMIN_USER and password == ADMIN_PASSWORD
    # En desarrollo sin password configurado, permitir acceso
    return username == ADMIN_USER

def verify_api_key(request: Request):
    """Verifica el header X-API-Key (legacy, para compatibilidad)."""
    if not API_SECRET:
        return True
    
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return True

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """Dependency para obtener el usuario actual del JWT token."""
    if credentials is None:
        return None
    
    token = credentials.credentials
    username = verify_token(token)
    return username

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware para autenticación por JWT o API Key."""
    
    async def dispatch(self, request: Request, call_next):
        # Permitir requests OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response
        
        # Rutas públicas (sin autenticación)
        public_paths = ["/", "/docs", "/openapi.json", "/redoc", "/login", "/health"]
        
        if any(request.url.path == path or request.url.path.startswith(path + "/") for path in public_paths):
            response = await call_next(request)
            return response
        
        # Verificar JWT token primero
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            username = verify_token(token)
            if username:
                # Token válido, continuar
                response = await call_next(request)
                return response
        
        # Fallback: verificar API Key (para compatibilidad con sistema anterior)
        api_key = request.headers.get("X-API-Key")
        if api_key and API_SECRET and api_key == API_SECRET:
            response = await call_next(request)
            return response
        
        # Si hay API_SECRET o ADMIN_PASSWORD configurado, requerir autenticación
        if API_SECRET or ADMIN_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autenticado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # En modo desarrollo sin auth configurado, permitir acceso
        response = await call_next(request)
        return response
