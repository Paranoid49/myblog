import { Navigate, useLocation } from 'react-router-dom';
import { hasStoredUserSnapshot } from './session';
import { getAuthGuardRedirect } from './navigation';

export default function AuthGuard({ children }) {
  const location = useLocation();
  const redirect = getAuthGuardRedirect(location.pathname, hasStoredUserSnapshot());

  if (redirect) {
    return <Navigate to={redirect.to} replace state={redirect.state} />;
  }

  return children;
}
