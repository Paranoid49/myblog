import PublicLayout from '../../shared/layout/PublicLayout';

export default function NotFoundPage() {
  return (
    <PublicLayout>
      <div className="not-found-page">
        <h1 className="not-found-code">404</h1>
        <p className="not-found-message">页面不存在</p>
      </div>
    </PublicLayout>
  );
}
