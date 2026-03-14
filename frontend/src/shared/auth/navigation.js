export function getAuthGuardRedirect(locationPathname, hasUserSnapshot) {
  if (hasUserSnapshot) {
    return null;
  }

  return {
    to: '/admin/login',
    state: locationPathname ? { from: locationPathname } : undefined,
  };
}
