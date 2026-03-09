import { apiRequest } from './api.js';

const form = document.getElementById('login-form');
const errorBox = document.getElementById('login-error');

if (form) {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorBox.textContent = '';

    const formData = new FormData(form);

    try {
      await apiRequest('/auth/login', {
        method: 'POST',
        body: formData,
      });
      window.location.href = '/static/web/admin/posts.html';
    } catch (error) {
      errorBox.textContent = error.message;
    }
  });
}
