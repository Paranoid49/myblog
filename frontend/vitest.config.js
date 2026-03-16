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
            'node_modules/**',
            'src/**/*.test.mjs',
            'src/admin/hooks/useAdminPostsState.helpers.test.js',
        ],
        // 覆盖率配置，使用 v8 引擎
        coverage: {
            provider: 'v8',
            reporter: ['text', 'text-summary'],
            include: ['src/**/*.{js,jsx}'],
            exclude: ['src/**/__tests__/**', 'src/**/*.test.*', 'src/test-setup.js'],
        },
    },
});
