export const EMPTY_FILTER = { category_id: '', tag_id: '' };
export const EMPTY_FORM = { id: null, title: '', summary: '', content: '', category_id: '', tag_ids: [] };

export function toQuery(filter) {
  const url = new URLSearchParams();
  if (filter.category_id) url.set('category_id', String(filter.category_id));
  if (filter.tag_id) url.set('tag_id', String(filter.tag_id));
  const query = url.toString();
  return query ? `?${query}` : '';
}

export function toPostPayload(form) {
  return {
    title: form.title,
    summary: form.summary || null,
    content: form.content,
    category_id: form.category_id ? Number(form.category_id) : null,
    tag_ids: form.tag_ids.map((id) => Number(id)),
  };
}

export function toEditForm(post) {
  return {
    id: post.id,
    title: post.title || '',
    summary: post.summary || '',
    content: post.content || '',
    category_id: post.category_id ? String(post.category_id) : '',
    tag_ids: (post.tag_ids || []).map((id) => Number(id)),
  };
}

export function buildJsonRequestOptions(payload) {
  return {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  };
}

export function appendMarkdownImage(content, imageUrl) {
  return `${content}\n\n![image](${imageUrl})\n`;
}

export function getPostSuccessMessage(formId) {
  return formId ? '文章已更新' : '文章已创建';
}

export function buildMarkdownImportPayload(markdown) {
  return { markdown, category_id: null, tag_ids: [] };
}

export function buildPostRequestPath(formId) {
  return formId ? `/admin/posts/${formId}` : '/admin/posts';
}

export function resetFeedback(setError, setMessage) {
  setError('');
  setMessage('');
}

export function setFailure(setError, error, fallback) {
  setError(error.message || fallback);
}

export async function runWithFeedback(action, { setError, setMessage, successMessage, failureMessage }) {
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

export function toggleTagIds(tagIds, tagId, checked) {
  const next = new Set(tagIds.map((id) => Number(id)));
  if (checked) next.add(Number(tagId));
  else next.delete(Number(tagId));
  return [...next];
}
