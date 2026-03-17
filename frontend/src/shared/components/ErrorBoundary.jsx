import { Component } from 'react';

/**
 * 错误边界组件 — 捕获子组件渲染错误，防止白屏
 */
export default class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary 捕获错误:', error, errorInfo);
        if (this.props.onError) {
            this.props.onError(error, errorInfo);
        }
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="site-frame center-frame">
                    <div className="panel-card auth-card">
                        <h2 className="mb-md">出错了</h2>
                        <p className="muted mb-lg">页面遇到了意外错误，请刷新重试。</p>
                        <button
                            className="primary-button"
                            onClick={() => window.location.reload()}
                        >
                            刷新页面
                        </button>
                    </div>
                </div>
            );
        }
        return this.props.children;
    }
}
