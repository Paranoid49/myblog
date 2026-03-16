import { describe, it, expect } from 'vitest';
import { getAuthGuardRedirect } from '../navigation';

describe('getAuthGuardRedirect', () => {
    it('有用户快照时不重定向', () => {
        expect(getAuthGuardRedirect('/admin', true)).toBeNull();
    });

    it('无用户快照时重定向到登录页', () => {
        const result = getAuthGuardRedirect('/admin/posts', false);
        expect(result).toEqual({
            to: '/admin/login',
            state: { from: '/admin/posts' },
        });
    });

    it('无路径名时 state 不包含 from', () => {
        const result = getAuthGuardRedirect('', false);
        expect(result).toEqual({
            to: '/admin/login',
            state: undefined,
        });
    });
});
