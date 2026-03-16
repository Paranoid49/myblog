import { Link, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { apiRequest } from '../../shared/api/client';
import { formatDate } from '../../shared/utils/format';
import PublicLayout from '../../shared/layout/PublicLayout';

export default function PublicTaxonomyListPage({ type }) {
  const { slug } = useParams();
  const [payload, setPayload] = useState(null);
  const [error, setError] = useState('');

  const isCategory = type === 'category';
  const apiPath = isCategory ? 'categories' : 'tags';
  const label = isCategory ? '分类' : '标签';

  useEffect(() => {
    if (!slug) return;
    setPayload(null);
    setError('');
    apiRequest(`/${apiPath}/${encodeURIComponent(slug)}`)
      .then((data) => setPayload(data))
      .catch((e) => setError(e.message || 'load_failed'));
  }, [slug, apiPath]);

  const taxonomy = isCategory ? payload?.category : payload?.tag;
  const posts = payload?.posts || [];

  return (
    <PublicLayout
      title={taxonomy?.name || `${label}文章`}
      description={taxonomy ? `${label}：${isCategory ? '' : '#'}${taxonomy.name}` : `按${label}浏览文章。`}
    >
      <p className="mb-lg">
        <Link to="/" className="nav-link">← 返回首页</Link>
      </p>
      {error ? <div className="notice error">{error}</div> : null}
      {!payload ? <div className="notice muted">加载中...</div> : null}
      {payload && !posts.length ? <div className="notice muted">该{label}下暂无已发布文章。</div> : null}
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
