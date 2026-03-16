import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    test: {
        environment: 'jsdom',
        globals: true,
        setupFiles: './src/test-setup.js',
        // 排除使用 node:test 的旧测试文件，仅收集 Vitest 格式的测试
        exclude: [
            '**/*.test.mjs',
            '**/useAdminPostsState.helpers.test.js',
            '**/node_modules/**',
        ],
    },
});
