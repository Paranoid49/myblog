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

## 2. 错误码约定

> 当前错误码权威来源：`app/core/error_codes.py`

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
- 说明：返回已发布文章列表
- 成功：200
- 返回 data：`Post[]`

### 5.2 GET `/api/v1/posts/{slug}`
- 说明：返回单篇已发布文章详情
- 成功：200
- 失败：404（`1404`）

### 5.3 GET `/api/v1/categories/{slug}`
- 说明：返回指定分类下的已发布文章列表
- 成功：200
- 失败：404（`1413`）
- 返回 data：

```json
{
  "category": { "id": 1, "name": "Python", "slug": "python" },
  "posts": []
}
```

### 5.4 GET `/api/v1/tags/{slug}`
- 说明：返回指定标签下的已发布文章列表
- 成功：200
- 失败：404（`1414`）
- 返回 data：

```json
{
  "tag": { "id": 1, "name": "FastAPI", "slug": "fastapi" },
  "posts": []
}
```

## 6. 后台文章接口（Admin/Posts）

> 需要登录（session）

### 6.1 GET `/api/v1/admin/posts`
- 说明：返回后台文章列表（包含草稿与已发布）
- 成功：200

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
- 入参（JSON）：`{ "name": "数据库" }`
- 成功：201
- 失败：409（`1409`）

### 7.3 POST `/api/v1/admin/tags`
- 入参（JSON）：`{ "name": "后端" }`
- 成功：201
- 失败：409（`1410`）

## 8. 数据模型（API 返回最小字段）

### 8.1 AuthorProfile

```json
{
  "name": "admin",
  "bio": "这是作者简介",
  "email": "admin@example.com",
  "avatar": "https://example.com/avatar.png",
  "link": "https://example.com/about"
}
```

### 8.2 Post

```json
{
  "id": 1,
  "title": "文章标题",
  "slug": "wen-zhang-biao-ti",
  "summary": "摘要",
  "content": "正文",
  "category_id": 1,
  "tag_ids": [1, 2],
  "published_at": "2026-03-09T10:00:00+00:00"
}
```

### 8.3 Category/Tag

```json
{ "id": 1, "name": "Python", "slug": "python" }
```

## 9. 管理端与前台边界

- 前台仅使用：`/posts`、`/posts/{slug}`、`/categories/{slug}`、`/tags/{slug}`、`/author`
- 管理端仅使用：`/auth/*`、`/author`（写）、`/admin/posts*`、`/taxonomy`、`/admin/categories`、`/admin/tags`
- 前台不直接调用后台写接口

## 10. 兼容策略（V1）

- 保持响应结构稳定（`code/message/data`）
- 新增字段遵循向后兼容（只增不删）
- 变更错误码需更新本文件并同步测试

## 11. 扩展边界补充

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
