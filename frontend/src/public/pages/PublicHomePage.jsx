import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import PublicLayout from '../../shared/layout/PublicLayout';

function formatDate(value) {
  if (!value) return '未发布';
  return new Date(value).toLocaleString('zh-CN', { hour12: false });
}

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
    <PublicLayout title="文章首页" description="记录技术实践、构建过程与独立博客系统思考。">
      {error ? <div className="notice error">加载失败：{error}</div> : null}
      {!loaded ? <div className="notice muted">正在加载文章列表...</div> : null}
      {loaded && !posts.length ? <div className="notice muted">暂无已发布文章，先去后台写一篇吧。</div> : null}

      <section className="post-list-grid">
        {posts.map((post) => (
          <article key={post.id} className="post-card">
            <div className="post-meta-row muted">
              <span>{formatDate(post.published_at)}</span>
              <span>{post.category_name || '未分类'}</span>
            </div>
            <h2 className="post-card-title">
              <Link to={`/posts/${post.slug}`}>{post.title}</Link>
            </h2>
            <p className="post-card-summary">{post.summary || '暂无摘要，点击进入查看完整正文。'}</p>
            <div className="post-tag-list">
              {(post.tags || []).length ? post.tags.map((tag) => <span key={tag.id} className="tag-chip">#{tag.name}</span>) : <span className="muted">无标签</span>}
            </div>
          </article>
        ))}
      </section>
    </PublicLayout>
  );
}
