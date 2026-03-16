import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import AuthGuard from './shared/auth/AuthGuard';
import { PostListSkeleton } from './shared/components/Skeleton';

// 懒加载页面组件
const SetupPage = lazy(() => import('./setup/pages/SetupPage'));
const LoginPage = lazy(() => import('./admin/pages/LoginPage'));
const AdminHomePage = lazy(() => import('./admin/pages/AdminHomePage'));
const AdminPostsPage = lazy(() => import('./admin/pages/AdminPostsPage'));
const AdminTaxonomyPage = lazy(() => import('./admin/pages/AdminTaxonomyPage'));
const AdminAuthorPage = lazy(() => import('./admin/pages/AdminAuthorPage'));
const PublicHomePage = lazy(() => import('./public/pages/PublicHomePage'));
const PublicPostDetailPage = lazy(() => import('./public/pages/PublicPostDetailPage'));
const PublicCategoryPage = lazy(() => import('./public/pages/PublicCategoryPage'));
const PublicTagPage = lazy(() => import('./public/pages/PublicTagPage'));
const PublicAuthorPage = lazy(() => import('./public/pages/PublicAuthorPage'));
const PublicTaxonomyListPage = lazy(() => import('./public/pages/PublicTaxonomyListPage'));
const NotFoundPage = lazy(() => import('./public/pages/NotFoundPage'));

function PageFallback() {
    return (
        <div className="app-shell public-shell">
            <PostListSkeleton count={2} />
        </div>
    );
}

function Lazy({ Component, ...props }) {
    return (
        <Suspense fallback={<PageFallback />}>
            <Component {...props} />
        </Suspense>
    );
}

export default function App() {
    return (
        <Suspense fallback={<PageFallback />}>
            <Routes>
                <Route path="/setup" element={<Lazy Component={SetupPage} />} />
                <Route path="/" element={<Lazy Component={PublicHomePage} />} />
                <Route path="/posts/:slug" element={<Lazy Component={PublicPostDetailPage} />} />
                <Route path="/categories/:slug" element={<Lazy Component={PublicCategoryPage} />} />
                <Route path="/categories" element={<Lazy Component={PublicTaxonomyListPage} />} />
                <Route path="/tags/:slug" element={<Lazy Component={PublicTagPage} />} />
                <Route path="/author" element={<Lazy Component={PublicAuthorPage} />} />
                <Route path="/admin/login" element={<Lazy Component={LoginPage} />} />
                <Route path="/admin" element={
                    <AuthGuard><Lazy Component={AdminHomePage} /></AuthGuard>
                } />
                <Route path="/admin/posts" element={
                    <AuthGuard><Lazy Component={AdminPostsPage} /></AuthGuard>
                } />
                <Route path="/admin/taxonomy" element={
                    <AuthGuard><Lazy Component={AdminTaxonomyPage} /></AuthGuard>
                } />
                <Route path="/admin/author" element={
                    <AuthGuard><Lazy Component={AdminAuthorPage} /></AuthGuard>
                } />
                <Route path="*" element={<Lazy Component={NotFoundPage} />} />
            </Routes>
        </Suspense>
    );
}
