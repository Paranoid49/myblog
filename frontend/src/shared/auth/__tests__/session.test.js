import { describe, it, expect, beforeEach, vi } from 'vitest';

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

import {
    getStoredUserSnapshot,
    setStoredUserSnapshot,
    clearStoredUserSnapshot,
    hasStoredUserSnapshot,
    getAdminEntryPath,
} from '../session';

describe('session', () => {
    beforeEach(() => {
        localStorageMock.clear();
        vi.clearAllMocks();
    });

    it('getStoredUserSnapshot 无数据时返回 null', () => {
        expect(getStoredUserSnapshot()).toBeNull();
    });

    it('setStoredUserSnapshot 存储后可读取', () => {
        const user = { user_id: 1, username: 'admin' };
        setStoredUserSnapshot(user);
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
            'myblog_user',
            JSON.stringify(user)
        );
    });

    it('clearStoredUserSnapshot 清除后 hasStoredUserSnapshot 返回 false', () => {
        setStoredUserSnapshot({ user_id: 1 });
        clearStoredUserSnapshot();
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('myblog_user');
    });

    it('getAdminEntryPath 无用户时返回登录路径', () => {
        expect(getAdminEntryPath()).toBe('/admin/login');
    });
});
