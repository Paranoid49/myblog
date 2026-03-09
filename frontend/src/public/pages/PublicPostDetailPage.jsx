import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import PublicLayout from '../../shared/layout/PublicLayout';
import MarkdownRenderer from '../../shared/markdown/MarkdownRenderer';

function formatDate(value) {
  if (!value) return '未发布';
  return new Date(value).toLocaleString('zh-CN', { hour12: false });
}

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
    <PublicLayout title={post?.title || '文章详情'} description={post?.summary || '阅读完整正文内容。'}>
      <p>
        <Link to="/">← 返回首页</Link>
      </p>
      {error ? <div className="notice error">加载失败：{error}</div> : null}
      {!post ? <div className="notice muted">加载中...</div> : null}
      {post ? (
        <article className="post-detail-card">
          <div className="post-meta-row muted">
            <span>发布时间：{formatDate(post.published_at)}</span>
            <span>分类：{post.category_name || '未分类'}</span>
          </div>
          {(post.tags || []).length ? (
            <div className="post-tag-list">
              {post.tags.map((tag) => (
                <span key={tag.id} className="tag-chip">#{tag.name}</span>
              ))}
            </div>
          ) : null}
          <MarkdownRenderer content={post.content || ''} />
        </article>
      ) : null}
    </PublicLayout>
  );
}
