# 开发态前后端联调约定

日期：2026-03-12

## 目标

统一 myblog 在开发模式下的前后端联调方式，减少“代码正确但本地联调行为不一致”的问题。

遵循原则：

- 轻量：尽量沿用现有启动脚本与 Vite 代理能力
- 克制：不引入额外 dev server、中间层或复杂环境管理方案
- 可扩展：保留通过端口与环境文件调整后端目标的能力

---

## 推荐启动入口

### 全栈联调（默认推荐）
开发时推荐统一使用：

```bash
python scripts/start_fullstack.py
```

该脚本会：

1. 启动后端：`scripts/start_blog.py`
2. 启动前端：`frontend` 下的 `npm run dev`
3. 自动为前端写入临时开发环境文件：`.env.development.local`
4. 在退出时自动停止前后端进程，并清理该临时环境文件

可选参数：

```bash
python scripts/start_fullstack.py --backend-port 8000 --frontend-port 5173 --no-browser
```

### 仅后端开发
若当前只处理后端 API、数据库迁移或启动链路，推荐直接使用：

```bash
python scripts/start_blog.py
```

### 历史兼容脚本说明
- `python scripts/run_dev.py` 仍保留为兼容脚本
- 但不再作为主文档入口推荐，避免形成与 `start_blog.py` / `start_fullstack.py` 的重复说明

---

## 端口约定

默认端口：

- 后端：`127.0.0.1:8000`
- 前端：`127.0.0.1:5173`

当通过 `start_fullstack.py` 自定义端口时：

- 后端端口由 `--backend-port` 决定
- 前端端口由 `--frontend-port` 决定
- 前端会通过临时 `.env.development.local` 读取后端地址

---

## 前端 dev 模式 API 请求策略

前端代码在开发模式下继续使用**相对路径**请求：

- `/api/v1/*`
- `/static/*`

不在前端运行时代码中直接拼接后端 URL。

统一由 Vite dev server 代理到后端服务。

这样可以保证：

- 前端代码与生产环境行为更一致
- 登录、上传、静态资源访问都复用同一套相对路径
- 避免前端运行时环境变量注入不稳定导致的联调问题

---

## Vite 代理约定

`frontend/vite.config.js` 中约定：

- `/api` → 代理到后端
- `/static` → 代理到后端

代理目标读取顺序：

1. `frontend/.env.development.local` 中的 `VITE_API_TARGET`
2. 进程环境变量中的 `VITE_API_TARGET`
3. 默认回退到 `http://127.0.0.1:8000`

因此：

- 推荐通过 `start_fullstack.py` 自动生成 `.env.development.local`
- 不建议手动在前端代码中拼接后端地址

---

## 静态资源访问约定

开发模式下：

- 前端页面通过 Vite 访问
- 后端静态资源（如上传图片）通过 `/static/...` 相对路径访问
- 实际仍由 Vite 代理转发到后端

生产模式下：

- FastAPI 直接托管 `frontend/dist`
- `/assets/*` 与 `/static/*` 都由后端统一提供

---

## 已知实践要求

### 1. 登录相关页面
- 登录页通过 `/api/v1/auth/login` 登录
- 登录成功后写入本地 `myblog_user`
- 公共布局中的“后台”入口根据本地登录态决定跳转到：
  - 已登录：`/admin`
  - 未登录：`/admin/login`

### 2. 登录页回跳
- 已登录用户访问 `/admin/login` 时，应直接跳转到 `/admin`

---

## 排查建议

如果开发态出现“接口正常但页面联调异常”，优先检查：

1. 是否使用 `python scripts/start_fullstack.py` 启动
2. `frontend/.env.development.local` 是否存在且内容正确
3. 前端 dev server 是否真的运行在预期端口
4. 后端端口是否与 `VITE_API_TARGET` 一致
5. 是否使用了旧的 `frontend/dist` 或旧页面缓存

---

## 浏览器冒烟测试基线

当前建议优先保留和复用的关键浏览器路径包括：

- 登录
- 登录后访问 `/admin/login` 自动回跳
- 登录后从首页点击“后台”进入 `/admin`
- 新建文章
- 发布文章
- 前台查看文章详情
- 登出后首页“后台”入口恢复为 `/admin/login`

执行这类测试时：

- 优先通过 `scripts/with_server.py` 管理前后端生命周期
- 优先使用隔离测试数据库
- 完成后按 `docs/manual-checks-governance.md` 清理临时测试产物

---

## 不建议的做法

- 不建议在前端运行时代码中直接拼接后端 base URL
- 不建议新增第二套独立 API client 策略区分开发/生产
- 不建议为了联调引入额外反向代理层
- 不建议把简单端口与代理问题升级成更复杂配置系统
