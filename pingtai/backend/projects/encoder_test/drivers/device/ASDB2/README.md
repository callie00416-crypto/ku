# ASDB2电机驱动

台达ASDA-B2系列伺服驱动器Python驱动，基于MODBUS-RTU协议。

## 目录结构

```
ASDB2/
├── __init__.py                          # 模块初始化
├── asdb2_driver.py                      # 电机驱动API（符合新框架）
├── example_usage.py                     # API使用示例
├── ASDB2_CONTROL_GUIDE.md              # 控制指南文档
├── tests/                               # 测试脚本
│   ├── test_speed_control.py           # P1-09/P1-10/P1-11速度测试
│   ├── test_comprehensive.py           # 综合测试脚本
│   └── test_motor_control_final_correct.py  # 电机控制测试
└── 103CalibratorV4_RandomSpeed_FastSwitch/  # 参考代码（C语言）
    ├── Source/                          # 源代码
    ├── Objects/                         # 编译输出
    └── RTE/                             # 运行时环境
```

## 核心功能

### 1. 速度控制
- 支持三个内部速度源（P1-09、P1-10、P1-11）
- 支持顺时针和逆时针方向控制
- 速度范围：0-3000 RPM

### 2. 反馈读取
- 读取电机实际转速
- 自动处理32位有符号整数
- 支持方向判断（正值=逆时针，负值=顺时针）

### 3. 伺服控制
- 伺服使能/禁用
- 软件SDI控制
- 速度模式配置

## 快速开始

### 基本使用

```python
from shared.drivers.comm.rs485_comm import RS485Comm
from shared.drivers.protocol.modbus_rtu import ModbusDriver
from projects.encoder_test.drivers.device.ASDB2.asdb2_driver import ASDB2Driver

# 创建通讯层
comm = RS485Comm(
    driver_id='rs485_asdb2',
    port='COM4',
    baudrate=38400,
    parity='N',
    stopbits=2,
    bytesize=8,
    timeout=2.0
)

# 创建协议层
protocol = ModbusDriver(
    driver_id='modbus_asdb2',
    comm=comm,
    slave_id=0x7F,
    mode='rtu'
)

# 创建设备驱动
driver = ASDB2Driver(
    driver_id='asdb2',
    protocol=protocol,
    slave_id=0x7F
)

# 连接设备
driver.connect()

# 初始化驱动器
driver.initialize_driver()

# 设置速度值
driver.set_speed(p1_09=100, p1_10=100, p1_11=100)

# 使能伺服
driver.enable_servo(True)

# 运行电机（顺时针，100 RPM，使用P1-11）
driver.run_motor(speed_rpm=100, direction='CW', source='P1-11')

# 读取反馈速度
feedback_speed = driver.read_feedback_speed()
print(f"反馈速度: {feedback_speed} RPM")

# 停止电机
driver.stop_motor()

# 关闭伺服
driver.enable_servo(False)

# 断开连接
driver.disconnect()
```

### 运行测试

```bash
# 激活虚拟环境
D:\Users\Administrator\PycharmProjects\django-vue3-admin\.venv\Scripts\activate

# P1-09/P1-10/P1-11速度测试（推荐）
python tests/test_speed_control.py

# 综合测试（包含所有测试功能）
python tests/test_comprehensive.py

# 电机控制测试
python tests/test_motor_control_final_correct.py

# API使用示例
python example_usage.py
```

## 关键参数

### 速度源选择（SPD0/SPD1映射）

| SPD0 | SPD1 | 速度源 | 寄存器值 |
|------|------|--------|----------|
| OFF  | ON   | P1-09  | reg=1    |
| ON   | OFF  | P1-10  | reg=2    |
| OFF  | OFF  | P1-11  | reg=3    |

### 方向控制（CMDINV）

| CMDINV值 | 方向     | 反馈速度 |
|----------|----------|----------|
| 0x0006   | 顺时针   | -100 RPM |
| 0x0106   | 逆时针   | +100 RPM |

### 反馈速度符号

| 符号 | 方向     | 说明 |
|------|----------|------|
| 负值 | 顺时针   | -100 RPM表示顺时针100 RPM |
| 正值 | 逆时针   | +100 RPM表示逆时针100 RPM |

## API文档

### ASDB2Driver

#### 初始化
```python
driver = ASDB2Driver(port='COM4', baudrate=38400, slave_id=0x7F)
```

#### 连接/断开
```python
driver.connect()
driver.disconnect()
```

#### 速度设置
```python
driver.set_speed(p1_09=100, p1_10=100, p1_11=100)
```

#### 速度源选择
```python
driver.select_speed_source('P1-11')  # 'P1-09', 'P1-10', 'P1-11'
```

#### 方向控制
```python
driver.set_direction('CW')  # 'CW'或'CCW'
```

#### 伺服控制
```python
driver.enable_servo(True)   # 使能
driver.enable_servo(False)  # 禁用
```

#### 运行电机
```python
driver.run_motor(speed_rpm=100, direction='CW', source='P1-11')
```

#### 停止电机
```python
driver.stop_motor()
```

#### 读取反馈速度
```python
feedback_speed = driver.read_feedback_speed()
```

## 注意事项

1. **方向符号**：反馈速度的负值表示顺时针，正值表示逆时针
2. **速度单位**：P1-09/P1-10/P1-11的单位是0.1 r/min，需要乘以10
3. **32位处理**：速度寄存器是32位有符号整数，需要正确处理符号位
4. **SPD映射**：SPD0=OFF,SPD1=ON对应P1-09，SPD0=ON,SPD1=OFF对应P1-10，SPD0=OFF,SPD1=OFF对应P1-11
5. **CMDINV值**：0x0006是顺时针，0x0106是逆时针
6. **伺服使能值**：DriverOn → 0x0001，DriverOff → 0x0101
7. **驱动器初始化**：首次使用需要调用`initialize_driver()`进行初始化
8. **新框架架构**：ASDB2Driver采用组合关系（ASDB2Driver -> ModbusDriver -> RS485Comm）

## 测试结果

### 测试环境
- 虚拟环境：D:\Users\Administrator\PycharmProjects\django-vue3-admin\.venv
- Python版本：3.11
- 通讯端口：COM4
- 波特率：38400

### 测试结果

| 测试项目 | 设定速度 | 反馈速度 | 方向 | 结果 |
|---------|---------|---------|------|------|
| P1-09 顺时针 | 10 RPM | -10.0 RPM | 顺时针 | ✅ |
| P1-09 逆时针 | 10 RPM | 10.0 RPM | 逆时针 | ✅ |
| P1-10 顺时针 | 100 RPM | -100.0 RPM | 顺时针 | ✅ |
| P1-10 逆时针 | 100 RPM | 100.0 RPM | 逆时针 | ✅ |
| P1-11 顺时针 | 1000 RPM | -1000.0 RPM | 顺时针 | ✅ |
| P1-11 逆时针 | 1000 RPM | 1000.0 RPM | 逆时针 | ✅ |

### 测试结论

- 反馈速度与设定速度完全一致
- 方向控制正确（负值=顺时针，正值=逆时针）
- 所有速度源（P1-09/P1-10/P1-11）都能正常工作
- 在虚拟环境中成功运行

## 依赖

- Python 3.7+
- pymodbus

## 安装依赖

```bash
pip install pymodbus
```

## 参考文档

- [ASDB2控制指南](ASDB2_CONTROL_GUIDE.md)
- [DELTA_IA-ASD_ASDA-B2_UM_SC_20230421.txt](../../../../../docs/drivers/device/ASDB2/DELTA_IA-ASD_ASDA-B2_UM_SC_20230421.txt)
- [DELTA_IA-ASDA_ASDA-Soft_UM_SC_20131024.txt](../../../../../docs/drivers/device/ASDB2/DELTA_IA-ASDA_ASDA-Soft_UM_SC_20131024.txt)

## 参考代码

`103CalibratorV4_RandomSpeed_FastSwitch/` 目录包含C语言参考代码，展示了完整的电机控制流程。

## 许可证

MIT License