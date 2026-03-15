# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目哲学

**轻量、克制、可扩展**

本项目的核心目标是成为一个足够轻量的个人博客系统。设计原则：

- **能不引入复杂度就不引入复杂度** - 每一个新增依赖、每一个抽象层都要问"真的需要吗"
- **满足生产要求的最小集合** - 不追求功能完备，追求功能恰好够用
- **核心极简，扩展开放** - 内核保持最小化，通过明确的扩展点（数据库 provider、主题 provider、Hook 机制）支持社区二次开发

这意味着：默认单体部署、默认 SQLite、默认 session 认证、默认无缓存中间件。只有在真实需求驱动时才引入新的复杂度。

## 项目概述

myblog 是一个前后端分离的技术博客系统，采用 FastAPI + React 架构。后端提供 RESTful API，前端使用 React SPA。

## 常用命令

### 后端
```bash
# 启动后端服务（自动执行数据库迁移）
python scripts/start_blog.py

# 运行测试
pytest

# 运行单个测试文件
pytest tests/test_api_v1_posts.py -v

# 运行特定测试
pytest tests/test_api_v1_posts.py::test_get_posts -v
```

### 前端
```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

### 全栈开发
```bash
# 同时启动前后端开发服务
python scripts/start_fullstack.py
```

## 架构概览

### 后端结构 (`app/`)

```
app/
├── main.py              # FastAPI 应用入口、中间件、SPA 路由
├── core/
│   ├── config.py        # 配置管理（pydantic-settings）
│   └── db.py            # SQLAlchemy 数据库会话
├── models/              # SQLAlchemy ORM 模型
│   ├── user.py          # 用户模型
│   ├── post.py          # 文章模型（含 post_tags 关联表）
│   ├── category.py      # 分类模型
│   ├── tag.py           # 标签模型
│   └── site_settings.py # 站点设置模型
├── schemas/             # Pydantic 请求/响应模型
├── routes/              # FastAPI 路由（api_v1_*.py）
└── services/            # 业务逻辑层
```

### 前端结构 (`frontend/src/`)

```
src/
├── main.jsx             # 入口文件
├── App.jsx              # 路由定义
├── shared/
│   ├── api/client.js    # API 请求封装
│   ├── auth/            # 认证相关（session 管理、AuthGuard）
│   ├── layout/          # 布局组件（PublicLayout、AdminLayout）
│   ├── markdown/        # Markdown 渲染器
│   └── theme/           # 主题样式（工业极客风格）
├── public/pages/        # 前台页面（首页、文章详情、作者页）
├── admin/pages/         # 后台页面（登录、文章管理、分类标签、作者设置）
└── setup/pages/         # 初始化向导页面
```

## 关键架构决策

### 初始化流程
- 中间件 `check_initialized_middleware` 统一检查初始化状态
- 未初始化时：API 返回 409 错误码 1001，页面请求重定向到 `/setup`
- 内存缓存避免重复查询数据库（`_initialized_cache`）

### 认证机制
- 使用 Session Middleware（starlette）
- 登录接口使用 Form 表单（`application/x-www-form-urlencoded`）
- 前端 `AuthGuard` 组件保护后台路由

### API 响应格式
统一响应结构：
```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

错误码定义见 `docs/api/api-v1-contract.md`。

### 中文 Slug 处理
- 使用 pypinyin 将中文标题转换为拼音 slug

## 测试策略

- 测试使用 SQLite 文件数据库（`test.db`）
- `conftest.py` 提供常用 fixtures：`client`、`initialized_site`、`admin_user`、`logged_in_admin`
- 每个测试前清除初始化缓存（`clear_initialized_cache()`）

## 开发注意事项

- 禁止执行非查询类 git 操作（仅允许 `git status`、`git diff`、`git log` 等）
- 任务完成后释放所有资源（关闭进程、清理测试产物）
- 代码注释和文档使用中文