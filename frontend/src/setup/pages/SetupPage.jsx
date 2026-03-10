import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import { setStoredUser } from '../../shared/auth/session';

export default function SetupPage() {
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [blogTitle, setBlogTitle] = useState('我的博客');
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    async function checkStatus() {
      try {
        const data = await apiRequest('/setup/status');
        if (data.initialized) {
          navigate('/', { replace: true });
        }
      } catch (e) {
        // 忽略错误，允许继续显示 setup 页面
      } finally {
        setLoading(false);
      }
    }
    checkStatus();
  }, [navigate]);

  async function onSubmit(event) {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const data = await apiRequest('/setup', {
        method: 'POST',
        body: JSON.stringify({
          blog_title: blogTitle,
          username,
          password,
          confirm_password: confirmPassword,
        }),
        headers: { 'Content-Type': 'application/json' },
      });
      setStoredUser({ user_id: data.user_id, username: data.username });
      navigate('/admin', { replace: true });
    } catch (e) {
      setError(e.message || 'setup_failed');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <main style={{ maxWidth: 420, margin: '40px auto', padding: 16 }}>
        <p>正在检查初始化状态...</p>
      </main>
    );
  }

  return (
    <main style={{ maxWidth: 420, margin: '40px auto', padding: 16, background: 'var(--bg)', borderRadius: 8 }}>
      <h1>博客初始化</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>首次运行需要初始化站点和管理员账号</p>
      {error ? <p style={{ color: '#c00' }}>{error}</p> : null}
      <form onSubmit={onSubmit}>
        <label style={{ display: 'block', marginBottom: 12 }}>
          博客标题
          <input
            value={blogTitle}
            onChange={(e) => setBlogTitle(e.target.value)}
            type="text"
            required
            style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
          />
        </label>
        <label style={{ display: 'block', marginBottom: 12 }}>
          管理员用户名
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
        <label style={{ display: 'block', marginBottom: 12 }}>
          确认密码
          <input
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            type="password"
            required
            style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
          />
        </label>
        <button type="submit" disabled={submitting} style={{ width: '100%', padding: 10 }}>
          {submitting ? '初始化中...' : '初始化'}
        </button>
      </form>
    </main>
  );
}