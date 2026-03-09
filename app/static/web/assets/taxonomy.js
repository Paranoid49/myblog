import { apiRequest } from './api.js';

const categoriesList = document.getElementById('categories-list');
const tagsList = document.getElementById('tags-list');
const categoryForm = document.getElementById('create-category-form');
const tagForm = document.getElementById('create-tag-form');
const errorBox = document.getElementById('taxonomy-error');
const logoutBtn = document.getElementById('logout-btn');

function renderSimpleList(container, items) {
  container.innerHTML = '';
  if (!items.length) {
    container.innerHTML = '<li>暂无数据</li>';
    return;
  }

  for (const item of items) {
    const li = document.createElement('li');
    li.textContent = `${item.name} (${item.slug})`;
    container.appendChild(li);
  }
}

async function loadTaxonomy() {
  const data = await apiRequest('/taxonomy');
  renderSimpleList(categoriesList, data.categories || []);
  renderSimpleList(tagsList, data.tags || []);
}

async function createCategory(event) {
  event.preventDefault();
  errorBox.textContent = '';

  const formData = new FormData(categoryForm);
  const payload = { name: formData.get('name')?.toString() || '' };

  try {
    await apiRequest('/admin/categories', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    categoryForm.reset();
    await loadTaxonomy();
  } catch (error) {
    errorBox.textContent = error.message;
  }
}

async function createTag(event) {
  event.preventDefault();
  errorBox.textContent = '';

  const formData = new FormData(tagForm);
  const payload = { name: formData.get('name')?.toString() || '' };

  try {
    await apiRequest('/admin/tags', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    tagForm.reset();
    await loadTaxonomy();
  } catch (error) {
    errorBox.textContent = error.message;
  }
}

async function logout() {
  await apiRequest('/auth/logout', { method: 'POST' });
  window.location.href = '/static/web/admin/login.html';
}

if (categoryForm) categoryForm.addEventListener('submit', createCategory);
if (tagForm) tagForm.addEventListener('submit', createTag);
if (logoutBtn) logoutBtn.addEventListener('click', logout);

loadTaxonomy().catch((error) => {
  errorBox.textContent = error.message;
});
