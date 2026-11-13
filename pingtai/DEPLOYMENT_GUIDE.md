# Django-Vue3-Admin 新电脑部署指南

本指南将帮助你在新的电脑上重新部署 Django-Vue3-Admin 项目。

## 系统要求

- Python 3.11+
- Node.js 16+ (推荐 18+)
- MySQL 8.0+
- Redis 6.2+
- Git

## 部署步骤

### 1. 克隆项目代码

```bash
git clone <your-repository-url>
cd django-vue3-admin
```

### 2. 后端环境配置

#### 2.1 创建虚拟环境并安装依赖

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

#### 2.2 配置数据库和环境变量

```bash
# 复制环境配置文件
cp conf/env.example.py conf/env.py
```

编辑 `backend/conf/env.py` 文件，根据你的实际环境修改以下配置：

```python
# 数据库配置
DATABASE_ENGINE = "django.db.backends.mysql"
DATABASE_NAME = 'django-vue3-admin'  # 数据库名称
DATABASE_HOST = '127.0.0.1'          # 数据库主机地址
DATABASE_PORT = 3306                 # 数据库端口
DATABASE_USER = "root"               # 数据库用户名
DATABASE_PASSWORD = 'DVADMIN3'       # 数据库密码

# Redis 配置
REDIS_DB = 1
CELERY_BROKER_DB = 3
REDIS_PASSWORD = 'DVADMIN3'
REDIS_HOST = '127.0.0.1'
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:6379'

# 其他配置
DEBUG = True
ENABLE_LOGIN_ANALYSIS_LOG = True
LOGIN_NO_CAPTCHA_AUTH = True
ALLOWED_HOSTS = ["*"]
```

#### 2.3 初始化数据库

确保 MySQL 服务正在运行，然后执行：

```bash
# 创建数据库（如果不存在）
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS \`django-vue3-admin\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 加载初始数据
python manage.py init
```

### 3. 前端环境配置

#### 3.1 安装前端依赖

```bash
# 进入前端目录
cd ../web

# 安装依赖（推荐使用 yarn）
yarn install

# 或者使用 npm
npm install

# 或者使用 pnpm
pnpm install
```

#### 3.2 配置前端环境变量

检查 `.env.development` 文件，确保 API 地址正确：

```env
# 本地环境
ENV = 'development'
VITE_PORT = 8080
VITE_API_URL = 'http://127.0.0.1:8000'
VITE_OPEN = false
VITE_PM_ENABLED = true
```

### 4. 启动服务

#### 4.1 启动后端服务

```bash
# 在后端目录 (backend) 中，确保虚拟环境已激活
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 启动 Django 开发服务器
python manage.py runserver 0.0.0.0:8000
```

#### 4.2 启动 Celery 异步任务（可选）

如果需要处理异步任务，在另一个终端窗口中：

```bash
# 在后端目录 (backend) 中，确保虚拟环境已激活
cd backend
venv\Scripts\activate  # Windows

# 启动 Celery worker
celery -A application worker -l info

# 启动 Celery beat（定时任务）
celery -A application beat -l info
```

#### 4.3 启动前端服务

```bash
# 在前端目录 (web) 中
cd web

# 启动开发服务器
yarn dev
# 或
npm run dev
# 或
pnpm dev
```

### 5. 访问应用

- 前端地址: http://localhost:8080
- 后端 API: http://localhost:8000
- Admin 后台: http://localhost:8000/admin

## Docker 部署方式（可选）

如果你更喜欢使用 Docker，可以按照以下步骤操作：

### 1. 准备环境变量

在项目根目录创建 `.env` 文件：

```env
MYSQL_PASSWORD=DVADMIN3
REDIS_PASSWORD=DVADMIN3
```

### 2. 构建并启动容器

```bash
docker-compose up -d --build
```

### 3. 初始化数据库

```bash
docker-compose exec dvadmin3-django python manage.py migrate
docker-compose exec dvadmin3-django python manage.py createsuperuser
docker-compose exec dvadmin3-django python manage.py init
```

### 4. 访问应用

- 前端地址: http://localhost:8080
- 后端 API: http://localhost:8000

## 常见问题

### 1. MySQL 连接失败

- 确保 MySQL 服务正在运行
- 检查 `conf/env.py` 中的数据库配置是否正确
- 确认数据库用户有足够权限

### 2. Redis 连接失败

- 确保 Redis 服务正在运行
- 检查 `conf/env.py` 中的 Redis 配置是否正确

### 3. 前端无法连接后端

- 检查 `.env.development` 中的 `VITE_API_URL` 是否指向正确的后端地址
- 确保后端服务正在运行且端口正确

### 4. 依赖安装失败

- 确保使用了正确的 Python 和 Node.js 版本
- 尝试清除缓存后重新安装：
  ```bash
  # Python
  pip cache purge
  pip install -r requirements.txt
  
  # Node.js
  rm -rf node_modules yarn.lock
  yarn install
  ```

## 注意事项

1. **安全提醒**: 生产环境中请务必修改默认密码和密钥
2. **备份数据**: 定期备份数据库和重要文件
3. **日志监控**: 定期检查 `logs/backend/` 目录下的日志文件
4. **更新依赖**: 定期更新项目依赖以修复安全漏洞

## 技术支持

如遇到问题，请参考：
- 项目文档: [README.md](../README.md)
- Issue 跟踪: [GitHub Issues](https://github.com/your-repo/issues)