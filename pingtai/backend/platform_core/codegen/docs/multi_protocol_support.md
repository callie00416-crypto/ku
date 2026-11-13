# 代码生成系统扩展 - 多协议支持

## 📋 扩展概述

本次扩展为代码生成系统添加了多协议支持，使其能够生成SCPI、Modbus等多种协议的设备驱动。

## 🎯 扩展目标

1. **支持多种协议** - SCPI、Modbus RTU、Modbus TCP等
2. **统一规范格式** - 使用通用的设备规范模板
3. **自动模板选择** - 根据协议类型自动选择合适的模板
4. **保持架构一致** - 生成的代码符合工业平台规范

## 📁 新增文件

### 1. 通用设备规范模板

**文件**: `backend/platform/codegen/examples/generic_device_spec.py`

**内容**:
- 通用设备规范结构
- 支持多种协议配置
- 支持多种通信方式
- 参数范围定义
- 方法定义

**特点**:
```python
GENERIC_DEVICE_SPEC_TEMPLATE = {
    "device_name": "device_name",
    "class_name": "DeviceClass",
    "protocol": {
        "type": "scpi",  # scpi, modbus_rtu, modbus_tcp, custom
    },
    "communication": {
        "type": "usb_visa",  # usb_visa, rs485, tcp, etc.
    },
    "scpi_config": {
        "device_commands": {},
        "channel_commands": {},
        "response_parser": {}
    },
    "modbus_config": {
        "registers": {},
        "channel_registers": {}
    },
    "parameters": {},
    "methods": []
}
```

### 2. DG811设备规范

**文件**: `backend/platform/codegen/examples/dg811_spec.py`

**内容**:
- DG811的完整设备规范
- 基于通用模板
- SCPI协议配置
- USB VISA通信配置

**关键配置**:
```python
DG811_SPEC = {
    "device_name": "waveform_generator",
    "class_name": "DG811WaveformGenerator",
    "protocol": {
        "type": "scpi"
    },
    "communication": {
        "type": "usb_visa",
        "config": {
            "resource_string": "USB0::0x1AB1::0x0643::DG8A272300397::INSTR",
            "vid": 0x1AB1,
            "pid": 0x0643
        }
    },
    "scpi_config": {
        "channel_commands": {
            "waveform": {
                "set": ":SOUR{channel}:FUNC {waveform}",
                "get": ":SOUR{channel}:FUNC?"
            }
        }
    }
}
```

### 3. SCPI设备模板

**文件**: `backend/platform/codegen/templates/device/device_scpi.py.j2`

**内容**:
- SCPI协议设备驱动模板
- 继承BaseDevice
- 使用SCPIProtocol
- 自动生成所有方法

**生成的代码结构**:
```python
class DG811WaveformGenerator(BaseDevice):
    def __init__(self, driver_id: str, protocol: SCPIProtocol, **kwargs):
        # 初始化
        
    def connect(self) -> bool:
        # 连接设备
        
    def disconnect(self):
        # 断开设备
        
    def set_waveform(self, waveform, frequency, amplitude, offset, phase, channel) -> bool:
        # 设置波形
        
    def output_on(self, channel) -> bool:
        # 打开输出
        
    # ... 其他方法
```

### 4. 更新的代码生成引擎

**文件**: `backend/platform/codegen/generator/engine.py`

**修改内容**:
- 支持根据协议类型选择模板
- 支持SCPI协议
- 改进上下文准备

**关键代码**:
```python
# 根据协议类型选择模板
protocol_type = spec.get('protocol', {}).get('type', 'modbus_rtu')

if protocol_type == 'scpi':
    template_name = 'device/device_scpi.py.j2'
elif self._should_use_enhanced_template(spec):
    template_name = 'device/device_enhanced.py.j2'
else:
    template_name = 'device/device.py.j2'
```

### 5. 使用示例

**文件**: `backend/platform/codegen/examples/usage_example.py`

**内容**:
- 演示如何使用代码生成系统
- 生成DG811驱动
- 显示生成结果

## 🚀 使用方法

### 方法1: 使用示例脚本

```bash
cd backend/platform/codegen/examples
python usage_example.py
```

### 方法2: 直接使用API

```python
from platform.codegen.generator.engine import GeneratorEngine
from platform.codegen.template_engine.engine import TemplateEngine
from platform.codegen.core.config import PlatformConfig
from platform.codegen.examples.dg811_spec import DG811_SPEC

# 创建配置
config = PlatformConfig()
config.base_path = Path(__file__).parent.parent.parent
config.generator.output_dir = 'backend'
config.generator.overwrite = True

# 创建引擎
template_engine = TemplateEngine(config)
generator = GeneratorEngine(config, template_engine)

# 生成代码
result = generator.generate(DG811_SPEC, type='device')
```

## 📊 支持的协议类型

| 协议类型 | 描述 | 模板 | 示例 |
|----------|------|------|------|
| SCPI | 标准命令可编程仪器协议 | device_scpi.py.j2 | DG811波形发生器 |
| Modbus RTU | 串口Modbus | device_enhanced.py.j2 | 博瑞电源 |
| Modbus TCP | 网络Modbus | device_enhanced.py.j2 | 网络设备 |
| Custom | 自定义协议 | device.py.j2 | 自定义设备 |

## 📋 设备规范结构

### 基本信息

```python
{
    "device_name": "device_name",      # 设备名称
    "class_name": "DeviceClass",       # 类名
    "description": "设备描述",         # 描述
    "manufacturer": "制造商",          # 制造商
    "model": "型号",                   # 型号
}
```

### 协议配置

```python
{
    "protocol": {
        "type": "scpi",                # 协议类型
        "version": "",                 # 协议版本
        "description": "协议描述"
    }
}
```

### 通信配置

```python
{
    "communication": {
        "type": "usb_visa",            # 通信类型
        "config": {
            "resource_string": "",     # VISA资源字符串
            "vid": 0x0000,             # USB Vendor ID
            "pid": 0x0000,             # USB Product ID
            "timeout": 10000           # 超时时间
        }
    }
}
```

### SCPI配置

```python
{
    "scpi_config": {
        "device_commands": {
            "get_id": "*IDN?",
            "reset": "*RST"
        },
        "channel_commands": {
            "waveform": {
                "set": ":SOUR{channel}:FUNC {waveform}",
                "get": ":SOUR{channel}:FUNC?"
            }
        },
        "response_parser": {
            "frequency": "float",
            "amplitude": "float"
        }
    }
}
```

### 方法定义

```python
{
    "methods": [
        {
            "name": "set_waveform",
            "description": "设置波形参数",
            "parameters": [
                {"name": "waveform", "type": "str"},
                {"name": "frequency", "type": "float"},
                {"name": "channel", "type": "int", "default": 1}
            ],
            "return_type": "bool"
        }
    ]
}
```

## 🎯 优势

### 1. 统一规范

所有设备使用统一的规范格式，便于维护和扩展。

### 2. 自动生成

根据规范自动生成代码，减少手动编写错误。

### 3. 多协议支持

支持SCPI、Modbus等多种协议，覆盖大部分工业设备。

### 4. 架构一致

生成的代码符合工业平台架构规范。

### 5. 可扩展性

易于添加新的协议类型和通信方式。

## 📝 后续工作

### 1. 完善模板

- 添加更多协议模板
- 优化现有模板
- 添加更多错误处理

### 2. 扩展规范

- 支持更多设备特性
- 添加更多参数类型
- 支持复杂的数据结构

### 3. 测试验证

- 测试生成的代码
- 验证功能完整性
- 性能测试

### 4. 文档完善

- 添加更多示例
- 编写详细文档
- 提供最佳实践

## 🔗 相关文件

- [通用设备规范模板](file:///D:\Users\Administrator\PycharmProjects\django-vue3-admin\backend\platform\codegen\examples\generic_device_spec.py)
- [DG811设备规范](file:///D:\Users\Administrator\PycharmProjects\django-vue3-admin\backend\platform\codegen\examples\dg811_spec.py)
- [SCPI设备模板](file:///D:\Users\Administrator\PycharmProjects\django-vue3-admin\backend\platform\codegen\templates\device\device_scpi.py.j2)
- [代码生成引擎](file:///D:\Users\Administrator\PycharmProjects\django-vue3-admin\backend\platform\codegen\generator\engine.py)
- [使用示例](file:///D:\Users\Administrator\PycharmProjects\django-vue3-admin\backend\platform\codegen\examples\usage_example.py)

## 📞 技术支持

如有问题，请参考：
- 设备规范模板
- 代码生成引擎文档
- 模板引擎文档
- 使用示例代码

---

**版本**: 1.0.0  
**日期**: 2026-06-01  
**作者**: Industrial Automation Platform