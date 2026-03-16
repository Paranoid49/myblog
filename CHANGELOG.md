# CHANGELOG

## v1.0.0 (2026-03-16)

### 功能
- 文章 CRUD、发布/转草稿
- Markdown 导入/导出
- 分类单选、标签多选
- 图片上传（jpg/png/webp/gif，5MB 限制）
- 作者资料管理
- light/dark 主题切换
- 初始化向导
- SQLite/PostgreSQL 数据库支持

### 安全
- Session/Cookie 认证
- CSRF 保护（自定义头校验）
- 图片上传 Magic Bytes 校验
- 登录速率限制（5分钟/5次）
- 安全响应头（CSP、X-Frame-Options 等）
- 生产环境强制安全密钥

### 扩展
- 数据库 Provider（SQLite/PostgreSQL）
- Hook 事件总线（发布/订阅）
- 扩展模块加载器
- 前端主题注册

### 工程
- CI/CD 管线（GitHub Actions）
- Docker 容器化部署
- 结构化日志
