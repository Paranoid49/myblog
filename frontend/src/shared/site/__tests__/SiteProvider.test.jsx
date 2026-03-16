import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

vi.mock('../../api/client', () => ({
    apiRequest: vi.fn(),
}));

import { apiRequest } from '../../api/client';
import { SiteProvider, useSite } from '../SiteProvider';

// 消费者组件，用于读取 SiteProvider 提供的上下文值
function SiteConsumer() {
    const { blogTitle } = useSite();
    return <span data-testid="blog-title">{blogTitle}</span>;
}

describe('SiteProvider', () => {
    beforeEach(() => { vi.clearAllMocks(); });

    it('默认 blogTitle 为 myblog', () => {
        // API 不返回，保持 pending 状态
        apiRequest.mockReturnValue(new Promise(() => {}));
        render(<SiteProvider><SiteConsumer /></SiteProvider>);
        expect(screen.getByTestId('blog-title').textContent).toBe('myblog');
    });

    it('从 API 获取 blogTitle 后更新', async () => {
        apiRequest.mockResolvedValue({ blog_title: '测试博客' });
        render(<SiteProvider><SiteConsumer /></SiteProvider>);
        await waitFor(() => {
            expect(screen.getByTestId('blog-title').textContent).toBe('测试博客');
        });
    });

    it('API 失败时保持默认值', async () => {
        apiRequest.mockRejectedValue(new Error('fail'));
        render(<SiteProvider><SiteConsumer /></SiteProvider>);
        // 等待 useEffect 中的 catch 执行完毕
        await waitFor(() => {
            expect(apiRequest).toHaveBeenCalled();
        });
        expect(screen.getByTestId('blog-title').textContent).toBe('myblog');
    });
});
