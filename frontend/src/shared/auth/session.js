const STORAGE_KEY = 'myblog_user';
const LOGIN_PATH = '/admin/login';

export function getStoredUserSnapshot() {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY);
    return value ? JSON.parse(value) : null;
  } catch (_) {
    return null;
  }
}

export function setStoredUserSnapshot(user) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
}

export function clearStoredUserSnapshot() {
  window.localStorage.removeItem(STORAGE_KEY);
}

export function hasStoredUserSnapshot() {
  return Boolean(getStoredUserSnapshot());
}

export function redirectToLoginAfterUnauthorized() {
  clearStoredUserSnapshot();

  if (typeof window !== 'undefined' && window.location.pathname !== LOGIN_PATH) {
    window.location.assign(LOGIN_PATH);
  }
}
