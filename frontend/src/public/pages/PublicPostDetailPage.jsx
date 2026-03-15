import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import { formatDate } from '../../shared/utils/format';
import PublicLayout from '../../shared/layout/PublicLayout';
import MarkdownRenderer from '../../shared/markdown/MarkdownRenderer';

export default function PublicPostDetailPage() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!slug) return;
    apiRequest(`/posts/${encodeURIComponent(slug)}`)
      .then((data) => setPost(data))
      .catch((e) => setError(e.message || 'load_failed'));
  }, [slug]);

  return (
    <PublicLayout title={post?.title || '文章详情'} description={post?.summary || ''}>
      <p style={{ marginBottom: 'var(--space-lg)' }}>
        <Link to="/" className="nav-link">← 返回首页</Link>
      </p>

      {error ? <div className="notice error">{error}</div> : null}
      {!post ? <div className="notice muted">加载中...</div> : null}

      {post ? (
        <article className="post-detail-card">
          <h1>{post.title}</h1>
          <div className="post-meta-detail">
            <span>
              <span className="label">发布于</span>
              <span className="value">{formatDate(post.published_at)}</span>
            </span>
            <span>
              <span className="label">分类</span>
              <span className="value">
                {post.category_slug ? (
                  <Link to={`/categories/${post.category_slug}`} className="nav-link">{post.category_name || '未分类'}</Link>
                ) : (
                  post.category_name || '未分类'
                )}
              </span>
            </span>
          </div>
          {(post.tags || []).length ? (
            <div className="post-tag-list" style={{ marginBottom: 'var(--space-lg)' }}>
              {post.tags.map((tag) => (
                <Link key={tag.id} to={`/tags/${tag.slug}`} className="tag-chip">#{tag.name}</Link>
              ))}
            </div>
          ) : null}
          <MarkdownRenderer content={post.content || ''} />
        </article>
      ) : null}
    </PublicLayout>
  );
}