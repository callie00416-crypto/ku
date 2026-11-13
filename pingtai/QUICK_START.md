# Django-Vue3-Admin Docker 一键部署快速指南

## 🚀 超简单三步部署

### 前提条件

只需安装 **Docker Desktop**：
- 下载地址：https://www.docker.com/products/docker-desktop
- 安装后重启电脑

### 部署步骤

#### 方法一：一键脚本（推荐）⭐

1. **打开 PowerShell**，进入项目目录
   ```powershell
   cd D:\Users\Administrator\PycharmProjects\django-vue3-admin
   ```

2. **运行一键部署脚本**
   ```powershell
   .\quick-start.ps1
   ```

3. **等待完成**，浏览器访问 http://localhost:8080

**就这么简单！** 🎉

---

#### 方法二：手动命令

如果不想用脚本，也可以手动执行以下命令：

```powershell
# 1. 创建 .env 文件（首次部署）
Copy-Item .env.example .env

# 2. 启动所有服务
docker compose up -d --build

# 3. 等待 10 秒让服务启动
Start-Sleep -Seconds 10

# 4. 初始化数据库
docker compose exec dvadmin3-django python manage.py migrate
docker compose exec dvadmin3-django python manage.py init

# 5. 创建超级用户（可选）
docker compose exec dvadmin3-django python manage.py createsuperuser
```

---

## 📋 访问信息

部署完成后，可以访问：

- **前端页面**: http://localhost:8080
- **后端 API**: http://localhost:8000
- **Admin 后台**: http://localhost:8000/admin

**默认账号**（如已加载初始数据）：
- 用户名: `admin`
- 密码: `admin123456`

---

## 🔧 常用命令

```powershell
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f dvadmin3-django
docker compose logs -f dvadmin3-web

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 重新构建并启动
docker compose up -d --build

# 进入容器内部
docker compose exec dvadmin3-django bash

# 创建超级用户
docker compose exec dvadmin3-django python manage.py createsuperuser

# 完全清理（删除数据和容器）
docker compose down -v
```

---

## ⚙️ 修改配置

### 修改数据库/Redis 密码

编辑 `.env` 文件：
```env
MYSQL_PASSWORD=你的新密码
REDIS_PASSWORD=你的新密码
```

然后重新构建：
```powershell
docker compose down
docker compose up -d --build
```

### 修改端口

编辑 `docker-compose.yml` 文件中的端口映射：
```yaml
ports:
  - "8080:8080"  # 改为 "你的端口:8080"
```

---

## ❓ 常见问题

### 1. Docker 启动失败？

- 确保 Docker Desktop 正在运行
- 检查是否以管理员权限运行 PowerShell

### 2. 端口被占用？

修改 `docker-compose.yml` 中的端口映射，例如：
```yaml
ports:
  - "8081:8080"  # 前端改用 8081 端口
  - "8001:8000"  # 后端改用 8001 端口
```

### 3. 如何重置数据库？

```powershell
# 警告：这会删除所有数据！
docker compose down -v
docker compose up -d --build
docker compose exec dvadmin3-django python manage.py migrate
docker compose exec dvadmin3-django python manage.py init
```

### 4. 容器正常运行但无法访问？

等待 1-2 分钟，服务可能需要时间启动。查看日志：
```powershell
docker compose logs -f
```

### 5. 如何更新代码？

```powershell
# 拉取最新代码
git pull

# 重新构建并启动
docker compose up -d --build
```

---

## 📦 容器说明

| 容器名 | 说明 | 端口 |
|--------|------|------|
| dvadmin3-web | 前端 (Nginx) | 8080 |
| dvadmin3-django | 后端 (Django) | 8000 |
| dvadmin3-mysql | 数据库 (MySQL 8.0) | 3306 |
| dvadmin3-redis | 缓存 (Redis) | 6379 |
| dvadmin3-celery | 异步任务 (Celery) | - |

---

## 💾 数据持久化

以下数据会持久化保存在本地：

- MySQL 数据: `./docker_env/mysql/data`
- Redis 数据: `./docker_env/redis/data`
- 媒体文件: `./backend/media`
- 日志文件: `./logs/log`

即使删除容器，这些数据也不会丢失。

---

## 🎯 下一步

部署成功后：

1. 访问 http://localhost:8080 登录系统
2. 阅读完整文档了解功能特性
3. 根据需求修改配置
4. 开始开发你的应用

祝你使用愉快！🚀