/**
 * 将 ISO 日期字符串格式化为中文日期显示。
 * @param {string|null} value - ISO 日期字符串
 * @returns {string} 格式化后的日期或"未发布"
 */
export function formatDate(value) {
  if (!value) return '未发布';
  const date = new Date(value);
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
}
