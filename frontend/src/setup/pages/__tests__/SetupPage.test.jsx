import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// mock apiRequest
vi.mock('../../../shared/api/client', () => ({
    apiRequest: vi.fn(),
}));

// mock session 模块
vi.mock('../../../shared/auth/session', () => ({
    setStoredUserSnapshot: vi.fn(),
}));

import { apiRequest } from '../../../shared/api/client';
import SetupPage from '../SetupPage';

describe('SetupPage', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // 模拟未初始化状态，apiRequest('/setup/status') 返回后 loading 变为 false
        apiRequest.mockResolvedValue({ initialized: false, database_exists: true });
    });

    it('渲染初始化表单', async () => {
        render(
            <MemoryRouter>
                <SetupPage />
            </MemoryRouter>
        );
        // 等待 loading 结束，标题 "博客初始化" 出现
        await screen.findByText(/博客初始化/);
        expect(screen.getByText(/博客初始化/)).toBeTruthy();
    });

    it('包含博客标题输入框', async () => {
        const { container } = render(
            <MemoryRouter>
                <SetupPage />
            </MemoryRouter>
        );
        await screen.findByText(/博客初始化/);
        // label 文本为"博客标题"，input 默认值为"我的博客"
        expect(screen.getByText('博客标题')).toBeTruthy();
        expect(container.querySelector('input[type="text"]')).toBeTruthy();
    });

    it('包含管理员用户名和密码输入框', async () => {
        const { container } = render(
            <MemoryRouter>
                <SetupPage />
            </MemoryRouter>
        );
        await screen.findByText(/博客初始化/);
        expect(screen.getByText('管理员用户名')).toBeTruthy();
        // 密码和确认密码共两个 password 输入框
        const passwordInputs = container.querySelectorAll('input[type="password"]');
        expect(passwordInputs.length).toBe(2);
    });

    it('加载中不渲染表单内容', () => {
        // 让 apiRequest 永不 resolve，保持 loading 状态
        apiRequest.mockReturnValue(new Promise(() => {}));
        const { container } = render(
            <MemoryRouter>
                <SetupPage />
            </MemoryRouter>
        );
        // loading 态返回 null，不渲染任何内容
        expect(container.querySelector('.setup-card')).toBeNull();
    });
});
