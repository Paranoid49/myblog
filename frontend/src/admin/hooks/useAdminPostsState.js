import { useEffect, useMemo, useState } from 'react';
import { apiRequest } from '../../shared/api/client';
import {
  EMPTY_FILTER,
  EMPTY_FORM,
  appendMarkdownImage,
  buildJsonRequestOptions,
  buildMarkdownImportPayload,
  buildPostRequestPath,
  getPostSuccessMessage,
  runWithFeedback,
  toEditForm,
  toPostPayload,
  toQuery,
  toggleTagIds,
} from './useAdminPostsState.helpers';

export default function useAdminPostsState() {
  // hook 只负责文章页状态编排与 API 交互，不承载跨页面状态管理或 CMS 平台化逻辑。
  const [posts, setPosts] = useState([]);
  const [taxonomy, setTaxonomy] = useState({ categories: [], tags: [] });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [filter, setFilter] = useState(EMPTY_FILTER);
  const [previewMode, setPreviewMode] = useState('edit');
  const [form, setForm] = useState(EMPTY_FORM);
  // 分页状态
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const selectedTagIds = useMemo(() => new Set(form.tag_ids.map((id) => Number(id))), [form.tag_ids]);

  async function loadTaxonomy() {
    const data = await apiRequest('/taxonomy');
    setTaxonomy({ categories: data.categories || [], tags: data.tags || [] });
  }

  async function loadPosts(nextFilter = filter, targetPage = page) {
    const data = await apiRequest(`/admin/posts${toQuery(nextFilter, targetPage)}`);
    // 后端返回分页格式：{ items, total, page, page_size, total_pages }
    setPosts(data?.items || []);
    setTotalPages(data?.total_pages || 1);
  }

  function resetForm() {
    setForm(EMPTY_FORM);
    setPreviewMode('edit');
  }

  function fillForEdit(post) {
    setForm(toEditForm(post));
    setPreviewMode('preview');
    setMessage('');
    setError('');
  }

  async function reloadEditorData(nextFilter = filter) {
    await Promise.all([loadTaxonomy(), loadPosts(nextFilter)]);
  }

  async function initialize() {
    setError('');
    await reloadEditorData();
  }

  useEffect(() => {
    initialize().catch((e) => setError(e.message || 'load_failed'));
  }, []);

  // page 变化时重新加载文章列表（首次加载由 initialize 处理，跳过 page=1 的重复请求）
  useEffect(() => {
    if (page === 1) return;
    loadPosts(filter, page).catch((e) => setError(e.message || 'load_failed'));
  }, [page]);

  async function submitForm(event) {
    event.preventDefault();
    const payload = toPostPayload(form);
    const method = form.id ? 'PUT' : 'POST';
    const succeeded = await runWithFeedback(
      () => apiRequest(buildPostRequestPath(form.id), buildJsonRequestOptions(payload, method)),
      {
        setError,
        setMessage,
        successMessage: getPostSuccessMessage(form.id),
        failureMessage: 'submit_failed',
      },
    );

    if (!succeeded) return;

    resetForm();
    await loadPosts();
  }

  async function importMarkdown(event) {
    event.preventDefault();
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const markdown = await file.text();
      const succeeded = await runWithFeedback(
        () => apiRequest('/admin/posts/import-markdown', buildJsonRequestOptions(buildMarkdownImportPayload(markdown))),
        {
          setError,
          setMessage,
          successMessage: 'Markdown 导入成功',
          failureMessage: 'import_failed',
        },
      );

      if (!succeeded) return;
      await loadPosts();
    } finally {
      event.target.value = '';
    }
  }

  async function exportMarkdown(postId) {
    setError('');
    try {
      const data = await apiRequest(`/admin/posts/${postId}/export-markdown`);
      const blob = new Blob([data.markdown || ''], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = data.filename || 'post.md';
      link.click();
      URL.revokeObjectURL(url);
      setMessage('Markdown 已导出');
    } catch (e) {
      setError(e.message || 'export_failed');
    }
  }

  async function uploadImage(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const body = new FormData();
      body.set('file', file);
      let uploadedUrl = '';
      const succeeded = await runWithFeedback(
        async () => {
          const data = await apiRequest('/admin/media/images', { method: 'POST', body });
          uploadedUrl = data.url || '';
        },
        {
          setError,
          setMessage,
          successMessage: '图片已插入 Markdown',
          failureMessage: 'upload_failed',
        },
      );

      if (!succeeded || !uploadedUrl) return;
      setForm((prev) => ({ ...prev, content: appendMarkdownImage(prev.content, uploadedUrl) }));
    } finally {
      event.target.value = '';
    }
  }

  async function updatePostPublishState(postId, action, successMessage) {
    const succeeded = await runWithFeedback(
      () => apiRequest(`/admin/posts/${postId}/${action}`, { method: 'POST' }),
      {
        setError,
        setMessage,
        successMessage,
        failureMessage: 'publish_failed',
      },
    );

    if (!succeeded) return;
    await loadPosts();
  }

  function publishPost(postId) {
    return updatePostPublishState(postId, 'publish', '文章已发布');
  }

  function unpublishPost(postId) {
    return updatePostPublishState(postId, 'unpublish', '文章已转为草稿');
  }

  // 删除文章，需用户确认
  async function deletePost(postId) {
    if (!window.confirm('确定删除这篇文章？')) return;
    const succeeded = await runWithFeedback(
      () => apiRequest(`/admin/posts/${postId}`, { method: 'DELETE' }),
      {
        setError,
        setMessage,
        successMessage: '文章已删除',
        failureMessage: 'delete_failed',
      },
    );

    if (!succeeded) return;
    // 如果正在编辑被删除的文章，重置表单
    if (form.id === postId) resetForm();
    await loadPosts();
  }

  async function applyFilter(nextFilter) {
    setFilter(nextFilter);
    // 筛选条件变化时重置到第一页
    setPage(1);
    await loadPosts(nextFilter, 1);
  }

  function handleFieldChange(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleToggleTag(tagId, checked) {
    setForm((prev) => ({ ...prev, tag_ids: toggleTagIds(prev.tag_ids, tagId, checked) }));
  }

  return {
    posts,
    taxonomy,
    error,
    message,
    filter,
    previewMode,
    form,
    selectedTagIds,
    page,
    totalPages,
    setPage,
    setPreviewMode,
    resetForm,
    fillForEdit,
    submitForm,
    importMarkdown,
    exportMarkdown,
    uploadImage,
    publishPost,
    unpublishPost,
    deletePost,
    applyFilter,
    handleFieldChange,
    handleToggleTag,
  };
}
