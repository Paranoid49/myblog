import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// mock apiRequest
vi.mock('../../../shared/api/client', () => ({
    apiRequest: vi.fn(),
}));

// mock PublicLayout，避免引入 ThemeProvider 等复杂依赖
vi.mock('../../../shared/layout/PublicLayout', () => ({
    default: ({ children }) => <div data-testid="public-layout">{children}</div>,
}));

// mock formatDate 工具函数
vi.mock('../../../shared/utils/format', () => ({
    formatDate: vi.fn((v) => v || '未发布'),
}));

import { apiRequest } from '../../../shared/api/client';
import PublicHomePage from '../PublicHomePage';

describe('PublicHomePage', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('加载中显示骨架屏', () => {
        // mock 两个 API 调用都不 resolve，保持 loading 状态
        apiRequest.mockReturnValue(new Promise(() => {}));
        const { container } = render(
            <MemoryRouter>
                <PublicHomePage />
            </MemoryRouter>
        );
        // PostListSkeleton 内部渲染带有 skeleton-card 类名的元素
        expect(container.querySelector('.skeleton-card')).toBeTruthy();
    });

    it('无文章时显示空状态提示', async () => {
        // apiRequest('/posts') 返回空数组，apiRequest('/author') 返回作者信息
        apiRequest.mockImplementation((path) => {
            if (path.startsWith('/posts')) return Promise.resolve({ items: [], total: 0, page: 1, page_size: 20, total_pages: 0 });
            if (path === '/author') return Promise.resolve({ blog_title: '测试博客' });
            return Promise.resolve(null);
        });

        render(
            <MemoryRouter>
                <PublicHomePage />
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(screen.getByText(/暂无已发布文章/)).toBeTruthy();
        });
    });

    it('有文章时渲染文章列表', async () => {
        const mockPosts = [
            {
                id: 1,
                title: '测试文章标题',
                slug: 'test-post',
                summary: '这是一篇测试文章',
                published_at: '2025-01-01T00:00:00Z',
                category_name: '技术',
                category_slug: 'tech',
                tags: [{ id: 1, name: 'React', slug: 'react' }],
            },
        ];

        apiRequest.mockImplementation((path) => {
            if (path.startsWith('/posts')) return Promise.resolve({ items: mockPosts, total: 1, page: 1, page_size: 20, total_pages: 1 });
            if (path === '/author') return Promise.resolve({ blog_title: '测试博客' });
            return Promise.resolve(null);
        });

        render(
            <MemoryRouter>
                <PublicHomePage />
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(screen.getByText('测试文章标题')).toBeTruthy();
        });
    });
});
