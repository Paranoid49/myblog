import { Navigate, useLocation } from 'react-router-dom';
import { hasStoredUserSnapshot } from './session';

export default function AuthGuard({ children }) {
  const location = useLocation();
  const hasUserSnapshot = hasStoredUserSnapshot();

  if (!hasUserSnapshot) {
    return <Navigate to="/admin/login" replace state={{ from: location.pathname }} />;
  }

  return children;
}
