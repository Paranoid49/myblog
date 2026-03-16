# 部署指南

## 一、Docker 部署（推荐）

### 1.1 准备环境文件

```bash
cp .env.example .env
# 编辑 .env，配置 SECRET_KEY 和 ENVIRONMENT=production
```

### 1.2 Docker Compose 启动

```bash
docker-compose up -d
```

默认使用 SQLite，数据存储在 `./data/` 目录。

### 1.3 使用 PostgreSQL

修改 `.env`：

```env
DATABASE_URL=postgresql+psycopg://user:pass@db:5432/myblog
```

添加 PostgreSQL 到 `docker-compose.yml`：

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: myblog
    volumes:
      - pgdata:/var/lib/postgresql/data

  myblog:
    build: .
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [db]

volumes:
  pgdata:
```

## 二、手动部署

### 2.1 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2.2 配置环境变量

```bash
cp .env.example .env
# 编辑 SECRET_KEY、DATABASE_URL、ENVIRONMENT=production
```

### 2.3 构建前端

```bash
cd frontend && npm ci && npm run build && cd ..
```

### 2.4 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 三、Nginx 反向代理

```nginx
server {
    listen 80;
    server_name blog.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 10m;
    }
}
```

## 四、systemd 服务

创建 `/etc/systemd/system/myblog.service`：

```ini
[Unit]
Description=myblog
After=network.target

[Service]
User=myblog
WorkingDirectory=/opt/myblog
ExecStart=/opt/myblog/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
EnvironmentFile=/opt/myblog/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable myblog
sudo systemctl start myblog
```

## 五、备份建议

### SQLite
```bash
cp data/myblog.db data/myblog.db.bak
```

### PostgreSQL
```bash
pg_dump -U user myblog > myblog_backup.sql
```

## 六、环境变量说明

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| SECRET_KEY | 是（生产） | change-me | Session 加密密钥 |
| ENVIRONMENT | 否 | development | 运行环境 |
| DATABASE_URL | 否 | sqlite:///myblog.db | 数据库连接 |
| EXTENSION_MODULES | 否 | (空) | 扩展模块路径 |
