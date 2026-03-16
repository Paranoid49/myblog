import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// 只 mock apiRequest，不再 mock ThemeProvider 和 SiteProvider
vi.mock('../../../shared/api/client', () => ({
    apiRequest: vi.fn(),
}));

import { apiRequest } from '../../../shared/api/client';
import { ThemeProvider } from '../../../shared/theme/ThemeProvider';
import { SiteProvider } from '../../../shared/site/SiteProvider';
import PublicAuthorPage from '../PublicAuthorPage';

// 模拟 localStorage（ThemeProvider 读写 data-theme 需要）
const localStorageMock = (() => {
    let store = {};
    return {
        getItem: vi.fn((key) => store[key] || null),
        setItem: vi.fn((key, value) => { store[key] = value; }),
        removeItem: vi.fn((key) => { delete store[key]; }),
        clear: vi.fn(() => { store = {}; }),
    };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// 用真实 Provider 包裹被测组件
function renderWithProviders(ui) {
    return render(
        <MemoryRouter>
            <ThemeProvider>
                <SiteProvider>
                    {ui}
                </SiteProvider>
            </ThemeProvider>
        </MemoryRouter>
    );
}

describe('PublicAuthorPage（真实 Provider 渲染）', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorageMock.clear();
    });

    it('加载作者数据后显示作者名', async () => {
        apiRequest.mockResolvedValue({
            blog_title: '测试博客',
            name: '张三',
            bio: '全栈开发者',
            email: 'test@example.com',
            avatar: '',
            link: '',
        });

        renderWithProviders(<PublicAuthorPage />);

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

        renderWithProviders(<PublicAuthorPage />);

        await waitFor(() => {
            expect(screen.getByText('全栈开发者')).toBeTruthy();
        });
    });

    it('博客标题从 SiteProvider 获取', async () => {
        apiRequest.mockResolvedValue({
            blog_title: '我的技术博客',
            name: '李四',
            bio: '',
            email: '',
            avatar: '',
            link: '',
        });

        renderWithProviders(<PublicAuthorPage />);

        await waitFor(() => {
            expect(screen.getByText('我的技术博客')).toBeTruthy();
        });
    });
});
