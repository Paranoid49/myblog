# 架构与边界总览

## 核心架构

myblog 当前采用：

- 前端：React SPA
- 后端：FastAPI JSON API + SPA 静态托管
- 数据层：SQLAlchemy + Alembic
- 认证：session / cookie
- 运行形态：默认单体部署

整体遵循：

- 轻量
- 克制
- 可扩展

---

## 后端基础设施边界

### 数据库 provider
位于：
- `app/core/database_provider.py`

当前能力：
- SQLite / PostgreSQL
- 根据 `DATABASE_URL` 选择 provider

当前边界：
- 只承担 URL 解析与 engine 参数差异抽象
- 不承担多租户编排或通用 ORM 适配层

---

### 扩展加载机制
位于：
- `app/core/extension_loader.py`

当前能力：
- 根据配置导入扩展模块
- 启动时执行模块级注册

当前边界：
- 不承担插件生命周期管理
- 不承担插件安装 / 卸载系统
- 不承担权限隔离

---

### 事件总线（发布订阅）
位于：
- `app/core/hook_bus.py`

当前能力：
- 订阅事件
- 触发事件
- 监听器异常隔离

当前边界：
- 只承担单进程内轻量事件分发
- 不承担跨进程消息系统能力
- 不承担持久化、重试、顺序保证

---

## 文章模块边界

位于：
- `app/routes/api_v1_posts.py`
- `app/services/post_service.py`
- `app/services/admin_post_service.py`
- `frontend/src/admin/pages/AdminPostsPage.jsx`

当前能力：
- 前台已发布文章读取
- 后台文章创建、编辑、筛选、发布、转草稿
- Markdown 导入导出
- 与文章编辑直接相关的最小图片插入能力

当前边界：
- 只服务个人博客文章生产闭环
- 优先通过单文件分区、轻量 hook、现有 service 收口复杂度
- 不承担 SEO 平台、协作编辑、版本系统、审核流、大型媒体中心等平台化能力

---

## SiteSettings 边界

位于：
- `app/models/site_settings.py`
- `app/services/setup_service.py`
- `app/routes/api_v1_setup.py`
- `app/routes/api_v1_author.py`

当前能力：
- 保存站点标题
- 保存作者资料最小集合：昵称、简介、邮箱、头像链接、个人链接
- 为 setup 与 author 两条链路提供同一份站点级基础信息

当前边界：
- 只承载站点级基础设置
- 不承担 SEO 配置中心
- 不承担运行时开关中心
- 不承担任意页面杂项配置收纳
- 不因为“先放这里最省事”而继续吸收无关字段

判断标准：
- 若一个字段不直接属于站点基础信息或作者基础资料，默认不进入 `SiteSettings`
- 若边界不清，优先先补文档与测试约束，而不是先加字段

---

## 前端边界

### 主题系统
位于：
- `frontend/src/shared/theme/ThemeProvider.jsx`

当前能力：
- 内置 `light` / `dark`
- localStorage 持久化
- 运行时注册主题 key：`registerTheme(themeKey)`
- 通过 `data-theme` 控制主题

当前边界：
- 只承担主题切换与主题 key 注册
- 不承担主题资源下载
- 不承担复杂主题包系统
- 不承担主题市场能力

---

## 扩展原则

后续如果继续扩展，统一遵守：

1. 先确认真实需求，再扩展能力
2. 优先沿用现有最小入口
3. 不在没有明确收益的情况下增加新的抽象层
4. 保持：
   - 核心极简
   - 扩展开放
   - 行为可预测

---

## 当前明确不做的方向

当前不建议把现有机制升级为：

- 插件平台
- 消息队列替代层
- 重型主题系统
- 多租户数据库编排系统

这些能力如果未来真有需求，应单独评估，而不是提前平台化。

---

## 当前结论

项目当前已经具备：

- 主题扩展入口
- 扩展模块加载入口
- 事件总线（发布订阅）入口
- 数据库 provider 入口

这些能力已经足够支撑当前阶段扩展需求。

下一阶段重点不是继续扩张扩展系统，而是：

- 保持入口稳定
- 保持边界清晰
- 在真实需求驱动下再演进

---

## 原始来源文档

- `docs/architecture/lightweight-extension-boundaries.md`
- `docs/api/extension-api-v1.md`
- `docs/product/product-overview.md`
