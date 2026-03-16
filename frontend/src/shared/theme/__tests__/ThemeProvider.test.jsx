import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../ThemeProvider';

// 模拟 localStorage
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

/** 消费 ThemeContext 的辅助组件 */
function ThemeConsumer() {
    const { theme, toggleTheme, themes } = useTheme();
    return (
        <div>
            <span data-testid="current-theme">{theme}</span>
            <span data-testid="theme-count">{themes.length}</span>
            <button onClick={toggleTheme}>切换</button>
        </div>
    );
}

describe('ThemeProvider', () => {
    beforeEach(() => {
        localStorageMock.clear();
        vi.clearAllMocks();
        document.documentElement.removeAttribute('data-theme');
    });

    it('默认主题为 light', () => {
        render(
            <ThemeProvider>
                <ThemeConsumer />
            </ThemeProvider>
        );
        expect(screen.getByTestId('current-theme').textContent).toBe('light');
    });

    it('内置 light 和 dark 两个主题', () => {
        render(
            <ThemeProvider>
                <ThemeConsumer />
            </ThemeProvider>
        );
        expect(screen.getByTestId('theme-count').textContent).toBe('2');
    });

    it('点击切换按钮可在 light 和 dark 之间切换', () => {
        render(
            <ThemeProvider>
                <ThemeConsumer />
            </ThemeProvider>
        );
        fireEvent.click(screen.getByText('切换'));
        expect(screen.getByTestId('current-theme').textContent).toBe('dark');
    });

    it('切换主题后写入 localStorage', () => {
        render(
            <ThemeProvider>
                <ThemeConsumer />
            </ThemeProvider>
        );
        fireEvent.click(screen.getByText('切换'));
        expect(localStorageMock.setItem).toHaveBeenCalledWith('myblog_theme', 'dark');
    });

    it('切换主题后设置 data-theme 属性', () => {
        render(
            <ThemeProvider>
                <ThemeConsumer />
            </ThemeProvider>
        );
        fireEvent.click(screen.getByText('切换'));
        expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });

    it('从 localStorage 恢复已保存的主题', () => {
        localStorageMock.getItem.mockReturnValueOnce('dark');
        render(
            <ThemeProvider>
                <ThemeConsumer />
            </ThemeProvider>
        );
        expect(screen.getByTestId('current-theme').textContent).toBe('dark');
    });

    it('localStorage 中存储的无效主题回退为 light', () => {
        localStorageMock.getItem.mockReturnValueOnce('invalid-theme');
        render(
            <ThemeProvider>
                <ThemeConsumer />
            </ThemeProvider>
        );
        expect(screen.getByTestId('current-theme').textContent).toBe('light');
    });
});
