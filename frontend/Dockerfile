# 纯前端构建镜像 — 仅编译产物，不包含运行时
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
# 启动时将构建产物同步到共享卷，供 nginx 容器读取
CMD ["sh", "-c", "rm -rf /output/* && cp -r /app/dist/. /output/"]
