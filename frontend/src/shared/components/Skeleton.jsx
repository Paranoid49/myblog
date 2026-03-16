/**
 * 骨架屏组件，用于页面加载时的视觉占位
 */
export function SkeletonLine({ width = '100%', height = '1rem' }) {
    return <div className="skeleton-line" style={{ width, height }} />;
}

export function PostCardSkeleton() {
    return (
        <article className="post-card skeleton-card">
            <div className="post-meta-row">
                <SkeletonLine width="6rem" />
                <SkeletonLine width="4rem" />
            </div>
            <SkeletonLine width="70%" height="1.5rem" />
            <SkeletonLine width="90%" />
            <div className="post-tag-list">
                <SkeletonLine width="3rem" height="1.25rem" />
                <SkeletonLine width="4rem" height="1.25rem" />
            </div>
        </article>
    );
}

export function PostListSkeleton({ count = 3 }) {
    return (
        <section className="post-list-grid">
            {Array.from({ length: count }, (_, i) => (
                <PostCardSkeleton key={i} />
            ))}
        </section>
    );
}

export function PostDetailSkeleton() {
    return (
        <article className="post-detail-card skeleton-card">
            <SkeletonLine width="60%" height="2rem" />
            <div className="post-meta-detail">
                <SkeletonLine width="8rem" />
                <SkeletonLine width="5rem" />
            </div>
            <SkeletonLine width="100%" />
            <SkeletonLine width="95%" />
            <SkeletonLine width="80%" />
            <SkeletonLine width="90%" />
            <SkeletonLine width="70%" />
        </article>
    );
}
