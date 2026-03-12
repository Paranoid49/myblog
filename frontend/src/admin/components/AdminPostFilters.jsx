export default function AdminPostFilters({ filter, taxonomy, onApplyFilter }) {
  return (
    <section className="panel-card">
      <div className="section-head">
        <h3>筛选</h3>
      </div>
      <div className="filter-row">
        <select value={filter.category_id} onChange={(e) => onApplyFilter({ ...filter, category_id: e.target.value })}>
          <option value="">全部分类</option>
          {taxonomy.categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={filter.tag_id} onChange={(e) => onApplyFilter({ ...filter, tag_id: e.target.value })}>
          <option value="">全部标签</option>
          {taxonomy.tags.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
      </div>
    </section>
  );
}
