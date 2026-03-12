const STORAGE_KEY = 'myblog_user';

export function getStoredUser() {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY);
    return value ? JSON.parse(value) : null;
  } catch (_) {
    return null;
  }
}

export function setStoredUser(user) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
}

export function clearStoredUser() {
  window.localStorage.removeItem(STORAGE_KEY);
}

export function hasStoredUser() {
  return Boolean(getStoredUser());
}
