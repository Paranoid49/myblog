# 开发与运行指南

## 开发前先读

以下改动开始前，建议先看守则文档，避免把局部问题扩成系统复杂度：

- [演进与风险压制守则](./evolution-guardrails.md)
- [变更边界检查清单](./change-review-checklist.md)
- [长期守护规则](./long-term-guardrails.md)
- [关键规则权威来源索引](./rule-authority-index.md)
- [核心回归测试包](./core-regression-suite.md)
- [哲学提分优化执行清单](../planning/project-philosophy-9plus-optimization-todos.md)

## 推荐开发启动方式

### 全栈联调（默认推荐）
开发时统一推荐使用：

```bash
python scripts/start_fullstack.py
```

该脚本负责：

1. 启动后端 `scripts/start_blog.py`
2. 启动前端 `npm run dev`
3. 自动写入前端临时开发环境文件 `.env.development.local`
4. 退出时清理该临时环境文件，并停止前后端进程

可选参数：

```bash
python scripts/start_fullstack.py --backend-port 8000 --frontend-port 5173 --no-browser
```

### 仅后端开发
如果当前只处理后端 API、数据库或脚本逻辑，推荐直接使用：

```bash
python scripts/start_blog.py
```

该脚本负责：

1. 在 PostgreSQL 显式配置场景下按需建库
2. 执行数据库迁移
3. 启动 FastAPI 开发服务

### 不再推荐作为主入口的脚本
- `python scripts/run_dev.py`

`run_dev.py` 仍可作为历史兼容脚本保留，但不再作为日常开发文档主入口，避免与 `start_blog.py` / `start_fullstack.py` 形成重复说法。

---

## 开发端口约定

默认：

- 后端：`127.0.0.1:8000`
- 前端：`127.0.0.1:5173`

自定义端口时：
- 后端端口由 `--backend-port` 决定
- 前端端口由 `--frontend-port` 决定
- 前端通过 `.env.development.local` 读取 `VITE_API_TARGET`

---

## 前端 dev 模式 API 策略

前端开发模式继续使用相对路径：

- `/api/v1/*`
- `/static/*`

前端运行时代码不直接拼接后端 URL。开发时统一由 Vite dev server 代理到后端。

这样可以保证：

- 前端代码与生产环境行为更一致
- 登录、上传、静态资源访问共用同一套相对路径
- 避免前端运行时环境变量注入不稳定带来的联调问题

---

## Vite 代理约定

`frontend/vite.config.js` 中约定：

- `/api` → 代理到后端
- `/static` → 代理到后端

代理目标读取顺序：
1. `frontend/.env.development.local`
2. 进程环境变量 `VITE_API_TARGET`
3. 默认回退到 `http://127.0.0.1:8000`

---

## 静态资源访问约定

### 开发模式
- 前端页面通过 Vite 访问
- 上传图片等静态资源仍使用 `/static/...`
- 实际由 Vite 代理转发到后端

### 生产模式
- FastAPI 托管 `frontend/dist`
- `/assets/*` 与 `/static/*` 由后端统一提供

---

## 浏览器冒烟测试基线

基础验证入口统一推荐：

```bash
pytest
```

如需只跑单个测试文件，再按需细化到具体文件或用例。

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

## 手工验证与临时脚本管理

`project_logs/manual_checks/` 只允许放两类内容：

### 长期保留材料
例如：
- 阶段性验收截图
- 关键手工检查脚本
- 可复盘的历史材料

推荐命名：
- `taskXX_*`

### 临时排查文件
例如：
- `todoX_*`
- `debug_*`
- `*_result.txt`
- 一次性 Playwright 调试脚本

这类文件默认在任务结束后清理。

---

## 清理流程

每次做手工排查或浏览器调试时，任务结束前建议按以下顺序处理：

1. 判断文件是否属于长期保留材料
2. 清理临时脚本
3. 清理结果文件
4. 清理测试数据库、临时截图、调试日志
5. 确认没有残留运行中的测试进程占用产物

---

## 排查建议

如果开发态出现“接口正常但页面联调异常”，优先检查：

1. 是否使用 `python scripts/start_fullstack.py` 启动
2. `frontend/.env.development.local` 是否存在且内容正确
3. 前端 dev server 是否运行在预期端口
4. 后端端口是否与 `VITE_API_TARGET` 一致
5. 是否仍在使用旧的 `frontend/dist` 或旧页面缓存

---

## 不建议的做法

- 不建议在前端运行时代码中直接拼接后端 base URL
- 不建议新增第二套独立 API client 策略区分开发/生产
- 不建议为了联调引入额外反向代理层
- 不建议把简单端口与代理问题升级成更复杂配置系统

---

## 原始来源文档

- `docs/engineering/dev-fullstack-contract.md`
- `docs/engineering/manual-checks-governance.md`
