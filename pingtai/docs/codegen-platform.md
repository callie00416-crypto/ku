# 代码生成平台 - CodeGen Platform

## 📋 平台概述

工业级代码生成平台，支持多种代码生成策略和模板引擎，专为工业自动化测试平台设计。

## 🏗️ 架构设计

```
Platform/
└── CodeGen/
    ├── core/              # 核心平台和配置
    │   ├── platform.py    # 平台核心类
    │   └── config.py      # 配置管理
    ├── dsl/               # 领域特定语言
    │   └── parser.py      # DSL解析器
    ├── template_engine/   # 模板引擎
    │   ├── engine.py      # 模板引擎基类
    │   └── jinja2_engine.py # Jinja2实现
    ├── generator/         # 代码生成引擎
    │   └── engine.py      # 生成引擎
    ├── scaffold/          # 项目脚手架
    │   └── builder.py     # 脚手架构建器
    ├── ast/               # 代码分析和转换
    │   └── processor.py   # AST处理器
    ├── ai/                # AI代码生成
    │   └── codegen.py     # AI生成器
    ├── templates/         # 代码模板
    │   ├── device/        # 设备模板
    │   └── tests/         # 测试模板
    └── examples/          # 使用示例
        └── usage_examples.py
```

## 🎯 核心功能

### 1. 设备代码生成
- 自动生成设备驱动代码
- 生成设备适配器
- 生成单元测试和集成测试
- 支持多种通信协议

### 2. 项目脚手架
- 创建标准项目结构
- 生成配置文件
- 初始化开发环境

### 3. 代码分析
- 语法验证
- 代码优化
- 复杂度分析
- 代码转换

### 4. AI代码生成
- 智能代码补全
- 自动代码优化
- 提示词工程

## 🚀 快速开始

### 基本使用

```python
from platform.codegen import CodeGenPlatform, CodeGenConfig

# 创建配置
config = CodeGenConfig(
    project_name="my_project",
    debug=True
)

# 创建平台实例
with CodeGenPlatform(config) as platform:
    # 生成设备
    device_spec = {
        'type': 'device',
        'name': 'temperature_sensor',
        'manufacturer': '西门子',
        'model': 'SITRANS T',
        'protocol': 'modbus_rtu',
        'communication': 'rs485',
        'description': '工业温度传感器'
    }
    
    result = platform.generate(device_spec)
    print(f"生成完成: {result['message']}")
```

### 生成项目脚手架

```python
# 创建项目脚手架
project_spec = {
    'type': 'standard',
    'name': 'my_industrial_project',
    'description': '我的工业自动化项目'
}

result = platform.create_scaffold(project_spec)
print(f"脚手架创建完成: {result['message']}")
```

### 代码验证

```python
# 验证代码
test_code = '''
def hello_world():
    print("Hello, World!")
    return True
'''

validation_result = platform.validate_code(test_code)
print(f"验证结果: {validation_result['valid']}")
```

## 📖 详细文档

### 配置说明

```python
config = CodeGenConfig(
    # 基础配置
    project_name="codegen_project",
    version="1.0.0",
    debug=False,
    
    # 模板引擎配置
    template_engine={
        'engine_type': 'jinja2',  # jinja2, mako, string
        'template_dir': 'templates',
        'cache_enabled': True,
        'cache_size': 100
    },
    
    # 生成器配置
    generator={
        'output_dir': 'output',
        'overwrite': False,
        'format_code': True,
        'validate_output': True
    },
    
    # AI配置
    ai={
        'enabled': False,
        'model': 'gpt-4',
        'api_key': None,
        'max_tokens': 2000,
        'temperature': 0.7
    },
    
    # AST配置
    ast={
        'enabled': True,
        'language': 'python',
        'validate_syntax': True,
        'optimize_ast': True
    }
)
```

### 设备生成规范

```python
device_spec = {
    # 必需字段
    'type': 'device',
    'name': 'device_name',           # 设备名称（小写+下划线）
    'manufacturer': '制造商',
    'model': '型号',
    'protocol': 'modbus_rtu',        # 通信协议
    'communication': 'rs485',        # 通信方式
    'description': '设备描述',
    
    # 可选字段
    'parameters': {                   # 设备参数
        'param1': value1,
        'param2': value2
    },
    
    'registers': {                    # 寄存器定义
        'REGISTER_NAME': address,
        'REGISTER_NAME2': address2
    },
    
    'read_registers': ['reg1', 'reg2'],    # 可读寄存器
    'write_registers': ['reg3', 'reg4'],   # 可写寄存器
    'status_registers': ['status_reg'],   # 状态寄存器
    
    'reset_command': 'RESET',             # 重置命令
    'init_commands': ['ENABLE', 'INIT'],  # 初始化命令
    
    'methods': [                       # 设备方法
        {
            'name': 'method_name',
            'description': '方法描述',
            'parameters': [
                {
                    'name': 'param_name',
                    'type': 'param_type',
                    'description': '参数描述',
                    'default': 'default_value'
                }
            ],
            'return_type': 'return_type',
            'return_description': '返回值描述'
        }
    ]
}
```

## 🔧 高级功能

### 1. 自定义模板

创建自定义模板文件：

```jinja2
# templates/custom/device.py.j2
class {{ class_name }}(BaseDevice):
    """{{ description }}"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 自定义初始化逻辑
```

### 2. 插件系统

创建插件：

```python
# my_plugin.py
class Plugin:
    def __init__(self, config, platform):
        self.config = config
        self.platform = platform
    
    def register_hooks(self):
        return {
            'before_generate': self.before_generate,
            'after_generate': self.after_generate
        }
    
    def before_generate(self, spec):
        print(f"开始生成: {spec.get('name')}")
    
    def after_generate(self, spec, result):
        print(f"生成完成: {result['message']}")
```

注册插件：

```python
config = CodeGenConfig(
    plugins=['my_plugin']
)
```

### 3. AI代码生成

启用AI功能：

```python
config = CodeGenConfig(
    ai={
        'enabled': True,
        'model': 'gpt-4',
        'api_key': 'your-api-key',
        'max_tokens': 2000,
        'temperature': 0.7
    }
)

# 使用AI生成代码
code = platform.ai_generate("生成一个温度传感器类")
```

## 📊 平台特性

### 模块化设计
- 各模块独立可测试
- 清晰的接口定义
- 支持模块热插拔

### 插件化架构
- 支持自定义插件
- 钩子机制
- 事件驱动

### 配置驱动
- 灵活的配置系统
- 支持配置文件
- 运行时配置更新

### 类型安全
- 完整的类型提示
- 静态类型检查
- IDE友好

### 错误处理
- 完善的异常机制
- 详细的错误信息
- 优雅的降级处理

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest platform/codegen/tests/

# 运行特定测试
pytest platform/codegen/tests/test_generator.py

# 运行示例
python platform/codegen/examples/usage_examples.py
```

### 测试覆盖

- 单元测试
- 集成测试
- 全链路测试
- 性能测试

## 📈 性能优化

### 模板缓存
- 启用模板缓存
- LRU缓存策略
- 可配置缓存大小

### 增量生成
- 只生成变更的文件
- 智能文件检测
- 避免重复生成

### 并行处理
- 支持并行生成
- 异步IO操作
- 批量处理优化

## 🛠️ 维护和迭代

### 版本管理
- 语义化版本
- 变更日志
- 兼容性保证

### 文档维护
- API文档
- 使用指南
- 最佳实践

### 持续集成
- 自动化测试
- 代码质量检查
- 自动部署

## 🤝 贡献指南

### 开发流程
1. Fork项目
2. 创建功能分支
3. 提交变更
4. 推送到分支
5. 创建Pull Request

### 代码规范
- 遵循PEP 8
- 添加类型提示
- 编写文档字符串
- 添加单元测试

## 📞 获取帮助

- 文档: `docs/codegen/`
- 示例: `platform/codegen/examples/`
- 问题反馈: 通过项目Issue系统

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有贡献者的支持！