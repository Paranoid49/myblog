import { Link, useLocation } from 'react-router-dom';
import { Outlet } from 'react-router-dom';
import { useTheme } from '../theme/ThemeProvider';
import { useSite } from '../site/SiteProvider';

export default function PublicLayout() {
  const { blogTitle } = useSite();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <div className="site-frame">
      <header className="site-header">
        <div className="site-header-inner">
          <Link className="brand-link" to="/">{blogTitle || 'myblog'}</Link>
          <nav className="site-nav">
            <Link to="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>
              首页
            </Link>
            <Link to="/author" className={`nav-link ${isActive('/author') ? 'active' : ''}`}>
              关于
            </Link>
            <button type="button" className="ghost-button theme-toggle" onClick={toggleTheme} aria-label="切换主题">
              {theme === 'dark' ? '☀' : '☾'}
            </button>
          </nav>
        </div>
      </header>

      <main className="app-shell public-shell">
        <Outlet />
      </main>

      <footer className="site-footer">
        &copy; {new Date().getFullYear()} {blogTitle || 'myblog'}
      </footer>
    </div>
  );
}

export function PageHero({ title, description }) {
  if (!title) return null;
  return (
    <section className="page-hero">
      <h1>{title}</h1>
      {description ? <p className="hero-description muted">{description}</p> : null}
    </section>
  );
}
