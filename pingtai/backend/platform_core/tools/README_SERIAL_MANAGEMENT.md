# 工业设备串口管理系统

## 🎯 系统概述

工业自动化测试平台需要管理大量硬件设备，每个设备都通过串口连接。本系统提供了一套完整的设备串口管理解决方案，包括：

1. **串口资源管理** - 统一管理串口资源，避免冲突
2. **设备配置管理** - 集中管理所有设备的串口配置
3. **自动检测功能** - 自动识别设备连接的串口
4. **状态监控** - 实时监控设备连接状态
5. **命令行工具** - 提供便捷的管理工具

## 📁 系统架构

```
backend/
├── shared/drivers/comm/
│   ├── serial_port_manager.py              # 串口资源管理器
│   ├── device_serial_config_manager.py     # 设备配置管理器
│   └── rs485_comm.py                       # RS485通信
├── conf/
│   └── device_serial_config.json           # 设备配置文件
└── platform/tools/
    └── serial_device_manager.py            # 命令行管理工具
```

## 🔧 核心组件

### 1. 串口资源管理器 (SerialPortManager)

**职责**：
- 管理串口资源的分配和释放
- 检测串口占用情况
- 自动清理占用进程
- 提供串口资源池

**主要功能**：
```python
from shared.drivers.comm.serial_port_manager import get_serial_port_manager

# 获取管理器
manager = get_serial_port_manager()

# 列出可用串口
ports = manager.list_available_ports()

# 检查串口状态
status = manager.check_port_status('COM1')

# 获取串口资源
success = manager.acquire_port('COM1', owner='test', timeout=10.0)

# 释放串口资源
manager.release_port('COM1')

# 重置串口
success = manager.reset_port('COM1')
```

### 2. 设备配置管理器 (DeviceSerialConfigManager)

**职责**：
- 管理设备的串口配置
- 自动检测设备串口
- 提供设备串口映射
- 支持设备识别和验证

**主要功能**：
```python
from shared.drivers.comm.device_serial_config_manager import get_device_config_manager

# 获取管理器
manager = get_device_config_manager()

# 加载配置文件
manager.load_config_file('backend/conf/device_serial_config.json')

# 获取设备配置
config = manager.get_device_config('power_amplifier')

# 自动检测设备串口
port = manager.auto_detect_device_port('power_amplifier')

# 验证设备连接
success = manager.verify_device_connection('power_amplifier')

# 获取所有设备状态
status = manager.get_all_devices_status()
```

### 3. 命令行管理工具 (serial_device_manager.py)

**功能**：
- 列出所有可用串口
- 检查设备连接状态
- 自动分配串口
- 管理设备配置
- 验证设备连接

## 🚀 使用方法

### 方法1: 使用命令行工具

#### 列出所有可用串口

```bash
cd backend
python platform/tools/serial_device_manager.py list-ports
```

**输出示例**：
```
======================================================================
可用串口列表
======================================================================

找到 2 个可用串口:

1. COM1            - ✓ 空闲
2. COM3            - ✓ 空闲
```

#### 检查所有设备状态

```bash
cd backend
python platform/tools/serial_device_manager.py check-status
```

**输出示例**：
```
======================================================================
设备状态检查
======================================================================

已加载配置文件: D:\...\backend\conf\device_serial_config.json

找到 5 个设备配置:

1. ATA-101B功率放大器 (power_amplifier)
   设备类型: power_amplifier
   串口号:   COM1
   波特率:   9600
   端口状态: ✓ 空闲
   连接状态: ✓ 连接正常
   自动检测: 是
   描述:     用于编码器测试的功率放大器
```

#### 检查特定设备状态

```bash
cd backend
python platform/tools/serial_device_manager.py check-status --device power_amplifier
```

#### 自动检测设备串口

```bash
cd backend
python platform/tools/serial_device_manager.py auto-detect
```

**功能**：
- 扫描所有可用串口
- 尝试连接每个串口
- 验证设备响应
- 自动更新配置

#### 添加设备配置

```bash
cd backend
python platform/tools/serial_device_manager.py add-device
```

**交互式输入**：
```
请输入设备信息:
设备ID (如: power_amplifier): new_device
设备名称 (如: ATA-101B功率放大器): 新设备
设备类型 (如: power_amplifier): sensor
串口号 (如: COM1): COM6
波特率 (默认: 9600): 115200
数据位 (默认: 8): 8
停止位 (默认: 1): 1
校验位 (none/even/odd, 默认: none): N
流控制 (none/rtscts/xonxoff, 默认: none): none
超时时间ms (默认: 1000): 1000
启用自动检测 (y/n, 默认: y): y
验证命令 (可选，留空跳过): 
验证响应 (可选，留空跳过): 
描述 (可选): 新增设备
```

#### 移除设备配置

```bash
cd backend
python platform/tools/serial_device_manager.py remove-device --device power_amplifier
```

#### 列出所有设备配置

```bash
cd backend
python platform/tools/serial_device_manager.py list-devices
```

#### 重置串口

```bash
cd backend
python platform/tools/serial_device_manager.py reset-port --port COM1
```

### 方法2: 在代码中使用

#### 基本使用

```python
from shared.drivers.comm.device_serial_config_manager import get_device_config_manager
from shared.drivers.comm.rs485_comm import RS485Comm

# 获取设备配置
manager = get_device_config_manager()
manager.load_config_file('backend/conf/device_serial_config.json')
config = manager.get_device_config('power_amplifier')

# 创建通信层
comm = RS485Comm(
    port=config.port,
    baudrate=config.baudrate,
    data_bits=config.data_bits,
    stop_bits=config.stop_bits,
    parity=config.parity,
    timeout=config.timeout
)

# 使用通信层
# ...
```

#### 自动检测设备

```python
from shared.drivers.comm.device_serial_config_manager import get_device_config_manager

# 自动检测设备串口
manager = get_device_config_manager()
manager.load_config_file('backend/conf/device_serial_config.json')

# 自动检测
detected_port = manager.auto_detect_device_port('power_amplifier')

if detected_port:
    print(f"检测到设备串口: {detected_port}")
    
    # 更新配置
    manager.update_device_port('power_amplifier', detected_port)
    
    # 保存配置
    manager.save_config_file()
else:
    print("未检测到设备")
```

#### 使用便捷函数

```python
from shared.drivers.comm.device_serial_config_manager import get_device_port

# 获取设备串口
port = get_device_port('power_amplifier', auto_detect=True)

if port:
    print(f"设备串口: {port}")
else:
    print("未找到设备串口")
```

## 📊 配置文件格式

配置文件位于 `backend/conf/device_serial_config.json`：

```json
{
  "power_amplifier": {
    "device_id": "power_amplifier",
    "device_name": "ATA-101B功率放大器",
    "device_type": "power_amplifier",
    "port": "COM1",
    "baudrate": 9600,
    "data_bits": 8,
    "stop_bits": 1,
    "parity": "N",
    "flow_control": "none",
    "timeout": 1000,
    "auto_detect": true,
    "verify_command": null,
    "verify_response": null,
    "description": "用于编码器测试的功率放大器"
  }
}
```

### 配置参数说明

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| device_id | string | 设备唯一标识 | "power_amplifier" |
| device_name | string | 设备名称 | "ATA-101B功率放大器" |
| device_type | string | 设备类型 | "power_amplifier" |
| port | string | 串口号 | "COM1" |
| baudrate | int | 波特率 | 9600 |
| data_bits | int | 数据位 | 8 |
| stop_bits | int | 停止位 | 1 |
| parity | string | 校验位 (N/E/O) | "N" |
| flow_control | string | 流控制 | "none" |
| timeout | int | 超时时间(ms) | 1000 |
| auto_detect | bool | 是否自动检测 | true |
| verify_command | string | 验证命令 | null |
| verify_response | string | 验证响应 | null |
| description | string | 描述 | "用于编码器测试" |

## 🎯 实际应用示例

### ATA-101B功率放大器测试

```python
from shared.drivers.comm.device_serial_config_manager import get_device_config_manager
from shared.drivers.comm.rs485_comm import RS485Comm
from shared.drivers.protocol.custom_ascii_protocol import CustomASCIIProtocol
from projects.encoder_test.drivers.device.power_amplifier.power_amplifier import ATA101BPowerAmplifier

# 1. 加载设备配置
manager = get_device_config_manager()
manager.load_config_file('backend/conf/device_serial_config.json')
config = manager.get_device_config('power_amplifier')

# 2. 创建通信层
comm = RS485Comm(
    port=config.port,
    baudrate=config.baudrate,
    data_bits=config.data_bits,
    stop_bits=config.stop_bits,
    parity=config.parity,
    timeout=config.timeout
)

# 3. 创建协议层
protocol = CustomASCIIProtocol(
    comm=comm,
    command_prefix='ATATATA,SET,',
    command_suffix=';'
)

# 4. 创建设备驱动
pa = ATA101BPowerAmplifier(
    driver_id='power_amplifier',
    protocol=protocol
)

# 5. 连接设备
if pa.connect():
    print("设备连接成功")
    
    # 6. 使用设备
    pa.set_gain(20)
    pa.output_on()
    
    # 7. 断开连接
    pa.disconnect()
```

### 多设备管理

```python
from shared.drivers.comm.device_serial_config_manager import get_device_config_manager

# 获取所有设备状态
manager = get_device_config_manager()
manager.load_config_file('backend/conf/device_serial_config.json')
status = manager.get_all_devices_status()

# 显示所有设备状态
for device_id, info in status.items():
    print(f"{device_id}:")
    print(f"  端口: {info['port']}")
    print(f"  状态: {info['port_status']}")
    print(f"  连接: {info['connection_status']}")
```

## 🔍 故障排除

### 问题1: 串口被占用

**症状**：
```
串口状态: ✗ 被占用
```

**解决方法**：
```bash
# 方法1: 使用命令行工具重置串口
cd backend
python platform/tools/serial_device_manager.py reset-port --port COM1

# 方法2: 在代码中重置
from shared.drivers.comm.serial_port_manager import get_serial_port_manager
manager = get_serial_port_manager()
manager.reset_port('COM1')
```

### 问题2: 设备连接失败

**症状**：
```
连接状态: ✗ 连接失败
```

**可能原因**：
1. 设备未上电
2. 串口连接错误
3. 通信参数不匹配
4. 设备故障

**解决方法**：
```bash
# 1. 检查设备状态
cd backend
python platform/tools/serial_device_manager.py check-status --device power_amplifier

# 2. 自动检测设备
cd backend
python platform/tools/serial_device_manager.py auto-detect

# 3. 验证设备连接
# 在配置中添加验证命令和响应
```

### 问题3: 串口号变化

**症状**：
设备连接的串口号经常变化

**解决方法**：
```bash
# 启用自动检测
cd backend
python platform/tools/serial_device_manager.py auto-detect

# 或在代码中
port = manager.auto_detect_device_port('power_amplifier')
```

## 📝 最佳实践

### 1. 配置管理

- ✅ 将所有设备配置集中管理
- ✅ 使用有意义的设备ID
- ✅ 添加详细的描述信息
- ✅ 定期备份配置文件

### 2. 自动检测

- ✅ 对关键设备启用自动检测
- ✅ 设置验证命令和响应
- ✅ 定期运行自动检测

### 3. 错误处理

- ✅ 检查串口状态后再连接
- ✅ 处理连接失败的情况
- ✅ 提供详细的错误日志

### 4. 资源管理

- ✅ 使用后及时释放串口
- ✅ 避免长时间占用串口
- ✅ 使用资源管理器统一管理

## 🎓 总结

工业设备串口管理系统提供了：

1. **统一的配置管理** - 所有设备配置集中管理
2. **自动检测功能** - 自动识别设备串口
3. **状态监控** - 实时监控设备状态
4. **命令行工具** - 便捷的管理工具
5. **完善的错误处理** - 自动清理和恢复

通过这个系统，可以高效地管理工业自动化测试平台中的大量硬件设备，大大提高开发效率和系统稳定性。

---

**版本**: 1.0.0  
**日期**: 2026-06-01  
**作者**: Industrial Automation Platform