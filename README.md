# myblog

轻量、克制、可扩展的个人技术博客系统。FastAPI + React 前后端分离架构。

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 一键启动（自动执行数据库迁移）
python scripts/start_blog.py

# 前后端同时启动（开发模式）
python scripts/start_fullstack.py
```

默认地址：`http://127.0.0.1:8000`，首次访问自动进入初始化向导。

## 完整文档

详细的架构说明、API 契约、扩展开发、工程规范等内容请参见 [`docs/README.md`](docs/README.md)。
