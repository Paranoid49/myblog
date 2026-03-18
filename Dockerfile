# 纯后端镜像 — 前端由独立的 frontend/Dockerfile 构建
FROM python:3.12-slim AS backend
WORKDIR /app
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock
COPY . .

FROM backend AS production
RUN mkdir -p /app/data /app/app/static/uploads
RUN useradd -m -r myblog && chown -R myblog:myblog /app
USER myblog
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["python", "scripts/docker_entrypoint.py"]
