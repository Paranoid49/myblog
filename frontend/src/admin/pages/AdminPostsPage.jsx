import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import AdminLayout from '../../shared/layout/AdminLayout';
import MarkdownRenderer from '../../shared/markdown/MarkdownRenderer';

function toQuery(params) {
  const url = new URLSearchParams();
  if (params.category_id) url.set('category_id', String(params.category_id));
  if (params.tag_id) url.set('tag_id', String(params.tag_id));
  const query = url.toString();
  return query ? `?${query}` : '';
}

export default function AdminPostsPage() {
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [taxonomy, setTaxonomy] = useState({ categories: [], tags: [] });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [filter, setFilter] = useState({ category_id: '', tag_id: '' });
  const [previewMode, setPreviewMode] = useState('edit');
  const [form, setForm] = useState({ id: null, title: '', summary: '', content: '', category_id: '', tag_ids: [] });

  const selectedTagIds = useMemo(() => new Set(form.tag_ids.map((x) => Number(x))), [form.tag_ids]);

  async function loadTaxonomy() {
    const data = await apiRequest('/taxonomy');
    setTaxonomy({ categories: data.categories || [], tags: data.tags || [] });
  }

  async function loadPosts(nextFilter = filter) {
    const query = toQuery(nextFilter);
    const data = await apiRequest(`/admin/posts${query}`);
    setPosts(data || []);
  }

  useEffect(() => {
    Promise.all([loadTaxonomy(), loadPosts()]).catch((e) => setError(e.message || 'load_failed'));
  }, []);

  function resetForm() {
    setForm({ id: null, title: '', summary: '', content: '', category_id: '', tag_ids: [] });
    setPreviewMode('edit');
  }

  function fillForEdit(post) {
    setForm({
      id: post.id,
      title: post.title || '',
      summary: post.summary || '',
      content: post.content || '',
      category_id: post.category_id ? String(post.category_id) : '',
      tag_ids: (post.tag_ids || []).map((id) => Number(id)),
    });
    setPreviewMode('preview');
    setMessage('');
  }

  async function submitForm(event) {
    event.preventDefault();
    setError('');
    setMessage('');

    const payload = {
      title: form.title,
      summary: form.summary || null,
      content: form.content,
      category_id: form.category_id ? Number(form.category_id) : null,
      tag_ids: form.tag_ids.map((id) => Number(id)),
    };

    try {
      if (form.id) {
        await apiRequest(`/admin/posts/${form.id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        setMessage('文章已更新');
      } else {
        await apiRequest('/admin/posts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        setMessage('文章已创建');
      }
      resetForm();
      await loadPosts();
    } catch (e) {
      setError(e.message || 'submit_failed');
    }
  }

  async function importMarkdown(event) {
    event.preventDefault();
    setError('');
    setMessage('');
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const markdown = await file.text();
      await apiRequest('/admin/posts/import-markdown', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ markdown, category_id: null, tag_ids: [] }),
      });
      setMessage('Markdown 导入成功');
      await loadPosts();
    } catch (e) {
      setError(e.message || 'import_failed');
    } finally {
      event.target.value = '';
    }
  }

  async function exportMarkdown(postId) {
    try {
      const data = await apiRequest(`/admin/posts/${postId}/export-markdown`);
      const blob = new Blob([data.markdown || ''], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = data.filename || 'post.md';
      a.click();
      URL.revokeObjectURL(url);
      setMessage('Markdown 已导出');
    } catch (e) {
      setError(e.message || 'export_failed');
    }
  }

  async function uploadImage(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setError('');
    setMessage('');
    try {
      const body = new FormData();
      body.set('file', file);
      const data = await apiRequest('/admin/media/images', { method: 'POST', body });
      setForm((prev) => ({ ...prev, content: `${prev.content}\n\n![image](${data.url})\n` }));
      setMessage('图片已插入 Markdown');
    } catch (e) {
      setError(e.message || 'upload_failed');
    } finally {
      event.target.value = '';
    }
  }

  async function togglePublish(postId, action) {
    try {
      await apiRequest(`/admin/posts/${postId}/${action}`, { method: 'POST' });
      setMessage(action === 'publish' ? '文章已发布' : '文章已转为草稿');
      await loadPosts();
    } catch (e) {
      setError(e.message || 'publish_failed');
    }
  }

  async function applyFilter(next) {
    setFilter(next);
    await loadPosts(next);
  }

  return (
    <AdminLayout title="文章管理" description="在这里完成写作、预览、筛选、导入导出和发布。" navigate={navigate}>
      {error ? <div className="notice error">{error}</div> : null}
      {message ? <div className="notice success">{message}</div> : null}

      <section className="panel-card">
        <div className="section-head">
          <h3>{form.id ? '编辑文章' : '新建文章'}</h3>
          <div className="inline-actions">
            <button type="button" className={previewMode === 'edit' ? 'primary-button' : 'ghost-button'} onClick={() => setPreviewMode('edit')}>编辑</button>
            <button type="button" className={previewMode === 'preview' ? 'primary-button' : 'ghost-button'} onClick={() => setPreviewMode('preview')}>预览</button>
            <button type="button" className="ghost-button" onClick={resetForm}>清空</button>
          </div>
        </div>

        <form onSubmit={submitForm} className="editor-layout">
          <div className="editor-form-grid">
            <label>
              标题
              <input value={form.title} onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))} required />
            </label>

            <label>
              摘要
              <textarea value={form.summary} onChange={(e) => setForm((prev) => ({ ...prev, summary: e.target.value }))} rows={3} />
            </label>

            <label>
              分类
              <select value={form.category_id} onChange={(e) => setForm((prev) => ({ ...prev, category_id: e.target.value }))}>
                <option value="">默认分类</option>
                {taxonomy.categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </label>

            <fieldset>
              <legend>标签</legend>
              <div className="checkbox-wrap">
                {taxonomy.tags.map((t) => (
                  <label key={t.id} className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={selectedTagIds.has(Number(t.id))}
                      onChange={(e) => {
                        setForm((prev) => {
                          const next = new Set(prev.tag_ids.map((id) => Number(id)));
                          if (e.target.checked) next.add(Number(t.id));
                          else next.delete(Number(t.id));
                          return { ...prev, tag_ids: [...next] };
                        });
                      }}
                    />
                    {t.name}
                  </label>
                ))}
              </div>
            </fieldset>

            <label>
              Markdown 正文
              <textarea
                value={form.content}
                onChange={(e) => setForm((prev) => ({ ...prev, content: e.target.value }))}
                rows={16}
                required
                className="editor-textarea"
              />
            </label>

            <div className="toolbar-row">
              <label className="file-action">
                导入 Markdown
                <input type="file" accept=".md,text/markdown" onChange={importMarkdown} />
              </label>
              <label className="file-action">
                上传图片
                <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={uploadImage} />
              </label>
              <button type="submit" className="primary-button">{form.id ? '保存修改' : '创建文章'}</button>
            </div>
          </div>

          <aside className="preview-panel">
            <h4>预览</h4>
            {previewMode === 'preview' ? <MarkdownRenderer content={form.content || '暂无内容'} /> : <p className="muted">切换到预览模式后查看渲染结果。</p>}
          </aside>
        </form>
      </section>

      <section className="panel-card">
        <div className="section-head">
          <h3>筛选</h3>
        </div>
        <div className="filter-row">
          <select value={filter.category_id} onChange={(e) => applyFilter({ ...filter, category_id: e.target.value })}>
            <option value="">全部分类</option>
            {taxonomy.categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <select value={filter.tag_id} onChange={(e) => applyFilter({ ...filter, tag_id: e.target.value })}>
            <option value="">全部标签</option>
            {taxonomy.tags.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </div>
      </section>

      <section className="panel-card">
        <div className="section-head">
          <h3>文章列表</h3>
        </div>
        {!posts.length ? <p className="muted">暂无文章</p> : null}
        <div className="admin-post-list">
          {posts.map((post) => (
            <article key={post.id} className="admin-post-item">
              <div>
                <h4>{post.title}</h4>
                <p className="muted">slug：{post.slug}</p>
                <p className="muted">状态：{post.published_at ? '已发布' : '草稿'}</p>
              </div>
              <div className="inline-actions">
                <button type="button" className="ghost-button" onClick={() => fillForEdit(post)}>编辑</button>
                <button type="button" className="ghost-button" onClick={() => exportMarkdown(post.id)}>导出</button>
                <button type="button" className="primary-button" onClick={() => togglePublish(post.id, 'publish')}>发布</button>
                <button type="button" className="ghost-button" onClick={() => togglePublish(post.id, 'unpublish')}>转草稿</button>
              </div>
            </article>
          ))}
        </div>
      </section>
    </AdminLayout>
  );
}
