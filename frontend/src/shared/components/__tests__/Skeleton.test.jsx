import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import {
    SkeletonLine,
    PostCardSkeleton,
    PostListSkeleton,
    PostDetailSkeleton,
} from '../Skeleton';

describe('Skeleton 组件', () => {
    describe('SkeletonLine', () => {
        it('渲染带 skeleton-line 类名的元素', () => {
            const { container } = render(<SkeletonLine />);
            expect(container.querySelector('.skeleton-line')).toBeTruthy();
        });

        it('默认宽度为 100%', () => {
            const { container } = render(<SkeletonLine />);
            const el = container.querySelector('.skeleton-line');
            expect(el.style.width).toBe('100%');
        });

        it('支持自定义宽度和高度', () => {
            const { container } = render(<SkeletonLine width="50%" height="2rem" />);
            const el = container.querySelector('.skeleton-line');
            expect(el.style.width).toBe('50%');
            expect(el.style.height).toBe('2rem');
        });
    });

    describe('PostCardSkeleton', () => {
        it('渲染骨架卡片', () => {
            const { container } = render(<PostCardSkeleton />);
            expect(container.querySelector('.skeleton-card')).toBeTruthy();
        });

        it('内部包含多条 skeleton-line', () => {
            const { container } = render(<PostCardSkeleton />);
            const lines = container.querySelectorAll('.skeleton-line');
            expect(lines.length).toBeGreaterThan(0);
        });
    });

    describe('PostListSkeleton', () => {
        it('默认渲染 3 个骨架卡片', () => {
            const { container } = render(<PostListSkeleton />);
            const cards = container.querySelectorAll('.skeleton-card');
            expect(cards.length).toBe(3);
        });

        it('支持自定义数量', () => {
            const { container } = render(<PostListSkeleton count={5} />);
            const cards = container.querySelectorAll('.skeleton-card');
            expect(cards.length).toBe(5);
        });

        it('count 为 1 时只渲染一个卡片', () => {
            const { container } = render(<PostListSkeleton count={1} />);
            const cards = container.querySelectorAll('.skeleton-card');
            expect(cards.length).toBe(1);
        });
    });

    describe('PostDetailSkeleton', () => {
        it('渲染骨架详情', () => {
            const { container } = render(<PostDetailSkeleton />);
            expect(container.querySelector('.skeleton-card')).toBeTruthy();
        });

        it('使用 post-detail-card 类名区分列表卡片', () => {
            const { container } = render(<PostDetailSkeleton />);
            expect(container.querySelector('.post-detail-card')).toBeTruthy();
        });

        it('内部包含多条 skeleton-line', () => {
            const { container } = render(<PostDetailSkeleton />);
            const lines = container.querySelectorAll('.skeleton-line');
            expect(lines.length).toBeGreaterThan(0);
        });
    });
});
