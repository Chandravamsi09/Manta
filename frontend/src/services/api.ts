const API_BASE = 'http://localhost:8000';

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('manta_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const errText = await res.text();
    let errMsg = `HTTP Error ${res.status}`;
    try {
      const errJson = JSON.parse(errText);
      errMsg = errJson.detail || errMsg;
    } catch {}
    throw new Error(errMsg);
  }

  return res.json();
}
