import { describe, it, expect } from 'vitest';
import { formatDate } from '../format';

describe('formatDate', () => {
    it('格式化 ISO 日期字符串为中文日期', () => {
        const result = formatDate('2024-06-15T12:00:00Z');
        // toLocaleDateString('zh-CN') 格式为 YYYY/MM/DD
        expect(result).toMatch(/2024/);
        expect(result).toMatch(/06/);
        expect(result).toMatch(/15/);
    });

    it('传入 null 返回"未发布"', () => {
        expect(formatDate(null)).toBe('未发布');
    });

    it('传入 undefined 返回"未发布"', () => {
        expect(formatDate(undefined)).toBe('未发布');
    });

    it('传入空字符串返回"未发布"', () => {
        expect(formatDate('')).toBe('未发布');
    });

    it('传入不含时间的日期字符串也能正常格式化', () => {
        const result = formatDate('2023-01-01');
        expect(result).toMatch(/2023/);
        expect(result).toMatch(/01/);
    });

    it('格式化结果不包含时间信息', () => {
        const result = formatDate('2024-12-25T23:59:59Z');
        // 不应包含冒号（时间分隔符）
        expect(result).not.toMatch(/:/);
    });
});
