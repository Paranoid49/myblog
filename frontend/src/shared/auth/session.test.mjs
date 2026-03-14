import test from 'node:test';
import assert from 'node:assert/strict';

import { getAuthGuardRedirect } from './navigation.js';
import {
  clearStoredUserSnapshot,
  getAdminEntryPath,
  getLoginNavigationState,
  getLoginRedirectPath,
  getStoredUserSnapshot,
  hasStoredUserSnapshot,
  loginWithUserSnapshot,
  logoutWithUserSnapshot,
  redirectToLoginAfterUnauthorized,
  setStoredUserSnapshot,
} from './session.js';

function createStorageMock() {
  const store = new Map();

  return {
    getItem(key) {
      return store.has(key) ? store.get(key) : null;
    },
    setItem(key, value) {
      store.set(key, value);
    },
    removeItem(key) {
      store.delete(key);
    },
  };
}

function installWindowMock(pathname = '/') {
  const storage = createStorageMock();
  const location = {
    pathname,
    assignedTo: null,
    assign(target) {
      this.assignedTo = target;
    },
  };

  globalThis.window = {
    localStorage: storage,
    location,
  };

  return { storage, location };
}

test('未登录访问后台路由时生成登录跳转信息', () => {
  const redirect = getAuthGuardRedirect('/admin/posts', false);

  assert.deepEqual(redirect, {
    to: '/admin/login',
    state: { from: '/admin/posts' },
  });
});

test('已登录访问后台路由时不再跳转登录页', () => {
  assert.equal(getAuthGuardRedirect('/admin/posts', true), null);
});

test('登录后按 redirectTo 回跳并写入快照', () => {
  installWindowMock('/admin/login');
  const calls = [];

  loginWithUserSnapshot({
    navigate: (to, options) => calls.push({ to, options }),
    user: { username: 'admin' },
    redirectTo: '/admin/posts',
  });

  assert.equal(hasStoredUserSnapshot(), true);
  assert.deepEqual(getStoredUserSnapshot(), { username: 'admin' });
  assert.deepEqual(calls, [{ to: '/admin/posts', options: { replace: true } }]);
});

test('退出登录清理快照并跳回登录页', () => {
  installWindowMock('/admin');
  setStoredUserSnapshot({ username: 'admin' });
  const calls = [];

  logoutWithUserSnapshot({
    navigate: (to, options) => calls.push({ to, options }),
  });

  assert.equal(hasStoredUserSnapshot(), false);
  assert.deepEqual(calls, [{ to: '/admin/login', options: { replace: true } }]);
});

test('收到未授权响应后清理快照并跳到登录页', () => {
  const { location } = installWindowMock('/admin/posts');
  setStoredUserSnapshot({ username: 'admin' });

  redirectToLoginAfterUnauthorized();

  assert.equal(hasStoredUserSnapshot(), false);
  assert.equal(location.assignedTo, '/admin/login');
});

test('已在登录页时未授权处理不重复跳转', () => {
  const { location } = installWindowMock('/admin/login');

  redirectToLoginAfterUnauthorized();

  assert.equal(location.assignedTo, null);
});

test('后台入口根据登录状态切换到登录页或后台首页', () => {
  installWindowMock('/');
  assert.equal(getAdminEntryPath(), '/admin/login');

  setStoredUserSnapshot({ username: 'admin' });
  assert.equal(getAdminEntryPath(), '/admin');
});

test('登录跳转状态在缺省时回退到后台首页', () => {
  assert.equal(getLoginRedirectPath(undefined), '/admin');
  assert.equal(getLoginRedirectPath({ from: '/admin/posts' }), '/admin/posts');
  assert.deepEqual(getLoginNavigationState('/admin/posts'), { from: '/admin/posts' });
  assert.equal(getLoginNavigationState('')?.from, undefined);
});

test('本地存储损坏时按未登录处理', () => {
  const { storage } = installWindowMock('/');
  storage.setItem('myblog_user', '{bad json');

  assert.equal(getStoredUserSnapshot(), null);
  assert.equal(hasStoredUserSnapshot(), false);
  clearStoredUserSnapshot();
  assert.equal(getStoredUserSnapshot(), null);
});
