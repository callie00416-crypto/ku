# 部署说明

## 部署文件说明

### gunicorn_conf.py
Gunicorn WSGI服务器配置文件
- 生产环境Web服务器配置
- 性能优化参数
- 日志配置

### docker_start.sh
Docker容器启动脚本
- 容器化部署
- 环境配置
- 服务启动

## 使用说明

### Gunicorn部署
```bash
gunicorn -c deployment/gunicorn_conf.py application.asgi:application
```

### Docker部署
```bash
chmod +x deployment/docker_start.sh
./deployment/docker_start.sh
```

## 配置说明

### Gunicorn配置
- workers: 工作进程数，默认为CPU数量*2+1
- threads: 每个进程的线程数，默认为3
- bind: 绑定的IP和端口，默认为0.0.0.0:8000
- worker_class: 工作模式，推荐使用uvicorn.workers.UvicornWorker
- timeout: 超时时间，默认为120秒

### Docker配置
- 基于Python 3.11镜像
- 安装依赖
- 启动服务

## 注意事项

1. 生产环境请根据实际情况调整配置参数
2. 确保环境变量正确设置
3. 检查日志输出是否正常
4. 监控服务运行状态