# myblog

轻量、克制、可扩展的个人技术博客系统。

FastAPI + React 前后端分离架构，默认 SQLite 零配置启动，支持 PostgreSQL 扩展。

## 特性

- 前后端分离 — FastAPI RESTful API + React SPA
- 零配置启动 — 默认 SQLite，首次访问自动进入初始化向导
- Markdown 写作 — 支持 GFM 语法
- 分类与标签 — 灵活的内容组织
- 中文友好 — 自动拼音 slug 生成
- 扩展机制 — 数据库 provider、主题 provider、Hook 扩展点
- CI 集成 — GitHub Actions 自动测试、Lint、安全审计

## 技术栈

| 层 | 技术 |
|---|------|
| 后端 | Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic |
| 前端 | React 18, React Router 6, Vite, react-markdown |
| 数据库 | SQLite（默认） / PostgreSQL（可选） |
| 测试 | pytest + coverage（后端）, Vitest（前端） |
| 代码质量 | Ruff（后端）, ESLint + Prettier（前端） |

## 快速启动

### 环境要求

- Python >= 3.11
- Node.js >= 20（前端开发时需要）

### 后端

```bash
# 克隆项目
git clone https://github.com/Paranoid49/myblog.git
cd myblog

# 创建虚拟环境并安装依赖
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 一键启动（自动执行数据库迁移）
python scripts/start_blog.py
```

### 前端（开发模式）

```bash
cd frontend
npm install
npm run dev
```

### 全栈开发

```bash
# 同时启动前后端
python scripts/start_fullstack.py
```

默认地址：`http://127.0.0.1:8000`，首次访问自动进入初始化向导。

## 配置

复制 `.env.example` 为 `.env` 并按需修改：

```bash
cp .env.example .env
```

主要配置项：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | 会话密钥（生产环境必须修改） | `change-me` |
| `ENVIRONMENT` | 运行环境 `development` / `production` | `development` |
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///myblog.db` |

切换 PostgreSQL 只需修改 `DATABASE_URL`，驱动已内置，无需额外安装。

## Docker 部署

### 默认部署（SQLite，零配置）

```bash
# 准备配置
cp .env.example .env
# 编辑 .env，至少设置 SECRET_KEY（>= 32 字符）

# 启动
docker compose up -d --build
```

默认使用 SQLite，数据库文件持久化在 `./data/myblog.db`，访问 `http://localhost` 即可使用。

### 使用 PostgreSQL

在 `.env` 中配置 `DATABASE_URL` 即可覆盖默认 SQLite：

```env
DATABASE_URL=postgresql+psycopg://用户名:密码@数据库地址:5432/数据库名
```

PostgreSQL 需自行准备，项目镜像已内置驱动。然后正常启动：

```bash
docker compose up -d --build
```

## 项目结构

```
myblog/
├── app/                  # 后端应用
│   ├── main.py           # FastAPI 入口、中间件
│   ├── core/             # 配置、数据库
│   ├── models/           # SQLAlchemy 模型
│   ├── schemas/          # Pydantic 请求/响应模型
│   ├── routes/           # API 路由
│   └── services/         # 业务逻辑
├── frontend/             # React 前端
│   └── src/
│       ├── public/       # 前台页面
│       ├── admin/        # 后台管理
│       ├── setup/        # 初始化向导
│       └── shared/       # 公共组件、API 封装、主题
├── tests/                # 后端测试
├── scripts/              # 启动与工具脚本
├── alembic/              # 数据库迁移
├── docs/                 # 项目文档
└── .github/workflows/    # CI 配置
```

## 开发

### 运行测试

```bash
# 后端测试（含覆盖率，要求 >= 80%）
pytest

# 前端测试
cd frontend && npm run test
```

### 代码检查

```bash
# 后端
ruff check app/ tests/
ruff format --check app/ tests/

# 前端
cd frontend && npm run lint
```

### 构建前端生产版本

```bash
cd frontend && npm run build
```

构建产物输出到 `frontend/dist/`，后端自动托管为 SPA 静态文件。

## 文档

详细的架构说明、API 契约、扩展开发、工程规范等内容请参见 [docs/README.md](docs/README.md)。

## 许可证

[MIT License](LICENSE)
