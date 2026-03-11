import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import AdminPostEditor from '../components/AdminPostEditor';
import AdminPostList from '../components/AdminPostList';
import AdminLayout from '../../shared/layout/AdminLayout';

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

  function handleFieldChange(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleToggleTag(tagId, checked) {
    setForm((prev) => {
      const next = new Set(prev.tag_ids.map((id) => Number(id)));
      if (checked) next.add(Number(tagId));
      else next.delete(Number(tagId));
      return { ...prev, tag_ids: [...next] };
    });
  }

  return (
    <AdminLayout title="文章管理" description="在这里完成写作、预览、筛选、导入导出和发布。" navigate={navigate}>
      {error ? <div className="notice error">{error}</div> : null}
      {message ? <div className="notice success">{message}</div> : null}

      <AdminPostEditor
        form={form}
        taxonomy={taxonomy}
        previewMode={previewMode}
        selectedTagIds={selectedTagIds}
        onPreviewModeChange={setPreviewMode}
        onReset={resetForm}
        onFieldChange={handleFieldChange}
        onToggleTag={handleToggleTag}
        onSubmit={submitForm}
        onImportMarkdown={importMarkdown}
        onUploadImage={uploadImage}
      />

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

      <AdminPostList
        posts={posts}
        onEdit={fillForEdit}
        onExport={exportMarkdown}
        onTogglePublish={togglePublish}
      />
    </AdminLayout>
  );
}
