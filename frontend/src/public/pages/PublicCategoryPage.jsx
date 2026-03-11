import { Link, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { apiRequest } from '../../shared/api/client';
import PublicLayout from '../../shared/layout/PublicLayout';

function formatDate(value) {
  if (!value) return '未发布';
  const date = new Date(value);
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
}

export default function PublicCategoryPage() {
  const { slug } = useParams();
  const [payload, setPayload] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!slug) return;
    apiRequest(`/categories/${encodeURIComponent(slug)}`)
      .then((data) => setPayload(data))
      .catch((e) => setError(e.message || 'load_failed'));
  }, [slug]);

  const category = payload?.category;
  const posts = payload?.posts || [];

  return (
    <PublicLayout title={category?.name || '分类文章'} description={category ? `分类：${category.name}` : '按分类浏览文章。'}>
      <p style={{ marginBottom: 'var(--space-lg)' }}>
        <Link to="/" className="nav-link">← 返回首页</Link>
      </p>
      {error ? <div className="notice error">{error}</div> : null}
      {!payload ? <div className="notice muted">加载中...</div> : null}
      {payload && !posts.length ? <div className="notice muted">该分类下暂无已发布文章。</div> : null}
      <section className="post-list-grid">
        {posts.map((post) => (
          <article key={post.id} className="post-card">
            <div className="post-meta-row">
              <time>{formatDate(post.published_at)}</time>
              <span>{post.category_name || '未分类'}</span>
            </div>
            <h2 className="post-card-title">
              <Link to={`/posts/${post.slug}`}>{post.title}</Link>
            </h2>
            <p className="post-card-summary">{post.summary || '点击查看完整内容。'}</p>
          </article>
        ))}
      </section>
    </PublicLayout>
  );
}
