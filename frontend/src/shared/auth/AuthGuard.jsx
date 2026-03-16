import { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { apiRequest } from '../api/client';
import { hasStoredUserSnapshot, clearStoredUserSnapshot } from './session';

export default function AuthGuard({ children }) {
    const location = useLocation();
    const [checking, setChecking] = useState(true);
    const [valid, setValid] = useState(false);

    useEffect(() => {
        if (!hasStoredUserSnapshot()) {
            setChecking(false);
            return;
        }
        // 轻量验证：请求一个需要登录的接口确认 session 有效
        apiRequest('/taxonomy')
            .then(() => setValid(true))
            .catch(() => {
                clearStoredUserSnapshot();
                setValid(false);
            })
            .finally(() => setChecking(false));
    }, []);

    if (checking) {
        return <div className="notice muted">验证登录状态...</div>;
    }
    if (!valid) {
        return <Navigate to="/admin/login" replace state={{ from: location.pathname }} />;
    }
    return children;
}
