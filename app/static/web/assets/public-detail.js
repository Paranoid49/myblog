import { apiRequest } from './api.js';

const titleEl = document.getElementById('detail-title');
const summaryEl = document.getElementById('detail-summary');
const contentEl = document.getElementById('detail-content');
const errorBox = document.getElementById('detail-error');

function getSlug() {
  const params = new URLSearchParams(window.location.search);
  return params.get('slug') || '';
}

async function loadDetail() {
  const slug = getSlug();
  if (!slug) {
    errorBox.textContent = 'missing_slug';
    return;
  }

  const post = await apiRequest(`/posts/${encodeURIComponent(slug)}`);
  titleEl.textContent = post.title || '';
  summaryEl.textContent = post.summary || '';
  contentEl.textContent = post.content || '';
}

loadDetail().catch((error) => {
  errorBox.textContent = error.message;
});
