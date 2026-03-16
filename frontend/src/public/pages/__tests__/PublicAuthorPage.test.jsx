import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// 只 mock apiRequest，不 mock Layout
vi.mock('../../../shared/api/client', () => ({
    apiRequest: vi.fn(),
}));

// mock SiteProvider 的 useSite（因为 PublicLayout 依赖它）
vi.mock('../../../shared/site/SiteProvider', () => ({
    useSite: () => ({ blogTitle: '测试博客' }),
}));

// mock ThemeProvider（PublicLayout 依赖）
vi.mock('../../../shared/theme/ThemeProvider', () => ({
    useTheme: () => ({ theme: 'light', toggleTheme: vi.fn() }),
}));

import { apiRequest } from '../../../shared/api/client';
import PublicAuthorPage from '../PublicAuthorPage';

describe('PublicAuthorPage（真实渲染）', () => {
    beforeEach(() => { vi.clearAllMocks(); });

    it('加载作者数据后显示作者名', async () => {
        apiRequest.mockResolvedValue({
            blog_title: '测试博客',
            name: '张三',
            bio: '全栈开发者',
            email: 'test@example.com',
            avatar: '',
            link: '',
        });

        render(
            <MemoryRouter>
                <PublicAuthorPage />
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(screen.getByText('张三')).toBeTruthy();
        });
    });

    it('显示作者简介', async () => {
        apiRequest.mockResolvedValue({
            blog_title: '测试博客',
            name: '张三',
            bio: '全栈开发者',
            email: '',
            avatar: '',
            link: '',
        });

        render(
            <MemoryRouter>
                <PublicAuthorPage />
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(screen.getByText('全栈开发者')).toBeTruthy();
        });
    });
});
