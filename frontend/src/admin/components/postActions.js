export function getPostPublishAction(post) {
  if (post?.published_at) {
    return {
      text: '转草稿',
      variant: 'ghost-button',
      handlerName: 'onUnpublish',
    };
  }

  return {
    text: '发布',
    variant: 'primary-button',
    handlerName: 'onPublish',
  };
}
