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

- `1001`：`site_not_initialized`
- `1002`：`unauthorized`
- `1003`：`invalid_credentials`
- `1404`：`post_not_found`
- `1409`：`category_exists`
- `1410`：`tag_exists`

## 3. 认证接口（Public/Auth）

### 3.1 POST `/api/v1/auth/login`
- 入参（Form）：`username`、`password`
- 成功：200
- 返回 data：`{ user_id, username }`

### 3.2 POST `/api/v1/auth/logout`
- 入参：无
- 成功：200
- 返回 data：`null`

## 4. 前台内容接口（Public/Posts）

### 4.1 GET `/api/v1/posts`
- 说明：返回已发布文章列表
- 成功：200
- 返回 data：`Post[]`

### 4.2 GET `/api/v1/posts/{slug}`
- 说明：返回单篇已发布文章详情
- 成功：200
- 失败：404（`1404`）

## 5. 后台文章接口（Admin/Posts）

> 需要登录（session）

### 5.1 GET `/api/v1/admin/posts`
- 说明：返回后台文章列表（包含草稿与已发布）
- 成功：200

### 5.2 POST `/api/v1/admin/posts`
- 入参（JSON）：
  - `title: string`
  - `summary: string | null`
  - `content: string`
  - `category_id: int | null`
  - `tag_ids: int[]`
- 成功：201
- 说明：`category_id` 为空时走默认分类策略

### 5.3 POST `/api/v1/admin/posts/{post_id}/publish`
- 成功：200
- 失败：404（`1404`）

### 5.4 POST `/api/v1/admin/posts/{post_id}/unpublish`
- 成功：200
- 失败：404（`1404`）

## 6. 后台分类标签接口（Admin/Taxonomy）

> 需要登录（session）

### 6.1 GET `/api/v1/taxonomy`
- 成功：200
- 返回 data：

```json
{
  "categories": [{ "id": 1, "name": "Python", "slug": "python" }],
  "tags": [{ "id": 1, "name": "FastAPI", "slug": "fastapi" }]
}
```

### 6.2 POST `/api/v1/admin/categories`
- 入参（JSON）：`{ "name": "数据库" }`
- 成功：201
- 失败：409（`1409`）

### 6.3 POST `/api/v1/admin/tags`
- 入参（JSON）：`{ "name": "后端" }`
- 成功：201
- 失败：409（`1410`）

## 7. 数据模型（API 返回最小字段）

### 7.1 Post

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

### 7.2 Category/Tag

```json
{ "id": 1, "name": "Python", "slug": "python" }
```

## 8. 管理端与前台边界

- 前台仅使用：`/posts`、`/posts/{slug}`
- 管理端仅使用：`/auth/*`、`/admin/posts*`、`/taxonomy`、`/admin/categories`、`/admin/tags`
- 前台不直接调用后台写接口

## 9. 兼容策略（V1）

- 保持响应结构稳定（`code/message/data`）
- 新增字段遵循向后兼容（只增不删）
- 变更错误码需更新本文件并同步测试
