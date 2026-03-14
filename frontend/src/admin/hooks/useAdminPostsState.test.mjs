import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const HOOK_FILE = '/mnt/d/projects/python/myblog/frontend/src/admin/hooks/useAdminPostsState.js';
const HELPERS_URL = pathToFileURL('/mnt/d/projects/python/myblog/frontend/src/admin/hooks/useAdminPostsState.helpers.js').href;

function createDataModule(source) {
  return `data:text/javascript;charset=utf-8,${encodeURIComponent(source)}`;
}

function areHookDepsEqual(prevDeps, nextDeps) {
  if (!prevDeps || !nextDeps || prevDeps.length !== nextDeps.length) {
    return false;
  }

  return prevDeps.every((value, index) => Object.is(value, nextDeps[index]));
}

async function flushMicrotasks() {
  await Promise.resolve();
  await Promise.resolve();
  await Promise.resolve();
}

async function createHookHarness(apiRequest) {
  const stateSlots = [];
  const memoSlots = [];
  const effectSlots = [];
  let renderCursor = 0;
  let pendingEffects = [];
  let result;

  // 这里只模拟当前 hook 用到的最小 React 能力，目的是验证“状态编排 + API 调用顺序”。

  const reactKey = `__hook_test_react_${Math.random().toString(36).slice(2)}`;
  const apiKey = `__hook_test_api_${Math.random().toString(36).slice(2)}`;

  globalThis[reactKey] = {
    useState(initialValue) {
      const slot = renderCursor;
      renderCursor += 1;
      if (!(slot in stateSlots)) {
        stateSlots[slot] = typeof initialValue === 'function' ? initialValue() : initialValue;
      }
      return [
        stateSlots[slot],
        (nextValue) => {
          stateSlots[slot] = typeof nextValue === 'function' ? nextValue(stateSlots[slot]) : nextValue;
        },
      ];
    },
    useMemo(factory, deps) {
      const slot = renderCursor;
      renderCursor += 1;
      const previous = memoSlots[slot];
      if (!previous || !areHookDepsEqual(previous.deps, deps)) {
        memoSlots[slot] = { value: factory(), deps };
      }
      return memoSlots[slot].value;
    },
    useEffect(effect, deps) {
      const slot = renderCursor;
      renderCursor += 1;
      const previous = effectSlots[slot];
      if (!previous || !areHookDepsEqual(previous.deps, deps)) {
        effectSlots[slot] = { deps };
        pendingEffects.push(effect);
      }
    },
  };

  globalThis[apiKey] = apiRequest;

  const source = await readFile(HOOK_FILE, 'utf8');
  const rewrittenSource = source
    .replace(`from 'react';`, `from '${createDataModule(`export const useState = globalThis.${reactKey}.useState; export const useMemo = globalThis.${reactKey}.useMemo; export const useEffect = globalThis.${reactKey}.useEffect;`)}';`)
    .replace(`from '../../shared/api/client';`, `from '${createDataModule(`export const apiRequest = (...args) => globalThis.${apiKey}(...args);`)}';`)
    .replace(`from './useAdminPostsState.helpers';`, `from '${HELPERS_URL}';`);

  const hookModule = await import(createDataModule(rewrittenSource));

  async function render() {
    renderCursor = 0;
    pendingEffects = [];
    result = hookModule.default();
    const effectsToRun = pendingEffects;
    pendingEffects = [];
    for (const effect of effectsToRun) {
      await effect();
    }
    await flushMicrotasks();
    return result;
  }

  async function renderSettled() {
    // 第一次 render 触发 useEffect，第二次 render 读取 effect 更新后的最新状态。
    await render();
    return render();
  }

  function cleanup() {
    delete globalThis[reactKey];
    delete globalThis[apiKey];
  }

  return {
    render,
    renderSettled,
    cleanup,
    get result() {
      return result;
    },
  };
}

test('publishPost 成功后刷新文章列表', async () => {
  const calls = [];
  let postsLoadCount = 0;
  const harness = await createHookHarness(async (path, options) => {
    calls.push([path, options]);
    if (path === '/taxonomy') {
      return { categories: [], tags: [] };
    }
    if (path === '/admin/posts' && !options) {
      postsLoadCount += 1;
      return postsLoadCount === 1 ? [{ id: 1, title: 'draft' }] : [{ id: 1, title: 'published' }];
    }
    if (path === '/admin/posts/1/publish') {
      return { ok: true };
    }
    throw new Error(`unexpected_request:${path}`);
  });

  try {
    await harness.renderSettled();

    await harness.result.publishPost(1);
    await harness.render();

    assert.deepEqual(harness.result.posts, [{ id: 1, title: 'published' }]);
    assert.equal(harness.result.message, '文章已发布');
    assert.deepEqual(calls, [
      ['/taxonomy', undefined],
      ['/admin/posts', undefined],
      ['/admin/posts/1/publish', { method: 'POST' }],
      ['/admin/posts', undefined],
    ]);
  } finally {
    harness.cleanup();
  }
});

test('submitForm 成功后重置表单并重新加载文章列表', async () => {
  const calls = [];
  let postsLoadCount = 0;
  const harness = await createHookHarness(async (path, options) => {
    calls.push([path, options]);
    if (path === '/taxonomy') {
      return { categories: [{ id: 3, name: '后端' }], tags: [{ id: 8, name: 'FastAPI' }] };
    }
    if (path === '/admin/posts' && !options) {
      postsLoadCount += 1;
      return postsLoadCount === 1 ? [{ id: 1, title: 'old' }] : [{ id: 2, title: 'new' }];
    }
    if (path === '/admin/posts' && options?.method === 'POST') {
      return { id: 2 };
    }
    throw new Error(`unexpected_request:${path}`);
  });

  try {
    await harness.renderSettled();

    harness.result.handleFieldChange('title', '新文章');
    harness.result.handleFieldChange('summary', '摘要');
    harness.result.handleFieldChange('content', '正文');
    harness.result.handleFieldChange('category_id', '3');
    harness.result.handleToggleTag(8, true);
    await harness.render();

    await harness.result.submitForm({ preventDefault() {} });
    await harness.render();

    assert.deepEqual(harness.result.form, {
      id: null,
      title: '',
      summary: '',
      content: '',
      category_id: '',
      tag_ids: [],
    });
    assert.equal(harness.result.previewMode, 'edit');
    assert.equal(harness.result.message, '文章已创建');
    assert.deepEqual(harness.result.posts, [{ id: 2, title: 'new' }]);
    assert.deepEqual(calls, [
      ['/taxonomy', undefined],
      ['/admin/posts', undefined],
      [
        '/admin/posts',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: '新文章',
            summary: '摘要',
            content: '正文',
            category_id: 3,
            tag_ids: [8],
          }),
        },
      ],
      ['/admin/posts', undefined],
    ]);
  } finally {
    harness.cleanup();
  }
});
