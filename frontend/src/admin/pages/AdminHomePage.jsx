import { Link, useNavigate } from 'react-router-dom';
import AdminLayout from '../../shared/layout/AdminLayout';

export default function AdminHomePage() {
  const navigate = useNavigate();

  return (
    <AdminLayout title="概览" description="集中管理文章、分类标签与作者资料。" navigate={navigate}>
      <section className="dashboard-grid">
        <article className="panel-card">
          <h3>写作工作区</h3>
          <p className="muted">新建、编辑、导入导出和发布文章。</p>
          <Link to="/admin/posts" className="nav-link inline-block-link">
            进入 →
          </Link>
        </article>
        <article className="panel-card">
          <h3>内容组织</h3>
          <p className="muted">管理分类与标签，保持内容结构清晰。</p>
          <Link to="/admin/taxonomy" className="nav-link inline-block-link">
            进入 →
          </Link>
        </article>
        <article className="panel-card">
          <h3>作者资料</h3>
          <p className="muted">编辑昵称、简介和邮箱，展示个人信息。</p>
          <Link to="/admin/author" className="nav-link inline-block-link">
            进入 →
          </Link>
        </article>
      </section>

      <section className="mt-xl">
        <div className="panel-card">
          <h3>快捷操作</h3>
          <div className="toolbar-row mt-md">
            <Link to="/admin/posts?mode=edit" className="primary-button">新建文章</Link>
            <Link to="/" className="ghost-button">查看站点</Link>
          </div>
        </div>
      </section>
    </AdminLayout>
  );
}