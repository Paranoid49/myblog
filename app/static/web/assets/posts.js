import { apiRequest } from './api.js';

const postsList = document.getElementById('posts-list');
const createForm = document.getElementById('create-post-form');
const errorBox = document.getElementById('posts-error');
const logoutBtn = document.getElementById('logout-btn');

function renderPosts(posts) {
  postsList.innerHTML = '';

  if (!posts.length) {
    postsList.innerHTML = '<li>暂无文章</li>';
    return;
  }

  for (const post of posts) {
    const li = document.createElement('li');
    const status = post.published_at ? '已发布' : '草稿';
    li.innerHTML = `
      <strong>${post.title}</strong>
      <span class="meta">(${post.slug})</span>
      <span class="status">${status}</span>
      <button data-action="publish" data-id="${post.id}">发布</button>
      <button data-action="unpublish" data-id="${post.id}">转草稿</button>
    `;
    postsList.appendChild(li);
  }
}

async function loadPosts() {
  const posts = await apiRequest('/admin/posts');
  renderPosts(posts);
}

async function createPost(event) {
  event.preventDefault();
  errorBox.textContent = '';

  const formData = new FormData(createForm);
  const payload = {
    title: formData.get('title')?.toString() || '',
    summary: formData.get('summary')?.toString() || '',
    content: formData.get('content')?.toString() || '',
    category_id: null,
    tag_ids: [],
  };

  try {
    await apiRequest('/admin/posts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    createForm.reset();
    await loadPosts();
  } catch (error) {
    errorBox.textContent = error.message;
  }
}

async function togglePublish(event) {
  const button = event.target;
  if (!(button instanceof HTMLButtonElement)) return;

  const action = button.dataset.action;
  const id = button.dataset.id;
  if (!action || !id) return;

  errorBox.textContent = '';

  try {
    await apiRequest(`/admin/posts/${id}/${action}`, { method: 'POST' });
    await loadPosts();
  } catch (error) {
    errorBox.textContent = error.message;
  }
}

async function logout() {
  await apiRequest('/auth/logout', { method: 'POST' });
  window.location.href = '/static/web/admin/login.html';
}

if (createForm) createForm.addEventListener('submit', createPost);
if (postsList) postsList.addEventListener('click', togglePublish);
if (logoutBtn) logoutBtn.addEventListener('click', logout);

loadPosts().catch((error) => {
  errorBox.textContent = error.message;
});
