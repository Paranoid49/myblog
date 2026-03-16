import { describe, it, expect } from 'vitest';

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

describe('useAdminPostsState helpers', () => {
  it('toQuery 只序列化已选筛选项', () => {
    // toQuery 默认携带 page=1&page_size=20 分页参数
    expect(toQuery({ category_id: '', tag_id: '' })).toBe('?page=1&page_size=20');
    expect(toQuery({ category_id: 3, tag_id: '' })).toBe('?page=1&page_size=20&category_id=3');
    expect(toQuery({ category_id: '3', tag_id: 9 })).toBe('?page=1&page_size=20&category_id=3&tag_id=9');
    // 自定义分页参数
    expect(toQuery({ category_id: '', tag_id: '' }, 2, 10)).toBe('?page=2&page_size=10');
  });

  it('toPostPayload 规范化表单提交字段', () => {
    expect(
      toPostPayload({
        title: '标题',
        summary: '',
        content: '正文',
        category_id: '12',
        tag_ids: ['1', 2, '3'],
      }),
    ).toEqual({
      title: '标题',
      summary: null,
      content: '正文',
      category_id: 12,
      tag_ids: [1, 2, 3],
    });
  });

  it('toEditForm 回填编辑表单默认值', () => {
    expect(
      toEditForm({
        id: 7,
        title: null,
        summary: null,
        content: null,
        category_id: 5,
        tag_ids: ['2', 3],
      }),
    ).toEqual({
      id: 7,
      title: '',
      summary: '',
      content: '',
      category_id: '5',
      tag_ids: [2, 3],
    });
  });

  it('轻量请求与提示 helper 保持既有行为', () => {
    expect(buildJsonRequestOptions({ a: 1 })).toEqual({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ a: 1 }),
    });
    expect(appendMarkdownImage('正文', '/uploads/a.png')).toBe('正文\n\n![image](/uploads/a.png)\n');
    expect(buildMarkdownImportPayload('# hi')).toEqual({ markdown: '# hi', category_id: null, tag_ids: [] });
    expect(buildPostRequestPath(null)).toBe('/admin/posts');
    expect(buildPostRequestPath(9)).toBe('/admin/posts/9');
    expect(getPostSuccessMessage(null)).toBe('文章已创建');
    expect(getPostSuccessMessage(9)).toBe('文章已更新');
  });

  it('toggleTagIds 仅做稳定标签切换', () => {
    expect(toggleTagIds([1, '2'], 3, true)).toEqual([1, 2, 3]);
    expect(toggleTagIds([1, 2, 3], '2', false)).toEqual([1, 3]);
    expect(toggleTagIds([1, 2], '2', true)).toEqual([1, 2]);
  });

  it('runWithFeedback 成功时清空错误并写入成功消息', async () => {
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

    expect(succeeded).toBe(true);
    expect(errors).toEqual(['']);
    expect(messages).toEqual(['', 'ok']);
  });

  it('runWithFeedback 失败时写入错误并返回 false', async () => {
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

    expect(succeeded).toBe(false);
    expect(errors).toEqual(['', 'boom']);
    expect(messages).toEqual(['']);
  });
});
