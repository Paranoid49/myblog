import test from 'node:test';
import assert from 'node:assert/strict';

import {
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
} from './useAdminPostsState.helpers.js';

test('toQuery 只序列化已选筛选项', () => {
  assert.equal(toQuery({ category_id: '', tag_id: '' }), '');
  assert.equal(toQuery({ category_id: 3, tag_id: '' }), '?category_id=3');
  assert.equal(toQuery({ category_id: '3', tag_id: 9 }), '?category_id=3&tag_id=9');
});

test('toPostPayload 规范化表单提交字段', () => {
  assert.deepEqual(
    toPostPayload({
      title: '标题',
      summary: '',
      content: '正文',
      category_id: '12',
      tag_ids: ['1', 2, '3'],
    }),
    {
      title: '标题',
      summary: null,
      content: '正文',
      category_id: 12,
      tag_ids: [1, 2, 3],
    },
  );
});

test('toEditForm 回填编辑表单默认值', () => {
  assert.deepEqual(
    toEditForm({
      id: 7,
      title: null,
      summary: null,
      content: null,
      category_id: 5,
      tag_ids: ['2', 3],
    }),
    {
      id: 7,
      title: '',
      summary: '',
      content: '',
      category_id: '5',
      tag_ids: [2, 3],
    },
  );
});

test('轻量请求与提示 helper 保持既有行为', () => {
  assert.deepEqual(buildJsonRequestOptions({ a: 1 }), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ a: 1 }),
  });
  assert.equal(appendMarkdownImage('正文', '/uploads/a.png'), '正文\n\n![image](/uploads/a.png)\n');
  assert.deepEqual(buildMarkdownImportPayload('# hi'), { markdown: '# hi', category_id: null, tag_ids: [] });
  assert.equal(buildPostRequestPath(null), '/admin/posts');
  assert.equal(buildPostRequestPath(9), '/admin/posts/9');
  assert.equal(getPostSuccessMessage(null), '文章已创建');
  assert.equal(getPostSuccessMessage(9), '文章已更新');
});

test('toggleTagIds 仅做稳定标签切换', () => {
  assert.deepEqual(toggleTagIds([1, '2'], 3, true), [1, 2, 3]);
  assert.deepEqual(toggleTagIds([1, 2, 3], '2', false), [1, 3]);
  assert.deepEqual(toggleTagIds([1, 2], '2', true), [1, 2]);
});

test('runWithFeedback 成功时清空错误并写入成功消息', async () => {
  const errors = [];
  const messages = [];
  const setError = (value) => errors.push(value);
  const setMessage = (value) => messages.push(value);

  const succeeded = await runWithFeedback(
    async () => {},
    {
      setError,
      setMessage,
      successMessage: 'ok',
      failureMessage: 'failed',
    },
  );

  assert.equal(succeeded, true);
  assert.deepEqual(errors, ['']);
  assert.deepEqual(messages, ['', 'ok']);
});

test('runWithFeedback 失败时写入错误并返回 false', async () => {
  const errors = [];
  const messages = [];
  const setError = (value) => errors.push(value);
  const setMessage = (value) => messages.push(value);

  const succeeded = await runWithFeedback(
    async () => {
      throw new Error('boom');
    },
    {
      setError,
      setMessage,
      successMessage: 'ok',
      failureMessage: 'failed',
    },
  );

  assert.equal(succeeded, false);
  assert.deepEqual(errors, ['', 'boom']);
  assert.deepEqual(messages, ['']);
});
