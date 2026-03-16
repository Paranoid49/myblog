/**
 * 通用分页组件
 */
export default function Pagination({ page, totalPages, onPageChange }) {
    if (totalPages <= 1) return null;

    return (
        <nav className="pagination">
            <button
                className="ghost-button"
                disabled={page <= 1}
                onClick={() => onPageChange(page - 1)}
            >
                ← 上一页
            </button>
            <span className="pagination-info">
                {page} / {totalPages}
            </span>
            <button
                className="ghost-button"
                disabled={page >= totalPages}
                onClick={() => onPageChange(page + 1)}
            >
                下一页 →
            </button>
        </nav>
    );
}
