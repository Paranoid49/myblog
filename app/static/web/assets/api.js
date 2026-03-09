const API_BASE = '/api/v1';

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: 'same-origin',
    ...options,
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch (_) {
    payload = { code: -1, message: 'invalid_json_response', data: null };
  }

  if (!response.ok || payload.code !== 0) {
    const message = payload?.message || `http_${response.status}`;
    throw new Error(message);
  }

  return payload.data;
}
