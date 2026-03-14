import { useNavigate } from 'react-router-dom';
import AdminLayout from '../../shared/layout/AdminLayout';
import AdminPostEditor from '../components/AdminPostEditor';
import AdminPostFilters from '../components/AdminPostFilters';
import AdminPostList from '../components/AdminPostList';
import useAdminPostsState from '../hooks/useAdminPostsState';

// 页面容器只负责文章管理编排，稳定逻辑下沉到轻量 hook，避免继续堆叠平台化职责。
export default function AdminPostsPage() {
  const navigate = useNavigate();
  const {
    posts,
    taxonomy,
    error,
    message,
    filter,
    previewMode,
    form,
    selectedTagIds,
    setPreviewMode,
    resetForm,
    fillForEdit,
    submitForm,
    importMarkdown,
    exportMarkdown,
    uploadImage,
    togglePublish,
    applyFilter,
    handleFieldChange,
    handleToggleTag,
  } = useAdminPostsState();

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

      <AdminPostFilters filter={filter} taxonomy={taxonomy} onApplyFilter={applyFilter} />

      <AdminPostList posts={posts} onEdit={fillForEdit} onExport={exportMarkdown} onTogglePublish={togglePublish} />
    </AdminLayout>
  );
}
