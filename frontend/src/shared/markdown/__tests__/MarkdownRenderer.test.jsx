import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MarkdownRenderer from '../MarkdownRenderer';

describe('MarkdownRenderer', () => {
    it('渲染普通文本', () => {
        render(<MarkdownRenderer content="Hello World" />);
        expect(screen.getByText('Hello World')).toBeTruthy();
    });

    it('渲染标题', () => {
        render(<MarkdownRenderer content="# 标题" />);
        const heading = screen.getByText('标题');
        expect(heading).toBeTruthy();
        expect(heading.tagName).toBe('H1');
    });

    it('空内容不崩溃', () => {
        const { container } = render(<MarkdownRenderer content="" />);
        // 不抛异常即为通过，容器应包含 markdown-body
        expect(container.querySelector('.markdown-body')).toBeTruthy();
    });

    it('未传 content 时使用默认空字符串不崩溃', () => {
        const { container } = render(<MarkdownRenderer />);
        expect(container.querySelector('.markdown-body')).toBeTruthy();
    });

    it('渲染代码块', () => {
        render(<MarkdownRenderer content={'```\nconsole.log("test")\n```'} />);
        expect(screen.getByText('console.log("test")')).toBeTruthy();
    });

    it('渲染加粗文本', () => {
        render(<MarkdownRenderer content="这是**加粗**文本" />);
        const bold = screen.getByText('加粗');
        expect(bold.tagName).toBe('STRONG');
    });

    it('默认包含 markdown-body 类名', () => {
        const { container } = render(<MarkdownRenderer content="text" />);
        expect(container.querySelector('.markdown-body')).toBeTruthy();
    });

    it('传入 className 时拼接到 markdown-body 之后', () => {
        const { container } = render(<MarkdownRenderer content="text" className="custom" />);
        const el = container.querySelector('.markdown-body.custom');
        expect(el).toBeTruthy();
    });

    it('渲染 GFM 表格', () => {
        const table = '| 列A | 列B |\n| --- | --- |\n| 1 | 2 |';
        const { container } = render(<MarkdownRenderer content={table} />);
        expect(container.querySelector('table')).toBeTruthy();
    });
});
