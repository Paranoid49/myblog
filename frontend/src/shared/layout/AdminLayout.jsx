import { Link, useLocation } from 'react-router-dom';
import { apiRequest } from '../api/client';
import { getStoredUserSnapshot, logoutWithUserSnapshot } from '../auth/session';

export default function AdminLayout({ title, description, navigate, children }) {
  const user = getStoredUserSnapshot();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  async function logout() {
    try {
      await apiRequest('/auth/logout', { method: 'POST' });
    } finally {
      logoutWithUserSnapshot({ navigate });
    }
  }

  return (
    <div className="admin-frame">
      <aside className="admin-sidebar">
        <div>
          <h1 className="admin-brand"><Link to="/admin">myblog</Link></h1>
          <p className="muted admin-user-info">
            {user?.username || 'unknown'}
          </p>
        </div>
        <nav className="admin-nav">
          <Link to="/admin" className={isActive('/admin') ? 'active' : ''}>
            概览
          </Link>
          <Link to="/admin/posts" className={isActive('/admin/posts') ? 'active' : ''}>
            文章
          </Link>
          <Link to="/admin/taxonomy" className={isActive('/admin/taxonomy') ? 'active' : ''}>
            分类标签
          </Link>
          <Link to="/admin/author" className={isActive('/admin/author') ? 'active' : ''}>
            作者
          </Link>
        </nav>
        <button type="button" className="ghost-button" onClick={logout}>
          退出登录
        </button>
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