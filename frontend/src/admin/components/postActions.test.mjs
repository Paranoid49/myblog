import test from 'node:test';
import assert from 'node:assert/strict';

import { getPostPublishAction } from './postActions.js';

test('草稿文章只显示发布动作', () => {
  assert.deepEqual(getPostPublishAction({ id: 1, published_at: null }), {
    text: '发布',
    variant: 'primary-button',
    handlerName: 'onPublish',
  });
});

test('已发布文章只显示转草稿动作', () => {
  assert.deepEqual(getPostPublishAction({ id: 1, published_at: '2026-03-14T12:00:00Z' }), {
    text: '转草稿',
    variant: 'ghost-button',
    handlerName: 'onUnpublish',
  });
});
