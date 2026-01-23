// Funciones de autenticación y manejo de sesión

const TOKEN_KEY = 'ms_auth_token';
const TOKEN_EXPIRY_KEY = 'ms_auth_expiry';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in_hours: number;
}

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  
  const token = localStorage.getItem(TOKEN_KEY);
  const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY);
  
  // Verificar si el token ha expirado
  if (token && expiry) {
    const expiryDate = new Date(expiry);
    if (expiryDate > new Date()) {
      return token;
    }
    // Token expirado, limpiar
    clearToken();
  }
  
  return null;
}

export function setToken(token: string, expiresInHours: number): void {
  if (typeof window === 'undefined') return;
  
  localStorage.setItem(TOKEN_KEY, token);
  
  // Calcular fecha de expiración
  const expiry = new Date();
  expiry.setHours(expiry.getHours() + expiresInHours);
  localStorage.setItem(TOKEN_EXPIRY_KEY, expiry.toISOString());
}

export function clearToken(): void {
  if (typeof window === 'undefined') return;
  
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error de conexión' }));
    throw new Error(error.detail || 'Error al iniciar sesión');
  }
  
  const data: LoginResponse = await response.json();
  setToken(data.access_token, data.expires_in_hours);
  
  return data;
}

export function logout(): void {
  clearToken();
  // Redirigir al login
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}
