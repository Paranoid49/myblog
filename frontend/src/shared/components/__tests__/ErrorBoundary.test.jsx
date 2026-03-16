import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import ErrorBoundary from '../ErrorBoundary';

// 故意抛出错误的组件，用于触发错误边界
function BrokenComponent() {
    throw new Error('测试错误');
}

describe('ErrorBoundary', () => {
    beforeEach(() => { vi.spyOn(console, 'error').mockImplementation(() => {}); });
    afterEach(() => { vi.restoreAllMocks(); });

    it('正常子组件正常渲染', () => {
        render(<ErrorBoundary><div>正常内容</div></ErrorBoundary>);
        expect(screen.getByText('正常内容')).toBeTruthy();
    });

    it('子组件报错时显示友好界面', () => {
        render(<ErrorBoundary><BrokenComponent /></ErrorBoundary>);
        expect(screen.getByText('出错了')).toBeTruthy();
    });

    it('显示刷新按钮', () => {
        render(<ErrorBoundary><BrokenComponent /></ErrorBoundary>);
        expect(screen.getByText('刷新页面')).toBeTruthy();
    });
});
