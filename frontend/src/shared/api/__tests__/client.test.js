import { describe, it, expect, vi, beforeEach } from 'vitest';

// mock fetch
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// mock session 中的重定向函数
vi.mock('../../auth/session', () => ({
    redirectToLoginAfterUnauthorized: vi.fn(),
}));

import { apiRequest } from '../client';
import { redirectToLoginAfterUnauthorized } from '../../auth/session';

describe('apiRequest', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('成功响应返回 data 字段', async () => {
        mockFetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({ code: 0, message: 'ok', data: { id: 1 } }),
        });
        const result = await apiRequest('/posts');
        expect(result).toEqual({ id: 1 });
    });

    it('请求路径自动拼接 /api/v1 前缀', async () => {
        mockFetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({ code: 0, message: 'ok', data: null }),
        });
        await apiRequest('/test');
        expect(mockFetch).toHaveBeenCalledWith(
            '/api/v1/test',
            expect.anything()
        );
    });

    it('默认携带 X-Requested-With 头', async () => {
        mockFetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({ code: 0, message: 'ok', data: null }),
        });
        await apiRequest('/test');
        expect(mockFetch).toHaveBeenCalledWith(
            '/api/v1/test',
            expect.objectContaining({
                headers: expect.objectContaining({
                    'X-Requested-With': 'XMLHttpRequest',
                }),
            })
        );
    });

    it('默认携带 credentials: same-origin', async () => {
        mockFetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({ code: 0, message: 'ok', data: null }),
        });
        await apiRequest('/test');
        expect(mockFetch).toHaveBeenCalledWith(
            '/api/v1/test',
            expect.objectContaining({
                credentials: 'same-origin',
            })
        );
    });

    it('业务错误（code != 0）抛出异常', async () => {
        mockFetch.mockResolvedValue({
            ok: false,
            status: 404,
            json: () => Promise.resolve({ code: 1404, message: 'post_not_found', data: null }),
        });
        await expect(apiRequest('/posts/xxx')).rejects.toThrow('post_not_found');
    });

    it('401 + code 1002 触发登录跳转', async () => {
        mockFetch.mockResolvedValue({
            ok: false,
            status: 401,
            json: () => Promise.resolve({ code: 1002, message: 'unauthorized', data: null }),
        });
        await expect(apiRequest('/admin/posts')).rejects.toThrow();
        expect(redirectToLoginAfterUnauthorized).toHaveBeenCalled();
    });

    it('401 但 code 不为 1002 时不触发登录跳转', async () => {
        mockFetch.mockResolvedValue({
            ok: false,
            status: 401,
            json: () => Promise.resolve({ code: 9999, message: 'other_error', data: null }),
        });
        await expect(apiRequest('/admin/posts')).rejects.toThrow();
        expect(redirectToLoginAfterUnauthorized).not.toHaveBeenCalled();
    });

    it('JSON 解析失败时抛出带 status 的错误', async () => {
        mockFetch.mockResolvedValue({
            ok: false,
            status: 500,
            json: () => Promise.reject(new Error('invalid json')),
        });
        await expect(apiRequest('/broken')).rejects.toThrow('http_500');
    });
});
