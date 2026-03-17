const STORAGE_KEY = 'myblog_user';
const LOGIN_PATH = '/admin/login';
const ADMIN_HOME_PATH = '/admin';

function canUseLocalStorage() {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
}

export function getStoredUserSnapshot() {
  if (!canUseLocalStorage()) {
    return null;
  }

  try {
    const value = window.localStorage.getItem(STORAGE_KEY);
    return value ? JSON.parse(value) : null;
  } catch (_) {
    return null;
  }
}

export function setStoredUserSnapshot(user) {
  if (!canUseLocalStorage()) {
    return;
  }

  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  } catch (_) {
    // Safari 隐私模式等场景下忽略
  }
}

export function clearStoredUserSnapshot() {
  if (!canUseLocalStorage()) {
    return;
  }

  try {
    window.localStorage.removeItem(STORAGE_KEY);
  } catch (_) {
    // Safari 隐私模式等场景下忽略
  }
}

export function hasStoredUserSnapshot() {
  return Boolean(getStoredUserSnapshot());
}

export function getAdminEntryPath() {
  return hasStoredUserSnapshot() ? ADMIN_HOME_PATH : LOGIN_PATH;
}

export function getLoginRedirectPath(locationState) {
  return locationState?.from || ADMIN_HOME_PATH;
}

export function getLoginNavigationState(from) {
  return from ? { from } : undefined;
}

export function loginWithUserSnapshot({ navigate, user, redirectTo }) {
  setStoredUserSnapshot(user);
  navigate(redirectTo || ADMIN_HOME_PATH, { replace: true });
}

export function logoutWithUserSnapshot({ navigate }) {
  clearStoredUserSnapshot();
  navigate(LOGIN_PATH, { replace: true });
}

export function redirectToLoginAfterUnauthorized() {
  clearStoredUserSnapshot();

  if (typeof window !== 'undefined' && window.location.pathname !== LOGIN_PATH) {
    window.location.assign(LOGIN_PATH);
  }
}
