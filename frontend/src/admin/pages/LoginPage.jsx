import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
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
    <main style={{ maxWidth: 420, margin: '40px auto', padding: 16, background: '#fff', borderRadius: 8 }}>
      <h1>后台登录（React）</h1>
      {error ? <p style={{ color: '#c00' }}>{error}</p> : null}
      <form onSubmit={onSubmit}>
        <label style={{ display: 'block', marginBottom: 12 }}>
          用户名
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            type="text"
            required
            style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
          />
        </label>
        <label style={{ display: 'block', marginBottom: 12 }}>
          密码
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            required
            style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
          />
        </label>
        <button type="submit" disabled={submitting}>
          {submitting ? '登录中...' : '登录'}
        </button>
      </form>
    </main>
  );
}
