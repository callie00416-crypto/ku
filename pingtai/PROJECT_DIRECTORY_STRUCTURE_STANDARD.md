# 项目目录结构规范（永久冻结）

## 🎯 核心原则

**Backend目录只包含代码文件，所有文档和日志统一到根目录管理**

## 📚 Docs目录规范

### 统一文档目录结构
```
docs/                          # 统一文档目录（根目录）
├── backend/                   # 后端文档
│   ├── BACKEND_CLEANUP_SUMMARY.md
│   ├── BACKEND_DEVELOPMENT_REPORT.md
│   ├── ROOT_PYTHON_FILES_CLEANUP_SUMMARY.md
│   ├── TEST_ISSUES_FIX_REPORT.md
│   ├── power_amplifier_debug_guide.md
│   ├── serial_debugging_experience.md
│   └── serial_port_management.md
├── drivers/                   # 设备文档
│   └── device/
│       ├── Power Amplifier/
│       ├── PowerSupply/
│       └── RIGOL DG811/
├── auto-permission-scan.md
├── codegen-platform.md
├── device-addition-specification.md
├── device-generator-usage.md
├── i18n-guide.md
└── 最终优化版架构｜极简图 + 端口 + 通信规则 + 性能说明.docx
```

### 文档路径规范

| 用途 | 正确路径 | ❌ 禁止路径 |
|------|----------|-------------|
| 后端文档 | `docs/backend/` | `backend/docs/` |
| 设备文档 | `docs/drivers/device/` | `backend/docs/drivers/device/` |
| 代码生成文档 | `docs/drivers/device/{device_name}/` | `backend/docs/drivers/device/{device_name}/` |

## 📝 Logs目录规范

### 统一日志目录结构
```
logs/                          # 统一日志目录（根目录）
├── backend/                   # 后端日志
│   ├── __init__.py
│   ├── error.log
│   └── server.log
├── device/                    # 设备日志
│   └── device.log
├── engine/                    # 引擎日志
│   └── engine.log
├── errors/                    # 错误日志
│   └── error.log
├── runtime/                   # 运行时日志
│   └── runtime.log
└── system/                    # 系统日志
    └── server.log
```

### 日志路径规范

| 用途 | 正确路径 | ❌ 禁止路径 |
|------|----------|-------------|
| 后端日志 | `logs/backend/` | `backend/logs/` |
| 设备日志 | `logs/device/` | `backend/logs/device/` |
| 系统日志 | `logs/system/` | `backend/logs/system/` |
| 错误日志 | `logs/errors/` | `backend/logs/errors/` |

## 🚫 禁止的路径

### 永久禁止
- ❌ `backend/docs/` - 禁止使用
- ❌ `backend/logs/` - 禁止使用

### 违反规范的示例
```python
# ❌ 错误示例
'backend/docs/drivers/device/{device_name}'
'backend/logs/error.log'
'backend/docs/serial_debugging_experience.md'

# ✅ 正确示例
'docs/drivers/device/{device_name}'
'logs/backend/error.log'
'docs/backend/serial_debugging_experience.md'
```

## ✅ 正确的路径

### 文档路径
- ✅ `docs/backend/` - 后端文档
- ✅ `docs/drivers/device/` - 设备文档
- ✅ `docs/drivers/device/{device_name}/` - 具体设备文档

### 日志路径
- ✅ `logs/backend/` - 后端日志
- ✅ `logs/system/` - 系统日志
- ✅ `logs/errors/` - 错误日志
- ✅ `logs/device/` - 设备日志
- ✅ `logs/engine/` - 引擎日志
- ✅ `logs/runtime/` - 运行时日志

## 🔧 Django配置规范

### settings.py日志配置
```python
# ✅ 正确配置
SERVER_LOGS_FILE = os.path.join(BASE_DIR.parent, "logs", "system", "server.log")
ERROR_LOGS_FILE = os.path.join(BASE_DIR.parent, "logs", "errors", "error.log")

# ❌ 错误配置
SERVER_LOGS_FILE = os.path.join(BASE_DIR, "logs", "server.log")
ERROR_LOGS_FILE = os.path.join(BASE_DIR, "logs", "error.log")
```

## 📋 代码生成规范

### 设备代码生成时的文档路径
```python
# ✅ 正确配置
DEVICE_DIRECTORIES = [
    'backend/projects/encoder_test/drivers/device/{device_name}',
    'backend/projects/encoder_test/adapters',
    'backend/tests/device',
    'docs/drivers/device/{device_name}'  # 正确路径
]

# ❌ 错误配置
DEVICE_DIRECTORIES = [
    'backend/projects/encoder_test/drivers/device/{device_name}',
    'backend/projects/encoder_test/adapters',
    'backend/tests/device',
    'backend/docs/drivers/device/{device_name}'  # 错误路径
]
```

### 生成文档时的路径
```python
# ✅ 正确配置
self.output_dir / f'docs/drivers/device/{device_name}/config.json'
self.output_dir / f'docs/drivers/device/{device_name}/README.md'

# ❌ 错误配置
self.output_dir / f'backend/docs/drivers/device/{device_name}/config.json'
self.output_dir / f'backend/docs/drivers/device/{device_name}/README.md'
```

## 🎯 Backend目录规范

### Backend目录只包含代码文件
```
backend/                       # 后端代码目录（纯代码）
├── application/               # Django应用配置
├── archive/                   # 归档文件
├── conf/                      # 配置文件
├── deployment/                # 部署文件
├── dvadmin/                   # Django Admin系统
├── examples/                  # 示例
├── locale/                    # 本地化
├── platform/                  # 平台代码
├── projects/                  # 项目代码
├── scripts/                   # 脚本
├── shared/                    # 共享代码
├── .coverage                  # 测试覆盖率
├── .coveragerc                # 测试覆盖率配置
├── .gitignore                 # Git忽略
└── manage.py                  # Django管理
```

### Backend目录禁止包含
- ❌ docs/ 目录
- ❌ logs/ 目录
- ❌ .md 文档文件
- ❌ .log 日志文件

## 📝 文档引用规范

### 在代码中引用文档
```python
# ✅ 正确引用
docs/backend/serial_debugging_experience.md
docs/drivers/device/Power Amplifier/ATA-101B使用说明书V2.0.pdf

# ❌ 错误引用
backend/docs/serial_debugging_experience.md
backend/docs/drivers/device/Power Amplifier/ATA-101B使用说明书V2.0.pdf
```

### 在README中引用文档
```markdown
# ✅ 正确引用
- **串口调试经验**: `docs/backend/serial_debugging_experience.md` ⚠️ 重要！
- **设备手册**: `docs/drivers/device/Power Amplifier/ATA-101B使用说明书V2.0.pdf`

# ❌ 错误引用
- **串口调试经验**: `backend/docs/serial_debugging_experience.md` ⚠️ 重要！
- **设备手册**: `backend/docs/drivers/device/Power Amplifier/ATA-101B使用说明书V2.0.pdf`
```

## 🔍 检查清单

### 新增文档时
- [ ] 确认文档类型（后端文档/设备文档/其他文档）
- [ ] 选择正确的目标目录
- [ ] 后端文档 → `docs/backend/`
- [ ] 设备文档 → `docs/drivers/device/{device_name}/`
- [ ] 更新相关引用

### 新增日志时
- [ ] 确认日志类型（后端日志/系统日志/设备日志等）
- [ ] 选择正确的目标目录
- [ ] 后端日志 → `logs/backend/`
- [ ] 系统日志 → `logs/system/`
- [ ] 更新Django配置（如需要）

### 更新代码时
- [ ] 检查是否有路径引用
- [ ] 确认路径符合规范
- [ ] 更新为正确的路径
- [ ] 测试路径是否正确

## 🎓 维护原则

### 1. 永久遵守
- 所有新操作必须遵守此规范
- 不得创建违反规范的路径
- 不得使用禁止的路径

### 2. 定期检查
- 定期检查是否有违反规范的路径
- 搜索 `backend/docs/` 和 `backend/logs/`
- 及时修正违规路径

### 3. 文档同步
- 新增文档时同步更新此规范
- 重大变更时更新此规范
- 保持规范的完整性

### 4. 团队协作
- 团队成员必须了解此规范
- 新成员必须学习此规范
- 代码审查时检查路径规范

## 📞 违规处理

### 发现违规路径时
1. 立即停止使用违规路径
2. 将文件移动到正确的目录
3. 更新所有相关引用
4. 验证修改的正确性
5. 记录违规情况

### 预防措施
1. 在代码中搜索禁止的路径
2. 在文档中检查路径引用
3. 在配置文件中验证路径
4. 在代码审查时检查路径

## 🎯 总结

**核心原则**: Backend目录只包含代码文件，所有文档和日志统一到根目录管理

**记住两点**:
1. ❌ 永远不要使用 `backend/docs/` 和 `backend/logs/`
2. ✅ 永远使用 `docs/backend/` 和 `logs/backend/`

**验证方法**:
- 搜索 `backend/docs/` 应该只出现在历史文档中
- 搜索 `backend/logs/` 应该只出现在历史文档中
- Backend目录不应该有 docs/ 和 logs/ 目录

---

**规范版本**: V1.0  
**规范状态**: 永久冻结  
**创建日期**: 2026-06-02  
**适用范围**: 全项目