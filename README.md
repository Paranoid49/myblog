# myblog 最小可用版

## 快速启动

1. 配置环境变量（可选，默认读取 `.env`）
2. 一键启动（自动执行数据库迁移）

```bash
python scripts/start_blog.py
```

默认地址：`http://127.0.0.1:8000`

## 首次使用

1. 访问 `http://127.0.0.1:8000/setup` 完成初始化
2. 访问 `http://127.0.0.1:8000/admin/login` 登录后台（模板页）
3. 在 `文章管理` 创建文章并发布
4. 在 `分类与标签` 页面维护分类与标签

## 静态页（前后端分离过渡）

- 后台登录（静态页）：`/static/web/admin/login.html`
- 文章管理（静态页）：`/static/web/admin/posts.html`
- 分类标签（静态页）：`/static/web/admin/taxonomy.html`
- 前台首页（静态页）：`/static/web/public/index.html`
- 前台详情（静态页）：`/static/web/public/post.html?slug=<post-slug>`

## API 概览（JSON）

- 认证：`POST /api/v1/auth/login`、`POST /api/v1/auth/logout`
- 前台：`GET /api/v1/posts`、`GET /api/v1/posts/{slug}`
- 后台文章：`GET /api/v1/admin/posts`、`POST /api/v1/admin/posts`、`POST /api/v1/admin/posts/{id}/publish`、`POST /api/v1/admin/posts/{id}/unpublish`
- 后台分类标签：`GET /api/v1/taxonomy`、`POST /api/v1/admin/categories`、`POST /api/v1/admin/tags`

## 四步完成清单

- Step1 API 契约完善：已完成（统一 `code/message/data`，补齐前台详情、后台列表、taxonomy 与创建接口）
- Step2 纯静态页：已完成（admin/public 纯 HTML/CSS/JS + fetch）
- Step3 认证迁移最小实现：已完成（静态页复用 session 鉴权，same-origin credentials）
- Step4 渐进替换页面：已完成（模板页与静态页并存，admin/public 均可切换到 JSON 链路）

## 当前功能

- 首次初始化（管理员 + 站点信息）
- 管理员登录/退出
- 文章创建、编辑
- 文章发布 / 转为草稿
- 分类与标签创建
- 首页仅展示已发布文章
