import { Link } from 'react-router-dom';
import { apiRequest } from '../api/client';
import { clearStoredUser, getStoredUser } from '../auth/session';

export default function AdminLayout({ title, description, navigate, children }) {
  const user = getStoredUser();

  async function logout() {
    await apiRequest('/auth/logout', { method: 'POST' });
    clearStoredUser();
    navigate('/admin/login', { replace: true });
  }

  return (
    <div className="admin-frame">
      <aside className="admin-sidebar">
        <div>
          <p className="admin-kicker">管理后台</p>
          <h1 className="admin-brand">myblog</h1>
          <p className="muted">当前用户：{user?.username || 'unknown'}</p>
        </div>
        <nav className="admin-nav">
          <Link to="/admin">概览</Link>
          <Link to="/admin/posts">文章管理</Link>
          <Link to="/admin/taxonomy">分类与标签</Link>
          <Link to="/admin/author">作者资料</Link>
        </nav>
        <button type="button" className="ghost-button" onClick={logout}>退出登录</button>
      </aside>
      <main className="admin-main">
        <section className="admin-page-head">
          <h2>{title}</h2>
          {description ? <p className="muted">{description}</p> : null}
        </section>
        {children}
      </main>
    </div>
  );
}
