import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// mock useAdminPostsState hook
vi.mock('../../hooks/useAdminPostsState', () => ({
    default: vi.fn(() => ({
        posts: [],
        taxonomy: { categories: [], tags: [] },
        error: '',
        message: '',
        filter: {},
        previewMode: false,
        form: { title: '', summary: '', content: '', category_id: null, tag_ids: [] },
        selectedTagIds: new Set(),
        setPreviewMode: vi.fn(),
        resetForm: vi.fn(),
        fillForEdit: vi.fn(),
        submitForm: vi.fn(),
        importMarkdown: vi.fn(),
        exportMarkdown: vi.fn(),
        uploadImage: vi.fn(),
        publishPost: vi.fn(),
        unpublishPost: vi.fn(),
        applyFilter: vi.fn(),
        handleFieldChange: vi.fn(),
        handleToggleTag: vi.fn(),
    })),
}));

// mock AdminLayout，直接渲染 title 和 children
vi.mock('../../../shared/layout/AdminLayout', () => ({
    default: ({ title, description, children }) => (
        <div data-testid="admin-layout">
            <h2>{title}</h2>
            {description ? <p>{description}</p> : null}
            {children}
        </div>
    ),
}));

// mock 子组件，避免引入更多依赖
vi.mock('../../components/AdminPostEditor', () => ({
    default: () => <div data-testid="post-editor">编辑器</div>,
}));

vi.mock('../../components/AdminPostFilters', () => ({
    default: () => <div data-testid="post-filters">筛选器</div>,
}));

vi.mock('../../components/AdminPostList', () => ({
    default: () => <div data-testid="post-list">文章列表</div>,
}));

import AdminPostsPage from '../AdminPostsPage';
import useAdminPostsState from '../../hooks/useAdminPostsState';

describe('AdminPostsPage', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('渲染文章管理页面标题', () => {
        render(
            <MemoryRouter>
                <AdminPostsPage />
            </MemoryRouter>
        );
        expect(screen.getByText('文章管理')).toBeTruthy();
    });

    it('渲染编辑器、筛选器和文章列表子组件', () => {
        render(
            <MemoryRouter>
                <AdminPostsPage />
            </MemoryRouter>
        );
        expect(screen.getByTestId('post-editor')).toBeTruthy();
        expect(screen.getByTestId('post-filters')).toBeTruthy();
        expect(screen.getByTestId('post-list')).toBeTruthy();
    });

    it('有错误时显示错误提示', () => {
        useAdminPostsState.mockReturnValue({
            posts: [],
            taxonomy: { categories: [], tags: [] },
            error: '加载失败',
            message: '',
            filter: {},
            previewMode: false,
            form: { title: '', summary: '', content: '', category_id: null, tag_ids: [] },
            selectedTagIds: new Set(),
            setPreviewMode: vi.fn(),
            resetForm: vi.fn(),
            fillForEdit: vi.fn(),
            submitForm: vi.fn(),
            importMarkdown: vi.fn(),
            exportMarkdown: vi.fn(),
            uploadImage: vi.fn(),
            publishPost: vi.fn(),
            unpublishPost: vi.fn(),
            applyFilter: vi.fn(),
            handleFieldChange: vi.fn(),
            handleToggleTag: vi.fn(),
        });

        render(
            <MemoryRouter>
                <AdminPostsPage />
            </MemoryRouter>
        );
        expect(screen.getByText('加载失败')).toBeTruthy();
    });

    it('有成功消息时显示成功提示', () => {
        useAdminPostsState.mockReturnValue({
            posts: [],
            taxonomy: { categories: [], tags: [] },
            error: '',
            message: '文章已发布',
            filter: {},
            previewMode: false,
            form: { title: '', summary: '', content: '', category_id: null, tag_ids: [] },
            selectedTagIds: new Set(),
            setPreviewMode: vi.fn(),
            resetForm: vi.fn(),
            fillForEdit: vi.fn(),
            submitForm: vi.fn(),
            importMarkdown: vi.fn(),
            exportMarkdown: vi.fn(),
            uploadImage: vi.fn(),
            publishPost: vi.fn(),
            unpublishPost: vi.fn(),
            applyFilter: vi.fn(),
            handleFieldChange: vi.fn(),
            handleToggleTag: vi.fn(),
        });

        render(
            <MemoryRouter>
                <AdminPostsPage />
            </MemoryRouter>
        );
        expect(screen.getByText('文章已发布')).toBeTruthy();
    });
});
