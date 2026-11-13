# RIGOL DG811波形发生器驱动

## 设备信息

- **厂商**: RIGOL
- **型号**: DG811
- **序列号**: DG8A272300397
- **连接方式**: USB (NI-VISA)
- **协议**: SCPI
- **通道数**: 双通道
- **频率范围**: 1μHz ~ 60MHz
- **幅度范围**: 10mVpp ~ 10Vpp
- **偏置范围**: -5V ~ +5V

## USB设备信息

- **Vendor ID**: 0x1AB1
- **Product ID**: 0x0643
- **资源字符串**: `USB0::0x1AB1::0x0643::DG8A272300397::INSTR`

## 架构说明

### 三层架构

```
DG811WaveformGenerator (设备层)
    ↓
SCPIProtocol (协议层)
    ↓
VISA通信层 (通信层)
```

### 文件结构

```
backend/
├── shared/drivers/
│   ├── comm/
│   │   ├── usb_comm.py              # USB通信驱动 (pyusb)
│   │   └── usb_visa_comm.py         # USB VISA通信驱动 (pyvisa)
│   └── protocol/
│       └── scpi_protocol.py         # SCPI协议驱动
│
└── projects/encoder_test/drivers/device/
    └── waveform_generator/
        ├── __init__.py               # 模块导出
        ├── dg811.py                  # DG811设备驱动
        ├── test_dg811_stable.py      # 稳定测试脚本
        ├── test_simple_waveform.py   # 简单示例脚本
        └── README.md                 # 本文档
```

## 安装依赖

```bash
# 安装Python依赖
pip install pyusb pyvisa pyvisa-py

# 安装NI-VISA驱动
# 从NI官网下载并安装: https://www.ni.com/zh-cn/support/downloads/drivers/download.ni-visa.html
```

## 使用方法

### 基本使用

```python
import sys
from pathlib import Path
import pyvisa
from shared.drivers.protocol.scpi_protocol import SCPIProtocol
from projects.encoder_test.drivers.device.waveform_generator.dg811 import DG811WaveformGenerator

# 设置路径
backend_path = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(backend_path))

# 创建VISA通信类
class VisaComm:
    def __init__(self, instrument):
        self.instrument = instrument
        self._is_open = True
    
    def send(self, data):
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        self.instrument.write(data)
        return len(data)
    
    def recv(self, size=1024, timeout=1.0):
        try:
            data = self.instrument.read()
            if isinstance(data, str):
                data = data.encode('utf-8')
            return data
        except:
            return None
    
    @property
    def is_open(self):
        return self._is_open
    
    def close(self):
        self.instrument.close()
        self._is_open = False

# 连接设备
resource_string = "USB0::0x1AB1::0x0643::DG8A272300397::INSTR"
rm = pyvisa.ResourceManager()
instrument = rm.open_resource(resource_string)
instrument.timeout = 10000

# 创建通信层
comm = VisaComm(instrument)

# 创建协议层
protocol = SCPIProtocol(driver_id='scpi', comm=comm)
protocol.connect()

# 创建设备驱动
generator = DG811WaveformGenerator(driver_id='dg811', protocol=protocol)
generator.connect()

# 设置波形
generator.set_waveform(
    waveform='SIN',
    frequency=1000.0,
    amplitude=5.0,
    offset=0.0,
    phase=0.0,
    channel=1
)

# 打开输出
generator.output_on(channel=1)

# 读取状态
status = generator.read_status(channel=1)
print(status)

# 关闭输出
generator.output_off(channel=1)

# 断开连接
generator.disconnect()
```

### 简化API调用

```python
# 设置波形（简化版）
generator.set_waveform('SIN', frequency=1000, amplitude=5.0, offset=0.0, channel=1)

# 打开输出
generator.output_on(channel=1)

# 关闭输出
generator.output_off(channel=1)
```

## 支持的波形类型

| 波形类型 | SCPI命令 | 描述 |
|----------|----------|------|
| 正弦波 | `SIN` | 标准正弦波形 |
| 方波 | `SQU` | 矩形方波 |
| 三角波 | `TRI` | 线性三角波 |
| 锯齿波 | `RAMP` | 线性锯齿波 |
| 脉冲波 | `PULS` | 窄脉冲波形 |

## 主要API

### 连接管理

- `connect()` - 连接设备
- `disconnect()` - 断开设备
- `is_connected` - 检查连接状态

### 波形设置

- `set_waveform(waveform, frequency, amplitude, offset, phase, channel)` - 设置波形参数
- `set_frequency(frequency, channel)` - 设置频率
- `set_amplitude(amplitude, channel)` - 设置幅度
- `set_offset(offset, channel)` - 设置偏置
- `set_phase(phase, channel)` - 设置相位

### 输出控制

- `output_on(channel)` - 打开输出
- `output_off(channel)` - 关闭输出

### 状态读取

- `get_waveform(channel)` - 获取波形类型
- `get_frequency(channel)` - 获取频率
- `get_amplitude(channel)` - 获取幅度
- `get_offset(channel)` - 获取偏置
- `get_phase(channel)` - 获取相位
- `get_output_status(channel)` - 获取输出状态
- `read_status(channel)` - 读取通道状态
- `read_data()` - 读取双通道数据

### 数据写入

- `write_data(data)` - 批量写入数据

### 设备管理

- `reset()` - 重置设备
- `health_check()` - 健康检查
- `get_device_info()` - 获取设备信息

## 测试

### 运行稳定测试

```bash
cd backend/projects/encoder_test/drivers/device/waveform_generator
python test_dg811_stable.py
```

测试选项：
1. 基本通信测试 - 验证基本SCPI命令
2. 波形变化测试 - 测试5种波形切换
3. 两个测试都运行 - 完整测试

### 运行简单示例

```bash
python test_simple_waveform.py
```

这个脚本演示了最基本的波形设置API调用。

## 参数范围

| 参数 | 最小值 | 最大值 | 单位 |
|------|--------|--------|------|
| 频率 | 1 | 60000000 | Hz |
| 幅度 | 0.01 | 10 | Vpp |
| 偏置 | -5 | +5 | V |
| 相位 | 0 | 360 | 度 |

## 故障排除

### USB连接失败

1. 检查USB线缆是否连接
2. 检查NI-VISA驱动是否已安装
3. 检查设备是否被其他程序占用
4. 使用NI MAX工具查看设备是否被识别

### VISA资源找不到

1. 确认设备VID/PID: `0x1AB1/0x0643`
2. 使用NI MAX查看VISA资源
3. 尝试重新安装NI-VISA驱动
4. 重启电脑和设备

### SCPI命令失败

1. 检查设备是否正常响应
2. 检查SCPI命令格式是否正确
3. 增加命令之间的延迟时间
4. 查看设备错误信息：`protocol.get_error()`

### 参数设置失败

1. 检查参数是否在有效范围内
2. 检查通道号是否正确（1或2）
3. 检查波形类型是否支持
4. 查看设备屏幕上的错误提示

## 架构集成

### 平台设备集成

DG811驱动支持与平台设备集成：

```python
from platform_core.domain.device import Device

# 创建平台设备
platform_device = Device(
    id='dg811_001',
    code='WG-001',
    name='波形发生器1',
    station_id=1
)

# 创建设备驱动时传入平台设备
generator = DG811WaveformGenerator(
    driver_id='dg811',
    protocol=protocol,
    platform_device=platform_device
)
```

### 事件发布

驱动会自动发布以下事件：

- 设备连接事件
- 设备断开事件
- 操作成功事件
- 操作失败事件
- 错误事件

### 健康检查

驱动提供详细的健康检查信息：

```python
health = generator.health_check()
print(health)
```

健康检查包括：

- 设备连接状态
- 通道状态
- 实时参数
- 错误信息
- 平台设备状态

## 注意事项

1. **生命周期管理**: 遵循工业设备生命周期规范，不要在`__init__`中自动连接
2. **参数验证**: 所有参数都会进行范围验证
3. **错误处理**: 所有操作都有错误处理和日志记录
4. **状态同步**: 驱动会维护本地状态，与设备状态同步
5. **资源释放**: 断开连接时会自动关闭输出和释放资源
6. **命令延迟**: 连续发送命令时建议增加50-100ms延迟
7. **超时设置**: VISA超时建议设置为10秒以上

## 性能优化建议

1. **批量操作**: 尽量使用`set_waveform()`一次性设置所有参数
2. **减少查询**: 避免频繁查询状态，影响性能
3. **延迟控制**: 根据实际情况调整命令延迟时间
4. **连接复用**: 在测试过程中保持连接，避免频繁重连

## 版本历史

### v1.0.0 (2026-06-01)
- 初始版本发布
- 支持基本波形设置
- 支持双通道控制
- 支持NI-VISA连接
- 完整的错误处理

## 许可证

本驱动遵循工业自动化测试平台架构规范。