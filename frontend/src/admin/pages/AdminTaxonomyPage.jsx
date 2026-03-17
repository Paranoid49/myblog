import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import AdminLayout from '../../shared/layout/AdminLayout';

export default function AdminTaxonomyPage() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [categoryName, setCategoryName] = useState('');
  const [tagName, setTagName] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  // 正在编辑的项：{ type: 'category'|'tag', id, name }
  const [editing, setEditing] = useState(null);

  async function loadTaxonomy() {
    const data = await apiRequest('/taxonomy');
    setCategories(data.categories || []);
    setTags(data.tags || []);
  }

  useEffect(() => {
    loadTaxonomy().catch((e) => setError(e.message || 'load_failed'));
  }, []);

  async function createCategory(event) {
    event.preventDefault();
    setError('');
    setMessage('');
    try {
      await apiRequest('/admin/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: categoryName }),
      });
      setCategoryName('');
      setMessage('分类已创建');
      await loadTaxonomy();
    } catch (e) {
      setError(e.message || 'create_category_failed');
    }
  }

  async function createTag(event) {
    event.preventDefault();
    setError('');
    setMessage('');
    try {
      await apiRequest('/admin/tags', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: tagName }),
      });
      setTagName('');
      setMessage('标签已创建');
      await loadTaxonomy();
    } catch (e) {
      setError(e.message || 'create_tag_failed');
    }
  }

  // 进入编辑状态
  function startEditing(type, item) {
    setEditing({ type, id: item.id, name: item.name });
  }

  // 取消编辑
  function cancelEditing() {
    setEditing(null);
  }

  // 提交重命名
  async function submitRename() {
    if (!editing || !editing.name.trim()) return;
    setError('');
    setMessage('');
    const endpoint = editing.type === 'category'
      ? `/admin/categories/${editing.id}`
      : `/admin/tags/${editing.id}`;
    try {
      await apiRequest(endpoint, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: editing.name }),
      });
      setMessage(editing.type === 'category' ? '分类已重命名' : '标签已重命名');
      setEditing(null);
      await loadTaxonomy();
    } catch (e) {
      setError(e.message || 'rename_failed');
    }
  }

  // 删除分类或标签
  async function handleDelete(type, id) {
    if (!window.confirm('确定删除？')) return;
    setError('');
    setMessage('');
    const endpoint = type === 'category'
      ? `/admin/categories/${id}`
      : `/admin/tags/${id}`;
    try {
      await apiRequest(endpoint, { method: 'DELETE' });
      setMessage(type === 'category' ? '分类已删除' : '标签已删除');
      await loadTaxonomy();
    } catch (e) {
      setError(e.message || 'delete_failed');
    }
  }

  // 渲染单个列表项（普通状态 / 编辑状态）
  function renderItem(type, item) {
    const isEditing = editing && editing.type === type && editing.id === item.id;

    if (isEditing) {
      return (
        <div key={item.id} className="simple-list-item">
          <input
            value={editing.name}
            onChange={(e) => setEditing({ ...editing, name: e.target.value })}
            autoFocus
          />
          <div className="inline-actions">
            <button type="button" className="ghost-button" onClick={submitRename}>保存</button>
            <button type="button" className="ghost-button" onClick={cancelEditing}>取消</button>
          </div>
        </div>
      );
    }

    return (
      <div key={item.id} className="simple-list-item">
        <div>
          <strong>{item.name}</strong>
          <span className="muted">{item.slug}</span>
        </div>
        <div className="inline-actions">
          <button type="button" className="ghost-button" onClick={() => startEditing(type, item)}>编辑</button>
          <button type="button" className="ghost-button" onClick={() => handleDelete(type, item.id)}>删除</button>
        </div>
      </div>
    );
  }

  return (
    <AdminLayout title="分类与标签" description="维护文章组织结构，让首页和详情页展示更完整。" navigate={navigate}>
      {error ? <div className="notice error">{error}</div> : null}
      {message ? <div className="notice success">{message}</div> : null}

      <section className="dashboard-grid two-col">
        <article className="panel-card">
          <h3>创建分类</h3>
          <form onSubmit={createCategory} className="stack-form">
            <input value={categoryName} onChange={(e) => setCategoryName(e.target.value)} required placeholder="输入分类名称" />
            <button type="submit" className="primary-button">创建分类</button>
          </form>
        </article>
        <article className="panel-card">
          <h3>创建标签</h3>
          <form onSubmit={createTag} className="stack-form">
            <input value={tagName} onChange={(e) => setTagName(e.target.value)} required placeholder="输入标签名称" />
            <button type="submit" className="primary-button">创建标签</button>
          </form>
        </article>
      </section>

      <section className="dashboard-grid two-col">
        <article className="panel-card">
          <h3>分类列表</h3>
          <div className="simple-list">
            {categories.map((item) => renderItem('category', item))}
          </div>
        </article>
        <article className="panel-card">
          <h3>标签列表</h3>
          <div className="simple-list">
            {tags.map((item) => renderItem('tag', item))}
          </div>
        </article>
      </section>
    </AdminLayout>
  );
}
