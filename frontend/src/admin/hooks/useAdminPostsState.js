import { useEffect, useMemo, useState } from 'react';
import { apiRequest } from '../../shared/api/client';

const EMPTY_FILTER = { category_id: '', tag_id: '' };
const EMPTY_FORM = { id: null, title: '', summary: '', content: '', category_id: '', tag_ids: [] };

function toQuery(filter) {
  const url = new URLSearchParams();
  if (filter.category_id) url.set('category_id', String(filter.category_id));
  if (filter.tag_id) url.set('tag_id', String(filter.tag_id));
  const query = url.toString();
  return query ? `?${query}` : '';
}

function toPostPayload(form) {
  return {
    title: form.title,
    summary: form.summary || null,
    content: form.content,
    category_id: form.category_id ? Number(form.category_id) : null,
    tag_ids: form.tag_ids.map((id) => Number(id)),
  };
}

function toEditForm(post) {
  return {
    id: post.id,
    title: post.title || '',
    summary: post.summary || '',
    content: post.content || '',
    category_id: post.category_id ? String(post.category_id) : '',
    tag_ids: (post.tag_ids || []).map((id) => Number(id)),
  };
}

function buildJsonRequestOptions(payload) {
  return {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  };
}

function appendMarkdownImage(content, imageUrl) {
  return `${content}\n\n![image](${imageUrl})\n`;
}

function getPostSuccessMessage(formId) {
  return formId ? '文章已更新' : '文章已创建';
}


function buildMarkdownImportPayload(markdown) {
  return { markdown, category_id: null, tag_ids: [] };
}

function buildPostRequestPath(formId) {
  return formId ? `/admin/posts/${formId}` : '/admin/posts';
}

function resetFeedback(setError, setMessage) {
  setError('');
  setMessage('');
}

function setFailure(setError, error, fallback) {
  setError(error.message || fallback);
}

async function runWithFeedback(action, { setError, setMessage, successMessage, failureMessage }) {
  resetFeedback(setError, setMessage);

  try {
    await action();
    if (successMessage) {
      setMessage(successMessage);
    }
    return true;
  } catch (error) {
    setFailure(setError, error, failureMessage);
    return false;
  }
}

export default function useAdminPostsState() {
  // hook 只负责文章页状态编排与 API 交互，不承载跨页面状态管理或 CMS 平台化逻辑。
  const [posts, setPosts] = useState([]);
  const [taxonomy, setTaxonomy] = useState({ categories: [], tags: [] });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [filter, setFilter] = useState(EMPTY_FILTER);
  const [previewMode, setPreviewMode] = useState('edit');
  const [form, setForm] = useState(EMPTY_FORM);

  const selectedTagIds = useMemo(() => new Set(form.tag_ids.map((id) => Number(id))), [form.tag_ids]);

  async function loadTaxonomy() {
    const data = await apiRequest('/taxonomy');
    setTaxonomy({ categories: data.categories || [], tags: data.tags || [] });
  }

  async function loadPosts(nextFilter = filter) {
    const data = await apiRequest(`/admin/posts${toQuery(nextFilter)}`);
    setPosts(data || []);
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

  async function submitForm(event) {
    event.preventDefault();
    const payload = toPostPayload(form);
    const succeeded = await runWithFeedback(
      () => apiRequest(buildPostRequestPath(form.id), buildJsonRequestOptions(payload)),
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

  async function applyFilter(nextFilter) {
    setFilter(nextFilter);
    await loadPosts(nextFilter);
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

  return {
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
    publishPost,
    unpublishPost,
    applyFilter,
    handleFieldChange,
    handleToggleTag,
  };
}
