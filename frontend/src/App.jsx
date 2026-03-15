import { Route, Routes } from 'react-router-dom';
import SetupPage from './setup/pages/SetupPage';
import LoginPage from './admin/pages/LoginPage';
import AdminHomePage from './admin/pages/AdminHomePage';
import AdminPostsPage from './admin/pages/AdminPostsPage';
import AdminTaxonomyPage from './admin/pages/AdminTaxonomyPage';
import AdminAuthorPage from './admin/pages/AdminAuthorPage';
import AuthGuard from './shared/auth/AuthGuard';
import PublicCategoryPage from './public/pages/PublicCategoryPage';
import PublicTagPage from './public/pages/PublicTagPage';
import PublicHomePage from './public/pages/PublicHomePage';
import PublicPostDetailPage from './public/pages/PublicPostDetailPage';
import PublicAuthorPage from './public/pages/PublicAuthorPage';
import NotFoundPage from './public/pages/NotFoundPage';

export default function App() {
  return (
    <Routes>
      <Route path="/setup" element={<SetupPage />} />
      <Route path="/" element={<PublicHomePage />} />
      <Route path="/posts/:slug" element={<PublicPostDetailPage />} />
      <Route path="/categories/:slug" element={<PublicCategoryPage />} />
      <Route path="/tags/:slug" element={<PublicTagPage />} />
      <Route path="/author" element={<PublicAuthorPage />} />

      <Route path="/admin/login" element={<LoginPage />} />
      <Route
        path="/admin"
        element={
          <AuthGuard>
            <AdminHomePage />
          </AuthGuard>
        }
      />
      <Route
        path="/admin/posts"
        element={
          <AuthGuard>
            <AdminPostsPage />
          </AuthGuard>
        }
      />
      <Route
        path="/admin/taxonomy"
        element={
          <AuthGuard>
            <AdminTaxonomyPage />
          </AuthGuard>
        }
      />
      <Route
        path="/admin/author"
        element={
          <AuthGuard>
            <AdminAuthorPage />
          </AuthGuard>
        }
      />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}