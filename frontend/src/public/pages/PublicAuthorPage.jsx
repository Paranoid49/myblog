import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import PublicLayout from '../../shared/layout/PublicLayout';

export default function PublicAuthorPage() {
  const [author, setAuthor] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    apiRequest('/author')
      .then((data) => setAuthor(data))
      .catch((e) => setError(e.message || 'load_failed'));
  }, []);

  return (
    <PublicLayout title="关于作者" description="站点作者的基本资料与联系方式。">
      <p style={{ marginBottom: 'var(--space-lg)' }}>
        <Link to="/" className="nav-link">← 返回首页</Link>
      </p>

      {error ? <div className="notice error">{error}</div> : null}
      {!author ? <div className="notice muted">加载中...</div> : null}

      {author ? (
        <section className="author-card">
          <div className="author-avatar">{(author.name || 'A').slice(0, 1).toUpperCase()}</div>
          <div className="author-content">
            <h2>{author.name || '未设置昵称'}</h2>
            <p className="author-bio">{author.bio || '这个作者还没有留下简介。'}</p>
            {author.email ? (
              <p className="muted" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>
                {'<'}{author.email}{'>'}
              </p>
            ) : null}
          </div>
        </section>
      ) : null}
    </PublicLayout>
  );
}