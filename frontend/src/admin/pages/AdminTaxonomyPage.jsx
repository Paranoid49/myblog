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
            {categories.map((item) => (
              <div key={item.id} className="simple-list-item">
                <strong>{item.name}</strong>
                <span className="muted">{item.slug}</span>
              </div>
            ))}
          </div>
        </article>
        <article className="panel-card">
          <h3>标签列表</h3>
          <div className="simple-list">
            {tags.map((item) => (
              <div key={item.id} className="simple-list-item">
                <strong>{item.name}</strong>
                <span className="muted">{item.slug}</span>
              </div>
            ))}
          </div>
        </article>
      </section>
    </AdminLayout>
  );
}
