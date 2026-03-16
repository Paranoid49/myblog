import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// mock apiRequest 和 session 模块
vi.mock('../../../shared/api/client', () => ({
    apiRequest: vi.fn(),
}));

vi.mock('../../../shared/auth/session', () => ({
    hasStoredUserSnapshot: vi.fn(() => false),
    getLoginRedirectPath: vi.fn(() => '/admin'),
    loginWithUserSnapshot: vi.fn(),
}));

import LoginPage from '../LoginPage';

describe('LoginPage', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('渲染登录表单', () => {
        render(
            <MemoryRouter>
                <LoginPage />
            </MemoryRouter>
        );
        // 页面标题 h2 包含 "登录"，按钮也包含 "登录"，使用 getAllByText 匹配多个元素
        const matches = screen.getAllByText(/登录/);
        expect(matches.length).toBeGreaterThanOrEqual(1);
    });

    it('包含用户名和密码输入框', () => {
        const { container } = render(
            <MemoryRouter>
                <LoginPage />
            </MemoryRouter>
        );
        // LoginPage 的 label 使用 className="form-label"，未通过 htmlFor 关联 input
        // 因此使用 querySelector 查找 input 元素
        expect(container.querySelector('input[name="username"]')).toBeTruthy();
        expect(container.querySelector('input[type="password"]')).toBeTruthy();
    });

    it('包含提交按钮', () => {
        render(
            <MemoryRouter>
                <LoginPage />
            </MemoryRouter>
        );
        const button = screen.getByRole('button', { name: /登录/ });
        expect(button).toBeTruthy();
        expect(button.type).toBe('submit');
    });

    it('包含返回首页链接', () => {
        render(
            <MemoryRouter>
                <LoginPage />
            </MemoryRouter>
        );
        expect(screen.getByText('← 返回首页')).toBeTruthy();
    });
});
