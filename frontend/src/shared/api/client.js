export async function apiRequest(path, options = {}) {
  const response = await fetch(`/api/v1${path}`, {
    credentials: 'same-origin',
    ...options,
  });

  let payload;
  try {
    payload = await response.json();
  } catch (_) {
    throw new Error(`http_${response.status}`);
  }

  if (!response.ok || payload.code !== 0) {
    throw new Error(payload?.message || `http_${response.status}`);
  }

  return payload.data;
}
