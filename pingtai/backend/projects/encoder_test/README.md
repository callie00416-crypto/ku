# 自动化测试模块使用说明

## 概述
自动化测试模块已成功集成到系统中，包含以下功能：
- 测试用例管理
- 测试任务管理
- 测试报告管理（待开发前端页面）

## 菜单配置

### 已完成
✅ 数据库菜单已初始化
✅ 按钮权限已配置
✅ 超级管理员角色已分配权限

### 菜单结构
```
自动化测试 (父级目录)
├── 测试用例 (/encoder-test/test-case)
│   ├── 查询
│   ├── 新增
│   ├── 编辑
│   ├── 删除
│   └── 执行
└── 测试任务 (/encoder-test/test-task)
    ├── 查询
    ├── 新增
    ├── 编辑
    ├── 删除
    ├── 启动
    └── 停止
```

## 如何查看菜单

### 方法1：刷新浏览器（推荐）
1. 确保前端开发服务器正在运行：`http://localhost:8080`
2. 按 `Ctrl + F5` 强制刷新浏览器缓存
3. 在左侧菜单栏中应该能看到"自动化测试"模块

### 方法2：重新登录
1. 退出当前登录
2. 重新登录系统
3. 菜单会自动加载最新的配置

### 方法3：清除缓存
如果上述方法都不行，可以：
1. 打开浏览器开发者工具（F12）
2. 切换到 Application/Storage 标签
3. 清除 Local Storage 和 Session Storage
4. 刷新页面并重新登录

## 测试用例扫描与同步

### 方式1：应用启动时自动扫描（推荐）

系统会在启动时自动检测并扫描测试用例：
- 如果数据库中没有测试用例，会自动扫描并添加
- 扫描过程在后台进行，不影响应用启动
- 查看控制台输出可以看到扫描结果

### 方式2：前端手动触发扫描

在测试用例页面点击 **“扫描用例”** 按钮：
1. 访问 http://localhost:8080/#/encoder-test/test-case
2. 点击绿色的“扫描用例”按钮
3. 系统会立即扫描代码并同步到数据库
4. 扫描完成后自动刷新列表

### 方式3：命令行扫描

系统支持从代码中自动扫描测试用例并同步到数据库。

**扫描命令：**
```bash
cd backend
python manage.py scan_test_cases
```

**仅预览（不同步）：**
```bash
python manage.py scan_test_cases --dry-run
```

**扫描原理：**
1. 扫描 `core/testcases/suites/` 目录下的所有 `test_*.py` 文件
2. 解析 `@test_case` 装饰器提取用例元数据
3. 将用例信息同步到 `encoder_test_case` 表
4. 自动禁用已删除的用例

**当前发现的用例：**
- CASE-001: 编码器零点精度测试
- CASE-002: 编码器全角度精度测试

## 访问路径

### 直接访问URL
- 测试用例：`http://localhost:8080/#/encoder-test/test-case`
- 测试任务：`http://localhost:8080/#/encoder-test/test-task`

### 后端API
- 测试用例列表：`http://localhost:8000/api/encoder_test/test-cases/`
- 测试任务列表：`http://localhost:8000/api/encoder_test/test-tasks/`
- 测试报告列表：`http://localhost:8000/api/encoder_test/test-reports/`

## 常见问题

### Q1: 菜单不显示？
**A:** 
1. 确认已执行菜单初始化命令：`python manage.py init_encoder_test_menu`
2. 检查当前用户是否有"管理员"角色
3. 清除浏览器缓存并刷新

### Q2: 点击菜单后页面空白？
**A:** 
1. 检查前端控制台是否有错误
2. 确认前端文件路径正确：
   - `web/src/views/encoder_test/testCase.vue`
   - `web/src/views/encoder_test/testTask.vue`
3. 检查路由配置是否正确

### Q3: API请求失败？
**A:** 
1. 确认后端服务正在运行：`http://localhost:8000`
2. 检查URL配置：`backend/application/urls.py` 第105行
3. 查看后端日志是否有错误信息

## 重新初始化菜单

如果需要重新初始化菜单（例如修改了菜单配置），可以：

```bash
cd backend
python manage.py init_encoder_test_menu
```

这个命令是安全的，使用 `get_or_create` 方法，不会重复创建数据。

## 下一步

1. **测试功能**：访问测试用例和测试任务页面，验证CRUD功能
2. **开发测试报告页面**：创建 `web/src/views/encoder_test/testReport.vue`
3. **完善权限控制**：为其他角色分配相应的菜单权限
4. **添加国际化**：在菜单管理中补充其他语言的翻译

## 技术支持

如有问题，请检查：
- 前端日志：浏览器控制台（F12）
- 后端日志：`logs/` 目录
- 数据库：确认菜单数据已正确插入到 `dvadmin_system_menu` 表