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
    <PublicLayout title="关于作者" description="这里展示站点作者的基本资料与联系方式。">
      <p>
        <Link to="/">← 返回首页</Link>
      </p>
      {error ? <div className="notice error">加载失败：{error}</div> : null}
      {!author ? <div className="notice muted">加载中...</div> : null}
      {author ? (
        <section className="author-card">
          <div className="author-avatar">{(author.name || 'A').slice(0, 1).toUpperCase()}</div>
          <div className="author-content">
            <h2>{author.name || '未设置昵称'}</h2>
            <p className="author-bio">{author.bio || '这个作者还没有留下简介。'}</p>
            <p className="muted">联系邮箱：{author.email || '暂未公开'}</p>
            <p>
              <Link to="/admin/author">进入后台编辑资料</Link>
            </p>
          </div>
        </section>
      ) : null}
    </PublicLayout>
  );
}
