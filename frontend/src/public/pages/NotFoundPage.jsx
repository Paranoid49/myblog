import { Link } from 'react-router-dom';
import PublicLayout from '../../shared/layout/PublicLayout';

export default function NotFoundPage() {
    return (
        <PublicLayout title="页面未找到" description="抱歉，您访问的页面不存在。">
            <div className="notice muted">
                <p>可能的原因：</p>
                <ul>
                    <li>页面已被移动或删除</li>
                    <li>URL 输入有误</li>
                </ul>
                <p className="mt-md">
                    <Link to="/" className="nav-link">← 返回首页</Link>
                </p>
            </div>
        </PublicLayout>
    );
}
