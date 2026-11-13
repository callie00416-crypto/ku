# Django-Vue3-Admin 前端环境配置模板

## 开发环境配置 (.env.development)

```env
# 本地环境
ENV = 'development'
VITE_PORT = 8080
VITE_API_URL = 'http://127.0.0.1:8000'
# open 运行 npm run dev 时自动打开浏览器
VITE_OPEN = false

# 是否启用按钮权限
VITE_PM_ENABLED = true
```

## 生产环境配置 (.env.production)

```env
# 线上环境
ENV = 'production'

# 线上环境接口地址
VITE_API_URL = '/api' # docker-compose部署不需要修改，nginx容器自动代理了这个地址

# 是否启用按钮权限
VITE_PM_ENABLED = true
```

## 本地生产环境配置 (.env.local_prod)

```env
# 本地生产环境
ENV = 'local_prod'

# 本地生产环境接口地址
VITE_API_URL = 'http://127.0.0.1:8000'

# 是否启用按钮权限
VITE_PM_ENABLED = true
```

## 配置说明

- `VITE_PORT`: 前端开发服务器端口
- `VITE_API_URL`: 后端 API 地址
- `VITE_OPEN`: 是否自动打开浏览器
- `VITE_PM_ENABLED`: 是否启用按钮权限控制

## 注意事项

1. 根据实际部署环境选择合适的配置文件
2. Docker 部署时使用 `.env.production` 配置
3. 本地开发时使用 `.env.development` 配置
4. 确保 `VITE_API_URL` 指向正确的后端服务地址