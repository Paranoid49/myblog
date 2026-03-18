import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import { formatDate } from '../../shared/utils/format';
import MarkdownRenderer from '../../shared/markdown/MarkdownRenderer';
import { PostDetailSkeleton } from '../../shared/components/Skeleton';

// 模块级缓存，按 slug 存储已加载的文章
const postCache = new Map();

// 供测试使用，清除缓存
export function _clearPostCache() {
  postCache.clear();
}

export default function PublicPostDetailPage() {
  const { slug } = useParams();
  const cached = postCache.get(slug);
  const [post, setPost] = useState(cached || null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!slug) return;
    if (postCache.has(slug)) {
      setPost(postCache.get(slug));
      return;
    }
    setPost(null);
    apiRequest(`/posts/${encodeURIComponent(slug)}`)
      .then((data) => {
        postCache.set(slug, data);
        setPost(data);
      })
      .catch((e) => setError(e.message || 'load_failed'));
  }, [slug]);

  return (
    <>
      {error ? <div className="notice error">{error}</div> : null}
      {!post ? <PostDetailSkeleton /> : null}

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
            <div className="post-tag-list mb-lg">
              {post.tags.map((tag) => (
                <Link key={tag.id} to={`/tags/${tag.slug}`} className="tag-chip">#{tag.name}</Link>
              ))}
            </div>
          ) : null}
          <MarkdownRenderer content={post.content || ''} />
        </article>
      ) : null}
    </>
  );
}