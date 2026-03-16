import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import { formatDate } from '../../shared/utils/format';
import PublicLayout from '../../shared/layout/PublicLayout';
import { PostListSkeleton } from '../../shared/components/Skeleton';

export default function PublicHomePage() {
  const [posts, setPosts] = useState([]);
  const [error, setError] = useState('');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    apiRequest('/posts')
      .then((data) => setPosts(data || []))
      .catch((e) => setError(e.message || 'load_failed'))
      .finally(() => setLoaded(true));
  }, []);

  return (
    <PublicLayout title="首页" description="记录技术实践、代码思考与系统构建。">
      {error ? <div className="notice error">{error}</div> : null}
      {!loaded ? (
        <PostListSkeleton />
      ) : null}
      {loaded && !posts.length ? (
        <div className="notice muted">暂无已发布文章，请先登录后台发布内容。</div>
      ) : null}

      <section className="post-list-grid">
        {posts.map((post) => (
          <article key={post.id} className="post-card">
            <div className="post-meta-row">
              <time>{formatDate(post.published_at)}</time>
              {post.category_slug ? (
                <Link to={`/categories/${post.category_slug}`} className="nav-link">{post.category_name || '未分类'}</Link>
              ) : (
                <span>{post.category_name || '未分类'}</span>
              )}
            </div>
            <h2 className="post-card-title">
              <Link to={`/posts/${post.slug}`}>{post.title}</Link>
            </h2>
            <p className="post-card-summary">{post.summary || '点击查看完整内容。'}</p>
            <div className="post-tag-list">
              {(post.tags || []).map((tag) => (
                <Link key={tag.id} to={`/tags/${tag.slug}`} className="tag-chip">#{tag.name}</Link>
              ))}
            </div>
          </article>
        ))}
      </section>
    </PublicLayout>
  );
}