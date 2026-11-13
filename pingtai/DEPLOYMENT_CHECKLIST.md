# Django-Vue3-Admin 部署检查清单

## 环境准备检查

- [ ] Python 3.11+ 已安装
- [ ] Node.js 16+ 已安装
- [ ] MySQL 8.0+ 已安装并运行
- [ ] Redis 6.2+ 已安装并运行（可选，但推荐）
- [ ] Git 已安装

## 后端部署检查

- [ ] 项目代码已克隆
- [ ] 虚拟环境已创建并激活
- [ ] 后端依赖已安装 (`pip install -r requirements.txt`)
- [ ] `backend/conf/env.py` 配置文件已创建并正确配置
  - [ ] 数据库连接信息正确
  - [ ] Redis 连接信息正确（如果使用）
  - [ ] DEBUG 模式设置正确
- [ ] 数据库已创建
- [ ] 数据库迁移已完成 (`python manage.py migrate`)
- [ ] 超级用户已创建 (`python manage.py createsuperuser`)
- [ ] 初始数据已加载 (`python manage.py init`)

## 前端部署检查

- [ ] 前端依赖已安装 (`yarn install` 或 `npm install`)
- [ ] `.env.development` 或相应环境配置文件已正确设置
  - [ ] `VITE_API_URL` 指向正确的后端地址
  - [ ] 端口配置正确

## 服务启动检查

- [ ] 后端服务已启动 (`python manage.py runserver`)
- [ ] Celery worker 已启动（如果需要异步任务）
- [ ] 前端服务已启动 (`yarn dev` 或 `npm run dev`)
- [ ] 所有服务无错误日志

## 功能验证检查

- [ ] 前端页面可以正常访问 (http://localhost:8080)
- [ ] 后端 API 可以正常访问 (http://localhost:8000)
- [ ] 可以使用超级用户登录后台
- [ ] 数据库连接正常
- [ ] Redis 连接正常（如果配置了）
- [ ] 文件上传功能正常（如果测试）
- [ ] 用户认证功能正常

## Docker 部署检查（如使用 Docker）

- [ ] Docker 和 Docker Compose 已安装
- [ ] `.env` 文件已创建并配置 MySQL 和 Redis 密码
- [ ] `docker-compose up -d --build` 成功执行
- [ ] 所有容器正常运行 (`docker-compose ps`)
- [ ] 数据库迁移已在容器中执行
- [ ] 超级用户已在容器中创建

## 安全配置检查（生产环境）

- [ ] DEBUG 模式已关闭
- [ ] 默认密码已更改
- [ ] ALLOWED_HOSTS 已正确配置
- [ ] 密钥和敏感信息已从代码中移除
- [ ] HTTPS 已配置（如适用）
- [ ] 防火墙规则已设置

## 性能优化检查（生产环境）

- [ ] 静态文件收集完成 (`python manage.py collectstatic`)
- [ ] Gunicorn 或其他 WSGI 服务器已配置
- [ ] Nginx 已配置（如适用）
- [ ] 数据库索引已优化
- [ ] 缓存策略已配置

## 监控和日志检查

- [ ] 日志文件路径已配置
- [ ] 错误监控已设置（如适用）
- [ ] 性能监控已设置（如适用）
- [ ] 备份策略已制定

## 文档和培训

- [ ] 部署文档已更新
- [ ] 运维手册已准备
- [ ] 相关人员已接受培训