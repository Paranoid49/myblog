import { useEffect, useState } from 'react';
import { apiRequest } from '../../shared/api/client';
import PublicLayout from '../../shared/layout/PublicLayout';

function renderAvatar(author) {
  if (author.avatar) {
    return <img src={author.avatar} alt={author.name || '作者头像'} className="author-avatar-image" />;
  }
  return (author.name || 'A').slice(0, 1).toUpperCase();
}

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
      {error ? <div className="notice error">{error}</div> : null}
      {!author ? <div className="notice muted">加载中...</div> : null}

      {author ? (
        <section className="author-card">
          <div className="author-avatar">{renderAvatar(author)}</div>
          <div className="author-content">
            <h2>{author.name || '未设置昵称'}</h2>
            <p className="author-bio">{author.bio || '这个作者还没有留下简介。'}</p>
            {author.link ? (
              <p className="mb-sm">
                个人链接：<a href={author.link} target="_blank" rel="noreferrer" className="nav-link">{author.link}</a>
              </p>
            ) : null}
            {author.email ? (
              <p className="muted mono-small">
                {'<'}{author.email}{'>'}
              </p>
            ) : null}
          </div>
        </section>
      ) : null}
    </PublicLayout>
  );
}