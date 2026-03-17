import { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import { getLoginRedirectPath, hasStoredUserSnapshot, loginWithUserSnapshot } from '../../shared/auth/session';

export default function LoginPage() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const redirectTo = getLoginRedirectPath(location.state);
  const hasUserSnapshot = hasStoredUserSnapshot();

  if (hasUserSnapshot) {
    return <Navigate to="/admin" replace />;
  }

  async function onSubmit(event) {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const formData = new FormData(event.currentTarget);
      const form = new URLSearchParams();
      form.set('username', String(formData.get('username') || ''));
      form.set('password', String(formData.get('password') || ''));
      const data = await apiRequest('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: form.toString(),
      });
      loginWithUserSnapshot({ navigate, user: data, redirectTo });
    } catch (e) {
      setError(e.message || 'login_failed');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="site-frame center-frame">
      <div className="panel-card auth-card">
        <h2 className="mb-md">
          登录
        </h2>

        {error ? <div className="notice error">{error}</div> : null}

        <form onSubmit={onSubmit} className="stack-form">
          <div>
            <label className="form-label">
              用户名
            </label>
            <input
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              type="text"
              required
              className="full-width"
            />
          </div>
          <div>
            <label className="form-label">
              密码
            </label>
            <input
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
              className="full-width"
            />
          </div>
          <button type="submit" className="primary-button mt-sm" disabled={submitting}>
            {submitting ? '登录中...' : '登录'}
          </button>
        </form>

        <p className="mt-lg text-center">
          <Link to="/" className="nav-link">← 返回首页</Link>
        </p>
      </div>
    </div>
  );
}
