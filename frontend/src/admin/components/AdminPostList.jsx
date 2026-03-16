import { getPostPublishAction } from './postActions';

export default function AdminPostList({ posts, onEdit, onExport, onPublish, onUnpublish, onDelete }) {
  return (
    <section className="panel-card">
      <div className="section-head">
        <h3>文章列表</h3>
      </div>
      {!posts.length ? <p className="muted">暂无文章</p> : null}
      <div className="admin-post-list">
        {posts.map((post) => {
          const publishAction = getPostPublishAction(post);
          const actionHandler = publishAction.handlerName === 'onUnpublish' ? onUnpublish : onPublish;

          return (
            <article key={post.id} className="admin-post-item">
              <div>
                <h4>{post.title}</h4>
                <p className="muted">slug：{post.slug}</p>
                <p className="muted">状态：{post.published_at ? '已发布' : '草稿'}</p>
              </div>
              <div className="inline-actions">
                <button type="button" className="ghost-button" onClick={() => onEdit(post)}>编辑</button>
                <button type="button" className="ghost-button" onClick={() => onExport(post.id)}>导出</button>
                <button type="button" className={publishAction.variant} onClick={() => actionHandler(post.id)}>
                  {publishAction.text}
                </button>
                <button type="button" className="ghost-button" onClick={() => onDelete(post.id)}>删除</button>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
