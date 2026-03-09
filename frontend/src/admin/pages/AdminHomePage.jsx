import { useNavigate } from 'react-router-dom';
import AdminLayout from '../../shared/layout/AdminLayout';

export default function AdminHomePage() {
  const navigate = useNavigate();

  return (
    <AdminLayout title="后台概览" description="集中管理文章、分类标签与作者资料。" navigate={navigate}>
      <section className="dashboard-grid">
        <article className="panel-card">
          <h3>写作工作区</h3>
          <p className="muted">进入文章管理页，完成新建、编辑、导入导出和发布操作。</p>
        </article>
        <article className="panel-card">
          <h3>内容组织</h3>
          <p className="muted">通过分类与标签维护文章结构，保持首页与详情页展示整洁。</p>
        </article>
        <article className="panel-card">
          <h3>作者资料</h3>
          <p className="muted">补齐昵称、简介和邮箱，让作者页更像真实博客主页。</p>
        </article>
      </section>
    </AdminLayout>
  );
}
