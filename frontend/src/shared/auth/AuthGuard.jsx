import { Navigate, useLocation } from 'react-router-dom';
import { getStoredUser } from './session';

export default function AuthGuard({ children }) {
  const location = useLocation();
  const user = getStoredUser();

  if (!user) {
    return <Navigate to="/admin/login" replace state={{ from: location.pathname }} />;
  }

  return children;
}
