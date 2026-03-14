import { clearStoredUser } from '../auth/session';

function createApiError({ status, code, message }) {
  const error = new Error(message || `http_${status}`);
  error.status = status;
  error.code = code;
  error.apiMessage = message || '';
  return error;
}

function handleUnauthorized(error) {
  if (error.status !== 401 || error.code !== 1002) {
    return;
  }

  clearStoredUser();

  if (typeof window !== 'undefined' && window.location.pathname !== '/admin/login') {
    window.location.assign('/admin/login');
  }
}

export async function apiRequest(path, options = {}) {
  const response = await fetch(`/api/v1${path}`, {
    credentials: 'same-origin',
    ...options,
  });

  let payload;
  try {
    payload = await response.json();
  } catch (_) {
    const error = createApiError({
      status: response.status,
      code: null,
      message: `http_${response.status}`,
    });
    handleUnauthorized(error);
    throw error;
  }

  if (!response.ok || payload.code !== 0) {
    const error = createApiError({
      status: response.status,
      code: payload?.code ?? null,
      message: payload?.message || `http_${response.status}`,
    });
    handleUnauthorized(error);
    throw error;
  }

  return payload.data;
}
