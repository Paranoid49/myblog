import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import { setStoredUser } from '../../shared/auth/session';

export default function LoginPage() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const redirectTo = location.state?.from || '/admin';

  async function onSubmit(event) {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const form = new FormData();
      form.set('username', username);
      form.set('password', password);
      const data = await apiRequest('/auth/login', {
        method: 'POST',
        body: form,
      });
      setStoredUser(data);
      navigate(redirectTo, { replace: true });
    } catch (e) {
      setError(e.message || 'login_failed');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="site-frame" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div className="panel-card" style={{ width: '100%', maxWidth: 400, margin: 'var(--space-xl)' }}>
        <p className="admin-kicker">Authentication</p>
        <h2 style={{ fontFamily: 'var(--font-mono)', marginBottom: 'var(--space-md)' }}>
          {'>'} 登录
        </h2>

        {error ? <div className="notice error">{error}</div> : null}

        <form onSubmit={onSubmit} className="stack-form">
          <div>
            <label style={{ display: 'block', marginBottom: 'var(--space-xs)', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              用户名
            </label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              type="text"
              required
              style={{ width: '100%' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: 'var(--space-xs)', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              密码
            </label>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
              style={{ width: '100%' }}
            />
          </div>
          <button type="submit" className="primary-button" disabled={submitting} style={{ marginTop: 'var(--space-sm)' }}>
            {submitting ? '登录中...' : '登录'}
          </button>
        </form>

        <p style={{ marginTop: 'var(--space-lg)', textAlign: 'center' }}>
          <Link to="/" className="nav-link">← 返回首页</Link>
        </p>
      </div>
    </div>
  );
}