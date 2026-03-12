import { Navigate, useLocation } from 'react-router-dom';
import { hasStoredUser } from './session';

export default function AuthGuard({ children }) {
  const location = useLocation();
  const isLoggedIn = hasStoredUser();

  if (!isLoggedIn) {
    return <Navigate to="/admin/login" replace state={{ from: location.pathname }} />;
  }

  return children;
}
