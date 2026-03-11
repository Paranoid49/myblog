import MarkdownRenderer from '../../shared/markdown/MarkdownRenderer';

export default function AdminPostEditor({
  form,
  taxonomy,
  previewMode,
  selectedTagIds,
  onPreviewModeChange,
  onReset,
  onFieldChange,
  onToggleTag,
  onSubmit,
  onImportMarkdown,
  onUploadImage,
}) {
  return (
    <section className="panel-card">
      <div className="section-head">
        <h3>{form.id ? '编辑文章' : '新建文章'}</h3>
        <div className="inline-actions">
          <button type="button" className={previewMode === 'edit' ? 'primary-button' : 'ghost-button'} onClick={() => onPreviewModeChange('edit')}>编辑</button>
          <button type="button" className={previewMode === 'preview' ? 'primary-button' : 'ghost-button'} onClick={() => onPreviewModeChange('preview')}>预览</button>
          <button type="button" className="ghost-button" onClick={onReset}>清空</button>
        </div>
      </div>

      <form onSubmit={onSubmit} className="editor-layout">
        <div className="editor-form-grid">
          <label>
            标题
            <input value={form.title} onChange={(e) => onFieldChange('title', e.target.value)} required />
          </label>

          <label>
            摘要
            <textarea value={form.summary} onChange={(e) => onFieldChange('summary', e.target.value)} rows={3} />
          </label>

          <label>
            分类
            <select value={form.category_id} onChange={(e) => onFieldChange('category_id', e.target.value)}>
              <option value="">默认分类</option>
              {taxonomy.categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </label>

          <fieldset>
            <legend>标签</legend>
            <div className="checkbox-wrap">
              {taxonomy.tags.map((t) => (
                <label key={t.id} className="checkbox-item">
                  <input type="checkbox" checked={selectedTagIds.has(Number(t.id))} onChange={(e) => onToggleTag(t.id, e.target.checked)} />
                  {t.name}
                </label>
              ))}
            </div>
          </fieldset>

          <label>
            Markdown 正文
            <textarea
              value={form.content}
              onChange={(e) => onFieldChange('content', e.target.value)}
              rows={16}
              required
              className="editor-textarea"
            />
          </label>

          <div className="toolbar-row">
            <label className="file-action">
              导入 Markdown
              <input type="file" accept=".md,text/markdown" onChange={onImportMarkdown} />
            </label>
            <label className="file-action">
              上传图片
              <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" onChange={onUploadImage} />
            </label>
            <button type="submit" className="primary-button">{form.id ? '保存修改' : '创建文章'}</button>
          </div>
        </div>

        <aside className="preview-panel">
          <h4>预览</h4>
          {previewMode === 'preview' ? <MarkdownRenderer content={form.content || '暂无内容'} /> : <p className="muted">切换到预览模式后查看渲染结果。</p>}
        </aside>
      </form>
    </section>
  );
}
