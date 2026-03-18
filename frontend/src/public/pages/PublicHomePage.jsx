import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import { formatDate } from '../../shared/utils/format';
import { PostListSkeleton } from '../../shared/components/Skeleton';
import Pagination from '../../shared/components/Pagination';

// 模块级缓存，组件卸载后数据不丢失
let cachedPage = 1;
let cachedData = null;

// 供测试使用，清除缓存
export function _clearHomeCache() {
  cachedPage = 1;
  cachedData = null;
}

export default function PublicHomePage() {
  const [posts, setPosts] = useState(cachedData?.items || []);
  const [error, setError] = useState('');
  const [loaded, setLoaded] = useState(!!cachedData);
  const [page, setPage] = useState(cachedPage);
  const [totalPages, setTotalPages] = useState(cachedData?.total_pages || 1);

  useEffect(() => {
    // 同页有缓存则跳过请求
    if (cachedData && page === cachedPage) return;

    setLoaded(false);
    apiRequest(`/posts?page=${page}&page_size=20`)
      .then((data) => {
        setPosts(data?.items || []);
        setTotalPages(data?.total_pages || 1);
        cachedData = data;
        cachedPage = page;
      })
      .catch((e) => setError(e.message || 'load_failed'))
      .finally(() => setLoaded(true));
  }, [page]);

  return (
    <>
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
      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
    </>
  );
}