from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from backend.config import API_SECRET

security = HTTPBasic()

def verify_api_key(request: Request):
    """Verifica el header X-API-Key."""
    if not API_SECRET:
        return True  # Si no hay secret configurado, permitir acceso
    
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return True

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware simple para autenticación por header."""
    
    async def dispatch(self, request: Request, call_next):
        # Permitir acceso a rutas públicas (sin autenticación)
        public_paths = ["/", "/docs", "/openapi.json", "/redoc"]
        if any(request.url.path.startswith(path) for path in public_paths):
            response = await call_next(request)
            return response
        
        # Verificar API Key para rutas protegidas
        if API_SECRET:
            try:
                verify_api_key(request)
            except HTTPException:
                raise
        
        response = await call_next(request)
        return response

