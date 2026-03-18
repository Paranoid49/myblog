import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import { setStoredUserSnapshot } from '../../shared/auth/session';

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
        // 忽略错误
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
      setStoredUserSnapshot({ user_id: data.user_id, username: data.username });
      navigate('/admin', { replace: true });
    } catch (e) {
      setError(e.message || 'setup_failed');
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return null;
  }

  return (
    <div className="site-frame center-frame">
      <div className="panel-card setup-card">
        <h2 className="mb-sm">
          博客初始化
        </h2>
        <p className="muted mb-lg">
          首次运行，请设置站点信息和管理员账号。
        </p>

        {error ? <div className="notice error">{error}</div> : null}

        <form onSubmit={onSubmit} className="stack-form">
          <div>
            <label className="form-label">
              博客标题
            </label>
            <input
              value={blogTitle}
              onChange={(e) => setBlogTitle(e.target.value)}
              type="text"
              required
              className="full-width"
            />
          </div>
          <div>
            <label className="form-label">
              管理员用户名
            </label>
            <input
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
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
              className="full-width"
            />
          </div>
          <div>
            <label className="form-label">
              确认密码
            </label>
            <input
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              type="password"
              required
              className="full-width"
            />
          </div>
          <button type="submit" className="primary-button mt-md" disabled={submitting}>
            {submitting ? '初始化中...' : '初始化'}
          </button>
        </form>
      </div>
    </div>
  );
}
