import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../shared/api/client';
import AdminLayout from '../../shared/layout/AdminLayout';

export default function AdminAuthorPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', bio: '', email: '' });
  const [error, setError] = useState('');
  const [saved, setSaved] = useState('');

  useEffect(() => {
    apiRequest('/author')
      .then((data) => setForm({ name: data.name || '', bio: data.bio || '', email: data.email || '' }))
      .catch((e) => setError(e.message || 'load_failed'));
  }, []);

  async function submit(event) {
    event.preventDefault();
    setError('');
    setSaved('');
    try {
      const data = await apiRequest('/author', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      setForm({ name: data.name || '', bio: data.bio || '', email: data.email || '' });
      setSaved('保存成功');
    } catch (e) {
      setError(e.message || 'save_failed');
    }
  }

  return (
    <AdminLayout title="作者资料管理" description="维护前台作者页展示内容。" navigate={navigate}>
      {error ? <div className="notice error">{error}</div> : null}
      {saved ? <div className="notice success">{saved}</div> : null}

      <section className="dashboard-grid two-col">
        <article className="panel-card">
          <h3>资料编辑</h3>
          <form onSubmit={submit} className="stack-form">
            <label>
              昵称
              <input value={form.name} onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))} required />
            </label>
            <label>
              简介
              <textarea value={form.bio} onChange={(e) => setForm((prev) => ({ ...prev, bio: e.target.value }))} rows={6} />
            </label>
            <label>
              邮箱
              <input type="email" value={form.email} onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))} />
            </label>
            <button type="submit" className="primary-button">保存资料</button>
          </form>
        </article>

        <article className="panel-card">
          <h3>前台预览</h3>
          <div className="author-card compact">
            <div className="author-avatar">{(form.name || 'A').slice(0, 1).toUpperCase()}</div>
            <div className="author-content">
              <h4>{form.name || '未设置昵称'}</h4>
              <p className="author-bio">{form.bio || '这个作者还没有留下简介。'}</p>
              <p className="muted">联系邮箱：{form.email || '暂未公开'}</p>
            </div>
          </div>
        </article>
      </section>
    </AdminLayout>
  );
}
