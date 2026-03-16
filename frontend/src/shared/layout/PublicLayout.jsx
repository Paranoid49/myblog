import { Link, useLocation } from 'react-router-dom';
import { getAdminEntryPath } from '../auth/session';
import { useTheme } from '../theme/ThemeProvider';
import { useSite } from '../site/SiteProvider';

export default function PublicLayout({ title, description, children }) {
  const { blogTitle } = useSite();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <div className="site-frame">
      <header className="site-header">
        <div className="site-header-inner">
          <div>
            <Link className="brand-link" to="/">{blogTitle || 'myblog'}</Link>
            <p className="site-description">技术博客 · React + FastAPI</p>
          </div>
          <nav className="site-nav">
            <Link to="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>
              首页
            </Link>
            <Link to="/author" className={`nav-link ${isActive('/author') ? 'active' : ''}`}>
              作者
            </Link>
            <Link to={getAdminEntryPath()} className="nav-link">
              后台
            </Link>
            <button type="button" className="ghost-button" onClick={toggleTheme}>
              {theme === 'dark' ? '☀' : '☾'}
            </button>
          </nav>
        </div>
      </header>

      <main className="app-shell public-shell">
        <section className="page-hero">
          <h1>{title}</h1>
          {description ? <p className="hero-description muted">{description}</p> : null}
        </section>
        {children}
      </main>

      <footer className="site-footer">
        myblog · 基于 React + FastAPI 构建
      </footer>
    </div>
  );
}