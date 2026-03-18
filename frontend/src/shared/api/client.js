import { redirectToLoginAfterUnauthorized } from '../auth/session';

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

  redirectToLoginAfterUnauthorized();
}

// 可由外部注入的导航函数，用于 SPA 内跳转
let _navigateToSetup = null;

export function setSetupNavigator(fn) {
  _navigateToSetup = fn;
}

// 站点未初始化时自动跳转到 /setup
function handleNotInitialized(error) {
  if (error.status !== 409 || error.code !== 1001) {
    return;
  }

  if (window.location.pathname !== '/setup') {
    if (_navigateToSetup) {
      _navigateToSetup();
    } else {
      window.location.replace('/setup');
    }
  }
}

export async function apiRequest(path, options = {}) {
  const { headers: customHeaders, ...restOptions } = options;
  const response = await fetch(`/api/v1${path}`, {
    credentials: 'same-origin',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      ...customHeaders,
    },
    ...restOptions,
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
    handleNotInitialized(error);
    throw error;
  }

  if (!response.ok || payload.code !== 0) {
    const error = createApiError({
      status: response.status,
      code: payload?.code ?? null,
      message: payload?.message || `http_${response.status}`,
    });
    handleUnauthorized(error);
    handleNotInitialized(error);
    throw error;
  }

  return payload.data;
}
