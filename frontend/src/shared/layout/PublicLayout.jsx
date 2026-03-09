import { Link } from 'react-router-dom';
import { useTheme } from '../theme/ThemeProvider';

export default function PublicLayout({ title, description, children }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="site-frame">
      <header className="site-header">
        <div>
          <Link className="brand-link" to="/">myblog</Link>
          <p className="site-description">轻量、可扩展的个人博客系统</p>
        </div>
        <nav className="site-nav">
          <Link to="/">首页</Link>
          <Link to="/author">作者</Link>
          <Link to="/admin/login">后台</Link>
          <button type="button" className="ghost-button" onClick={toggleTheme}>主题：{theme}</button>
        </nav>
      </header>

      <main className="app-shell public-shell">
        <section className="page-hero">
          <h1>{title}</h1>
          {description ? <p className="muted hero-text">{description}</p> : null}
        </section>
        {children}
      </main>

      <footer className="site-footer muted">基于 React + FastAPI 构建</footer>
    </div>
  );
}
