import { apiRequest } from './api.js';

const postsEl = document.getElementById('public-posts');
const errorBox = document.getElementById('public-error');

function renderPosts(posts) {
  postsEl.innerHTML = '';
  if (!posts.length) {
    postsEl.innerHTML = '<li>暂无已发布文章</li>';
    return;
  }

  for (const post of posts) {
    const li = document.createElement('li');
    li.innerHTML = `<a href="/static/web/public/post.html?slug=${encodeURIComponent(post.slug)}">${post.title}</a>`;
    postsEl.appendChild(li);
  }
}

async function loadPosts() {
  const posts = await apiRequest('/posts');
  renderPosts(posts);
}

loadPosts().catch((error) => {
  errorBox.textContent = error.message;
});
