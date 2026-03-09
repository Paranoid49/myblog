export function getStoredUser() {
  try {
    const value = window.localStorage.getItem('myblog_user');
    return value ? JSON.parse(value) : null;
  } catch (_) {
    return null;
  }
}

export function setStoredUser(user) {
  window.localStorage.setItem('myblog_user', JSON.stringify(user));
}

export function clearStoredUser() {
  window.localStorage.removeItem('myblog_user');
}
