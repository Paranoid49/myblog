import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Pagination from '../Pagination';

describe('Pagination', () => {
    it('totalPages <= 1 时不渲染', () => {
        const { container } = render(
            <Pagination page={1} totalPages={1} onPageChange={() => {}} />
        );
        expect(container.querySelector('.pagination')).toBeNull();
    });

    it('渲染页码信息', () => {
        render(<Pagination page={2} totalPages={5} onPageChange={() => {}} />);
        expect(screen.getByText('2 / 5')).toBeTruthy();
    });

    it('点击下一页触发回调', () => {
        const onChange = vi.fn();
        render(<Pagination page={1} totalPages={3} onPageChange={onChange} />);
        fireEvent.click(screen.getByText(/下一页/));
        expect(onChange).toHaveBeenCalledWith(2);
    });

    it('第一页时上一页按钮禁用', () => {
        render(<Pagination page={1} totalPages={3} onPageChange={() => {}} />);
        expect(screen.getByText(/上一页/).disabled).toBe(true);
    });

    it('最后一页时下一页按钮禁用', () => {
        render(<Pagination page={3} totalPages={3} onPageChange={() => {}} />);
        expect(screen.getByText(/下一页/).disabled).toBe(true);
    });
});
