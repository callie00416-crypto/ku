# Django-Vue3-Admin Docker 一键部署脚本 (Windows PowerShell)
# 使用方法: 在 PowerShell 中运行 .\quick-start.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Django-Vue3-Admin Docker 一键部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否安装
Write-Host "[1/6] 检查 Docker 是否安装..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker 已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker 未安装，请先安装 Docker Desktop" -ForegroundColor Red
    Write-Host "下载地址: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# 检查 Docker Compose 是否安装
Write-Host ""
Write-Host "[2/6] 检查 Docker Compose 是否安装..." -ForegroundColor Yellow
try {
    $composeVersion = docker compose version
    Write-Host "✓ Docker Compose 已安装: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Compose 未安装" -ForegroundColor Red
    exit 1
}

# 检查 .env 文件是否存在
Write-Host ""
Write-Host "[3/6] 检查环境配置文件..." -ForegroundColor Yellow
if (-Not (Test-Path ".env")) {
    Write-Host "创建 .env 配置文件..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
    if (-Not (Test-Path ".env")) {
        # 如果 .env.example 不存在，创建默认的 .env
        @"
MYSQL_PASSWORD=DVADMIN3
REDIS_PASSWORD=DVADMIN3
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "✓ 已创建默认 .env 文件" -ForegroundColor Green
        Write-Host "⚠ 请根据需要修改 .env 文件中的密码" -ForegroundColor Yellow
    } else {
        Write-Host "✓ 已从模板创建 .env 文件" -ForegroundColor Green
    }
} else {
    Write-Host "✓ .env 文件已存在" -ForegroundColor Green
}

# 构建并启动容器
Write-Host ""
Write-Host "[4/6] 构建并启动 Docker 容器..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟时间，请耐心等待..." -ForegroundColor Cyan
docker compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 容器启动成功" -ForegroundColor Green
} else {
    Write-Host "✗ 容器启动失败" -ForegroundColor Red
    exit 1
}

# 等待服务就绪
Write-Host ""
Write-Host "[5/6] 等待服务就绪..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查容器状态
Write-Host ""
Write-Host "容器状态:" -ForegroundColor Cyan
docker compose ps

# 初始化数据库
Write-Host ""
Write-Host "[6/6] 初始化数据库..." -ForegroundColor Yellow
Write-Host "执行数据库迁移..." -ForegroundColor Cyan
docker compose exec -T dvadmin3-django python manage.py migrate

Write-Host "加载初始数据..." -ForegroundColor Cyan
docker compose exec -T dvadmin3-django python manage.py init

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Cyan
Write-Host "  前端页面: http://localhost:8080" -ForegroundColor White
Write-Host "  后端 API: http://localhost:8000" -ForegroundColor White
Write-Host "  Admin后台: http://localhost:8000/admin" -ForegroundColor White
Write-Host ""
Write-Host "默认账号:" -ForegroundColor Cyan
Write-Host "  用户名: admin" -ForegroundColor White
Write-Host "  密码: admin123456" -ForegroundColor White
Write-Host ""
Write-Host "常用命令:" -ForegroundColor Cyan
Write-Host "  查看日志: docker compose logs -f" -ForegroundColor White
Write-Host "  停止服务: docker compose down" -ForegroundColor White
Write-Host "  重启服务: docker compose restart" -ForegroundColor White
Write-Host "  创建超级用户: docker compose exec dvadmin3-django python manage.py createsuperuser" -ForegroundColor White
Write-Host ""