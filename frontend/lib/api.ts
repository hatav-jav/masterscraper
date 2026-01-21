const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (API_KEY) {
    headers['X-API-Key'] = API_KEY;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || 'Error en la peticion');
  }

  return response.json();
}

export async function scrapeSource(source: string) {
  return apiRequest(`/scrape/${source}`, {
    method: 'POST',
  });
}

export async function scrapeAll() {
  return apiRequest('/scrape-all', {
    method: 'POST',
  });
}

export async function generateReport() {
  return apiRequest('/report', {
    method: 'POST',
  });
}

export async function getLeads(limit: number = 500, sortBy?: string, sortOrder?: 'asc' | 'desc') {
  let endpoint = `/leads?limit=${limit}`;
  if (sortBy) {
    endpoint += `&sort_by=${sortBy}&sort_order=${sortOrder || 'desc'}`;
  }
  return apiRequest(endpoint);
}

export async function getRuns(limit: number = 10) {
  return apiRequest(`/runs?limit=${limit}`);
}

export async function getScrapeProgress(source: string) {
  return apiRequest(`/scrape-progress/${source}`);
}

export async function cancelScrape(source: string) {
  return apiRequest(`/scrape-cancel/${source}`, {
    method: 'POST',
  });
}
