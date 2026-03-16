import js from '@eslint/js';
import reactPlugin from 'eslint-plugin-react';
import reactHooksPlugin from 'eslint-plugin-react-hooks';

export default [
    js.configs.recommended,
    {
        files: ['src/**/*.{js,jsx}'],
        plugins: {
            react: reactPlugin,
            'react-hooks': reactHooksPlugin,
        },
        languageOptions: {
            ecmaVersion: 2024,
            sourceType: 'module',
            parserOptions: {
                ecmaFeatures: { jsx: true },
            },
            globals: {
                window: 'readonly',
                document: 'readonly',
                console: 'readonly',
                fetch: 'readonly',
                FormData: 'readonly',
                URLSearchParams: 'readonly',
                FileReader: 'readonly',
                setTimeout: 'readonly',
                clearTimeout: 'readonly',
                URL: 'readonly',
            },
        },
        settings: {
            react: { version: 'detect' },
        },
        rules: {
            'react/react-in-jsx-scope': 'off',
            'react/prop-types': 'off',
            'react-hooks/rules-of-hooks': 'error',
            'react-hooks/exhaustive-deps': 'warn',
            'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
        },
    },
];
