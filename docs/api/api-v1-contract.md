# API V1 契约文档

## 1. 通用约定

- Base Path：`/api/v1`
- Content-Type：
  - JSON 接口：`application/json`
  - 登录接口：`application/x-www-form-urlencoded`（当前实现）
- 统一响应结构：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

### 1.1 成功语义
- `code = 0` 代表业务成功
- HTTP 状态码表达传输层语义（200/201 等）

### 1.2 失败语义
- `code != 0` 代表业务失败
- `data = null`
- `message` 使用稳定英文错误标识

### 1.3 分页约定

所有列表接口支持分页查询参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | int | 1 | 页码，从 1 开始 |
| `page_size` | int | 20 | 每页条数 |

分页响应结构：

```json
{
  "items": [],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

适用接口：`GET /posts`、`GET /admin/posts`、`GET /categories/{slug}`、`GET /tags/{slug}`

## 2. 错误码约定

> 当前错误码权威来源：`app/core/error_codes.py`

### 2.1 通用错误码

| 错误码 | 标识 | 说明 |
|--------|------|------|
| `1001` | `site_not_initialized` | 站点未初始化 |
| `1002` | `unauthorized` | 未登录或会话过期 |
| `1003` | `invalid_credentials` | 用户名或密码错误 |
| `1005` | `csrf_rejected` | CSRF 校验失败 |
| `1006` | `too_many_attempts` | 请求过于频繁（限流） |

### 2.2 资源错误码

| 错误码 | 标识 | 说明 |
|--------|------|------|
| `1404` | `post_not_found` | 文章不存在 |
| `1409` | `category_exists` | 分类名称已存在 |
| `1410` | `tag_exists` | 标签名称已存在 |
| `1411` | `unsupported_image_type` | 不支持的图片类型 |
| `1412` | `image_too_large` | 图片超过大小限制 |
| `1413` | `category_not_found` | 分类不存在 |
| `1414` | `tag_not_found` | 标签不存在 |
| `1415` | `request_too_large` | 请求体超过大小限制 |

### 2.3 初始化/密码错误码

| 错误码 | 标识 | 说明 |
|--------|------|------|
| `2001` | `setup_password_mismatch` | 两次密码不一致 |
| `2002` | `setup_database_bootstrap_failed` | 数据库初始化失败 |
| `2003` | `setup_migration_failed` | 数据库迁移失败 |
| `2004` | `setup_already_initialized` | 站点已初始化 |
| `2005` | `password_too_short` | 密码长度不足 |
| `2006` | `password_needs_digit` | 密码缺少数字 |
| `2007` | `password_needs_letter` | 密码缺少字母 |

## 3. 认证接口（Public/Auth）

### 3.1 POST `/api/v1/auth/login`
- 入参（Form）：`username`、`password`
- 成功：200
- 返回 data：`{ user_id, username }`

### 3.2 POST `/api/v1/auth/logout`
- 入参：无
- 成功：200
- 返回 data：`null`

## 4. 作者资料接口（Public/Author）

### 4.1 GET `/api/v1/author`
- 说明：返回站点作者公开资料
- 成功：200
- 失败：409（`1001`）
- 返回 data：`AuthorProfile`

### 4.2 POST `/api/v1/author`

> 需要登录（session）

- 入参（JSON）：
  - `name: string`
  - `bio: string`
  - `email: string`
  - `avatar: string`
  - `link: string`
- 成功：200
- 失败：401（`1002`）、409（`1001`）
- 说明：新增字段遵循向后兼容，`avatar` 与 `link` 可为空字符串

## 5. 前台内容接口（Public/Posts）

### 5.1 GET `/api/v1/posts`
- 说明：返回已发布文章列表（分页）
- 查询参数：`page`（默认 1）、`page_size`（默认 20）
- 成功：200
- 返回 data：分页结构 `{ items: Post[], total, page, page_size, total_pages }`

### 5.2 GET `/api/v1/posts/{slug}`
- 说明：返回单篇已发布文章详情
- 成功：200
- 失败：404（`1404`）

### 5.3 GET `/api/v1/categories/{slug}`
- 说明：返回指定分类下的已发布文章列表（分页）
- 查询参数：`page`（默认 1）、`page_size`（默认 20）
- 成功：200
- 失败：404（`1413`）
- 返回 data：

```json
{
  "category": { "id": 1, "name": "Python", "slug": "python" },
  "posts": { "items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 0 }
}
```

### 5.4 GET `/api/v1/tags/{slug}`
- 说明：返回指定标签下的已发布文章列表（分页）
- 查询参数：`page`（默认 1）、`page_size`（默认 20）
- 成功：200
- 失败：404（`1414`）
- 返回 data：

```json
{
  "tag": { "id": 1, "name": "FastAPI", "slug": "fastapi" },
  "posts": { "items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 0 }
}
```

## 6. 后台文章接口（Admin/Posts）

> 需要登录（session）

### 6.1 GET `/api/v1/admin/posts`
- 说明：返回后台文章列表（包含草稿与已发布，分页）
- 查询参数：`category_id`（可选）、`tag_id`（可选）、`page`（默认 1）、`page_size`（默认 20）
- 成功：200
- 返回 data：分页结构 `{ items: Post[], total, page, page_size, total_pages }`

### 6.2 POST `/api/v1/admin/posts`
- 入参（JSON）：
  - `title: string`
  - `summary: string | null`
  - `content: string`
  - `category_id: int | null`
  - `tag_ids: int[]`
- 成功：201
- 说明：`category_id` 为空时走默认分类策略

### 6.3 POST `/api/v1/admin/posts/{post_id}/publish`
- 成功：200
- 失败：404（`1404`）

### 6.4 POST `/api/v1/admin/posts/{post_id}/unpublish`
- 成功：200
- 失败：404（`1404`）

### 6.5 POST `/api/v1/admin/posts/{post_id}`
- 说明：更新指定文章
- 入参（JSON）：
  - `title: string`
  - `summary: string | null`
  - `content: string`
  - `category_id: int | null`
  - `tag_ids: int[]`
- 成功：200
- 失败：404（`1404`）

### 6.6 POST `/api/v1/admin/posts/{post_id}/delete`
- 说明：删除指定文章
- 成功：200
- 失败：404（`1404`）
- 返回 data：`null`

### 6.7 POST `/api/v1/admin/posts/import-markdown`
- 说明：通过 Markdown 内容导入新文章
- 入参（JSON）：`ImportMarkdownRequest`
- 成功：201

### 6.8 GET `/api/v1/admin/posts/{post_id}/export-markdown`
- 说明：导出指定文章为 Markdown 格式
- 成功：200
- 失败：404（`1404`）

## 7. 后台分类标签接口（Admin/Taxonomy）

> 需要登录（session）

### 7.1 GET `/api/v1/taxonomy`
- 成功：200
- 返回 data：

```json
{
  "categories": [{ "id": 1, "name": "Python", "slug": "python" }],
  "tags": [{ "id": 1, "name": "FastAPI", "slug": "fastapi" }]
}
```

### 7.2 POST `/api/v1/admin/categories`
- 说明：创建分类
- 入参（JSON）：`{ "name": "数据库" }`
- 成功：201
- 失败：409（`1409`）

### 7.3 POST `/api/v1/admin/categories/{category_id}`
- 说明：重命名分类
- 入参（JSON）：`{ "name": "新分类名" }`
- 成功：200
- 失败：404（`1413`）、409（`1409`）

### 7.4 POST `/api/v1/admin/categories/{category_id}/delete`
- 说明：删除分类
- 成功：200
- 失败：404（`1413`）
- 返回 data：`null`

### 7.5 POST `/api/v1/admin/tags`
- 说明：创建标签
- 入参（JSON）：`{ "name": "后端" }`
- 成功：201
- 失败：409（`1410`）

### 7.6 POST `/api/v1/admin/tags/{tag_id}`
- 说明：重命名标签
- 入参（JSON）：`{ "name": "新标签名" }`
- 成功：200
- 失败：404（`1414`）、409（`1410`）

### 7.7 POST `/api/v1/admin/tags/{tag_id}/delete`
- 说明：删除标签
- 成功：200
- 失败：404（`1414`）
- 返回 data：`null`

## 8. 媒体接口（Admin/Media）

> 需要登录（session）

### 8.1 POST `/api/v1/admin/media/images`
- 说明：上传图片
- 入参（Multipart Form）：`file`（图片文件）
- 支持类型：`image/jpeg`、`image/png`、`image/webp`、`image/gif`
- 大小限制：5 MB
- 成功：201
- 失败：400（`1411` 不支持的图片类型）、400（`1412` 图片超过大小限制）
- 返回 data：

```json
{
  "url": "/static/uploads/xxxx.jpg",
  "key": "xxxx.jpg",
  "size": 102400,
  "content_type": "image/jpeg"
}
```

## 9. Feed 接口

### 9.1 GET `/feed.xml`
- 说明：RSS 2.0 Feed，返回已发布文章列表
- Content-Type：`application/rss+xml`
- 缓存：内存缓存 5 分钟
- 成功：200

## 10. 数据模型（API 返回最小字段）

### 10.1 AuthorProfile

```json
{
  "blog_title": "我的博客",
  "name": "admin",
  "bio": "这是作者简介",
  "email": "admin@example.com",
  "avatar": "https://example.com/avatar.png",
  "link": "https://example.com/about"
}
```

### 10.2 Post

```json
{
  "id": 1,
  "title": "文章标题",
  "slug": "wen-zhang-biao-ti",
  "summary": "摘要",
  "content": "正文",
  "category_id": 1,
  "category_name": "Python",
  "category_slug": "python",
  "tag_ids": [1, 2],
  "tags": [{"id": 1, "name": "FastAPI", "slug": "fastapi"}],
  "published_at": "2026-03-09T10:00:00+00:00"
}
```

### 10.3 Category/Tag

```json
{ "id": 1, "name": "Python", "slug": "python" }
```

## 11. 管理端与前台边界

- 前台仅使用：`/posts`、`/posts/{slug}`、`/categories/{slug}`、`/tags/{slug}`、`/author`、`/feed.xml`
- 管理端仅使用：`/auth/*`、`/author`（写）、`/admin/posts*`、`/taxonomy`、`/admin/categories*`、`/admin/tags*`、`/admin/media/*`
- 前台不直接调用后台写接口

## 12. 兼容策略（V1）

- 保持响应结构稳定（`code/message/data`）
- 新增字段遵循向后兼容（只增不删）
- 变更错误码需更新本文件并同步测试

## 13. 扩展边界补充

当前扩展点只承担最小稳定入口：

- `database_provider` 负责数据库 URL 解析与 provider 选择
- `hook_bus` 负责单进程内事件订阅与触发
- `extension_loader` 负责按模块路径导入扩展
- `ThemeProvider` 负责主题切换与主题 key 注册

当前不包含：

- 插件平台或插件市场
- Hook 优先级、重试、持久化、热加载
- 复杂主题包系统
- 多租户数据库编排
