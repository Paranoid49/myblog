# API 与扩展总览

## API 基本约定

- Base Path：`/api/v1`
- JSON 接口：`application/json`
- 登录接口：`application/x-www-form-urlencoded`
- 统一响应结构：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

### 成功语义
- `code = 0`
- HTTP 状态码表达传输层语义（200 / 201 等）

### 失败语义
- `code != 0`
- `data = null`
- `message` 使用稳定英文错误标识

---

## 主要错误码

- `1001`：`site_not_initialized`
- `1002`：`unauthorized`
- `1003`：`invalid_credentials`
- `1404`：`post_not_found`
- `1409`：`category_exists`
- `1410`：`tag_exists`
- `1411`：`unsupported_image_type`
- `1412`：`image_too_large`
- `1413`：`category_not_found`
- `1414`：`tag_not_found`

---

## 核心接口分组

### 认证接口
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`

### 作者资料接口
- `GET /api/v1/author`
- `POST /api/v1/author`

### 前台内容接口
- `GET /api/v1/posts`
- `GET /api/v1/posts/{slug}`
- `GET /api/v1/categories/{slug}`
- `GET /api/v1/tags/{slug}`

### 后台文章接口
- `GET /api/v1/admin/posts`
- `POST /api/v1/admin/posts`
- `POST /api/v1/admin/posts/{post_id}`
- `POST /api/v1/admin/posts/{post_id}/publish`
- `POST /api/v1/admin/posts/{post_id}/unpublish`
- `POST /api/v1/admin/posts/import-markdown`
- `GET /api/v1/admin/posts/{post_id}/export-markdown`

### 后台分类标签接口
- `GET /api/v1/taxonomy`
- `POST /api/v1/admin/categories`
- `POST /api/v1/admin/tags`

### 媒体接口
- `POST /api/v1/admin/media/images`

---

## API 边界

### 前台只使用
- `/posts`
- `/posts/{slug}`
- `/categories/{slug}`
- `/tags/{slug}`
- `/author`

### 管理端只使用
- `/auth/*`
- `/author`（写）
- `/admin/posts*`
- `/taxonomy`
- `/admin/categories`
- `/admin/tags`
- `/admin/media/images`

---

## 扩展入口总览

### 主题扩展
当前主题系统支持：
- `light`
- `dark`
- `registerTheme(themeKey)` 注册新主题 key

### 扩展模块加载
后端支持从配置读取模块路径并在启动时导入扩展模块。

### 事件总线（发布订阅）
支持关键业务事件订阅与分发，例如：
- 文章创建 / 更新 / 发布 / 取消发布
- 图片上传

### 数据库 provider
当前内置：
- SQLite
- PostgreSQL

根据 `DATABASE_URL` 解析 provider。

---

## 扩展边界

当前扩展能力是**最小实现**，只承担：

- 主题切换与注册入口
- 模块导入式扩展加载
- 单进程内事件分发
- 数据库连接参数差异抽象

当前**不承担**：

- 插件平台
- 分布式消息系统
- 多层主题运行时系统
- 多租户数据库编排

---

## 原始来源文档

- `docs/api-v1-contract.md`
- `docs/extension-api-v1.md`
- `docs/lightweight-extension-boundaries.md`
