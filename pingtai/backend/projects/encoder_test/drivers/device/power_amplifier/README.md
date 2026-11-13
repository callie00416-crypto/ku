# ATA-101B 功率放大器驱动

## 📋 设备信息

- **型号**: ATA-101B
- **制造商**: 安泰电子
- **类型**: 单通道功率放大器
- **带宽**: DC~1MHz
- **最大输出电压**: 25Vp-p (±12.5Vp)
- **最大输出电流**: 2Ap
- **最大输出功率**: 25Wp

## 🔌 通信参数

- **接口**: USB虚拟串口 (CDC-ACM)
- **端口**: COM3 (自动检测)
- **波特率**: 9600
- **数据位**: 8
- **停止位**: 1
- **校验位**: 无
- **流控制**: 无
- **编码**: ASCII
- **回车换行符**: CRLF (\r\n) ⚠️ 重要！

## 📡 协议特点

- **协议类型**: 自定义ASCII协议
- **指令格式**: `ATA,SET,<CMD>,<VALUE>;\r\n`
- **响应格式**: ASCII字符串
- **关键发现**: 命令必须以CRLF (\r\n)结尾

## 📚 指令集

| 指令 | 功能 | 格式 | 说明 |
|------|------|------|------|
| 输出开 | 打开输出 | `ATA,SET,AON,0000;\r\n` | 启用设备输出 |
| 输出关 | 关闭输出 | `ATA,SET,AOF,0000;\r\n` | 禁用设备输出 |
| 保存设置 | 保存配置 | `ATA,SET,SAV,0000;\r\n` | 保存当前设置 |
| 输入电阻 | 设置输入电阻 | `ATA,SET,RIN,<VALUE>;\r\n` | 50Ω 或 1000Ω |
| 输出电阻 | 设置输出电阻 | `ATA,SET,ROT,<VALUE>;\r\n` | 1.5Ω 或 50Ω |
| 增益 | 设置增益 | `ATA,SET,AMP,<VALUE>;\r\n` | 0-20dB，步进2dB |

## 📦 文件结构

```
power_amplifier/
├── power_amplifier.py               # ATA-101B驱动主文件
├── README.md                        # 说明文档
├── TESTING_GUIDE.md                 # 测试指南
├── CLEANUP_PLAN.md                  # 文件整理计划
├── tests/                           # 测试文件目录
│   ├── test_comprehensive.py        # 全面测试
│   ├── test_newline_simple.py       # 回车换行符测试
│   ├── test_protocol_direct.py      # 协议测试
│   ├── test_output_switch.py        # 输出开关测试
│   └── test_screen_display.py       # 屏幕显示测试
└── archive/                         # 归档文件目录
    ├── deep_diagnose.py             # 深度诊断
    ├── detect_usb_device.py         # USB设备检测
    ├── diagnose_device.py           # 设备诊断
    ├── read_pdf_manual.py           # PDF阅读
    └── serial_assistant_for_manufacturer.py  # 串口助手
```

## 🚀 使用方法

### 1. 基本使用

```python
from shared.drivers.comm.rs485_comm import RS485Comm
from shared.drivers.protocol.custom_ascii_protocol import CustomASCIIProtocol
from projects.encoder_test.drivers.device.power_amplifier.power_amplifier import ATA101BPowerAmplifier

# 创建通信层（USB虚拟串口）
comm = RS485Comm(
    port='COM3',
    baudrate=9600,
    data_bits=8,
    stop_bits=1,
    parity='none',
    timeout=1000
)

# 创建协议层（关键：使用CRLF回车换行符）
protocol = CustomASCIIProtocol(
    comm=comm,
    command_prefix='ATA,SET,',
    command_suffix=';',
    newline='\r\n'  # ⚠️ 重要：必须使用CRLF
)

# 创建设备驱动
pa = ATA101BPowerAmplifier(
    driver_id='power_amplifier',
    protocol=protocol
)

# 连接设备
pa.connect()

# 设置增益
pa.set_gain(20)

# 设置输入电阻
pa.set_input_resistance(50.0)

# 设置输出电阻
pa.set_output_resistance(50.0)

# 打开输出
pa.output_on()

# 获取状态
status = pa.get_status()
print(status)

# 关闭输出
pa.output_off()

# 断开连接
pa.disconnect()
```

### 2. 快速测试

```bash
# 运行全面测试
cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
python test_comprehensive.py

# 运行回车换行符测试
cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
python test_newline_simple.py

# 运行协议测试
cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
python test_protocol_direct.py

# 运行输出开关测试
cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
python test_output_switch.py

# 运行屏幕显示测试
cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
python test_screen_display.py
```

## 🎯 功能特性

### 核心功能

- ✅ **输出控制**: 打开/关闭输出
- ✅ **增益设置**: 0-20dB，步进2dB
- ✅ **输入电阻设置**: 50Ω 或 1000Ω
- ✅ **输出电阻设置**: 1.5Ω 或 50Ω
- ✅ **设置保存**: 保存当前配置
- ✅ **状态查询**: 获取设备状态
- ✅ **设备重置**: 重置到默认状态

### 高级功能

- ✅ **参数验证**: 自动验证参数范围
- ✅ **错误处理**: 完善的错误处理机制
- ✅ **日志记录**: 详细的操作日志
- ✅ **状态管理**: 维护设备内部状态
- ✅ **响应解析**: 智能解析设备响应

## 📊 响应码

| 响应 | 含义 |
|------|------|
| `SET DONE!` | 设置成功 |
| `SET ERROR!` | 指令错误 |
| `OVER RANGE ERROR!` | 参数越界 |

## 🔧 参数范围

### 增益参数

- **范围**: 0-20dB
- **步进**: 2dB
- **有效值**: 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20

### 输入电阻

- **有效值**: 50Ω, 1000Ω

### 输出电阻

- **有效值**: 1.5Ω, 50Ω

## 🧪 测试说明

### 全面测试

测试驱动的完整功能：

```bash
cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
python test_comprehensive.py
```

**测试内容**:
- 设备初始化
- 通信层连接
- 协议层初始化
- 设备驱动创建
- 设备连接
- 增益设置
- 输入电阻设置
- 输出电阻设置
- 输出控制
- 状态查询
- 设置保存
- 设备断开

### 回车换行符测试

测试不同的回车换行符格式：

```bash
cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
python test_newline_simple.py
```

**测试内容**:
- 无回车换行符
- 仅换行符 LF (\n)
- 回车换行符 CRLF (\r\n) ⚠️ 正确答案
- 仅回车符 CR (\r)
- 双回车换行符 (\r\n\r\n)
- 反向回车换行符 (\n\r)

### 协议测试

直接测试协议层：

```bash
cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
python test_protocol_direct.py
```

**测试内容**:
- 协议层直接通信
- 命令构建和发送
- 响应解析
- 错误处理

### 输出开关测试

专门测试输出开关功能：

```bash
cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
python test_output_switch.py
```

**测试内容**:
- 输出开/关循环测试
- 屏幕显示观察
- 状态验证

### 屏幕显示测试

测试屏幕显示变化：

```bash
cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
python test_screen_display.py
```

**测试内容**:
- 各种参数设置
- 屏幕显示观察
- 参数验证

## 📝 代码生成

本驱动使用代码生成系统自动生成，基于以下文件：

- **设备规范**: `backend/platform/codegen/examples/ata101b_spec.py`
- **模板文件**: `backend/platform/codegen/templates/device/device_custom_ascii.py.j2`
- **生成脚本**: `backend/platform/codegen/examples/test_template_render.py`

### 重新生成驱动

```bash
cd backend/platform/codegen/examples
python test_template_render.py
```

## 🏗️ 架构设计

### 三层架构

```
ATA101BPowerAmplifier (设备层)
    ↓
CustomASCIIProtocol (协议层)
    ↓
RS485Comm (通信层)
```

### 职责分离

- **设备层**: 业务逻辑、状态管理、参数验证
- **协议层**: 命令构建、响应解析、协议转换
- **通信层**: 串口通信、数据传输

## 🔍 故障排除

### 常见问题

1. **设备连接失败**
   - 检查USB连接
   - 确认设备电源
   - 验证串口号（COM3）
   - 检查USB驱动是否安装

2. **参数设置失败**
   - 检查参数范围
   - 确认参数类型
   - 查看错误日志
   - 验证回车换行符配置

3. **响应解析错误**
   - 检查设备响应格式
   - 确认协议配置
   - 查看通信日志
   - 验证回车换行符

4. **设备无响应**
   - ⚠️ **最常见问题**：缺少CRLF回车换行符
   - 检查命令格式
   - 验证通信参数
   - 测试回车换行符配置

### 调试方法

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看设备状态
status = pa.get_status()
print(status)

# 检查设备连接
print(pa.is_connected)

# 查看错误计数
print(pa._error_count)
```

### 重要调试经验

**回车换行符问题** ⚠️⚠️⚠️

这是ATA-101B设备最容易导致通信失败的问题：

1. **必须使用CRLF** (\r\n)
   - ✅ 正确：`ATA,SET,AON,0000;\r\n`
   - ❌ 错误：`ATA,SET,AON,0000;`
   - ❌ 错误：`ATA,SET,AON,0000;\n`
   - ❌ 错误：`ATA,SET,AON,0000;\r`

2. **技术说明**：
   - `\r` (CR, Carriage Return, 0x0D) - 回车符，光标回到行首
   - `\n` (LF, Line Feed, 0x0A) - 换行符，光标移动到下一行
   - `\r\n` (CRLF) - 回车换行符，先回车再换行

3. **测试方法**：
   ```bash
   cd backend/projects/encoder_test/drivers/device/power_amplifier/tests
   python test_newline_simple.py
   ```

**命令前缀问题**

1. **正确的命令前缀**：`ATA,SET,`
2. **错误的命令前缀**：`ATATATA,SET,`

**响应格式问题**

1. **正确的响应**：`SET DONE!` (有空格)
2. **错误的响应**：`SETDONE!` (无空格)

**接口类型问题**

1. **实际接口**：USB虚拟串口 (CDC-ACM)
2. **手册描述**：RS485
3. **实际端口**：COM3 (自动检测)

## 📖 参考资料

- **设备手册**: `docs/drivers/device/Power Amplifier/ATA-101B使用说明书V2.0.pdf`
- **代码生成文档**: `backend/platform/codegen/docs/multi_protocol_support.md`
- **自定义ASCII协议**: `backend/shared/drivers/protocol/custom_ascii_protocol.py`
- **串口调试经验**: `docs/backend/serial_debugging_experience.md` ⚠️ 重要！
- **串口管理工具**: `backend/platform/tools/serial_device_manager.py`
- **设备配置**: `backend/conf/device_serial_config.json`

## 🤝 贡献

如需添加新功能或修复问题，请遵循以下步骤：

1. 修改设备规范文件
2. 更新模板文件（如需要）
3. 重新生成驱动代码
4. 运行测试验证
5. 提交代码审查

## 📄 许可证

本驱动遵循工业自动化测试平台的许可证规定。

---

**版本**: 2.0.0  
**日期**: 2026-06-02  
**作者**: Industrial Automation Platform  
**状态**: ✅ 已测试并验证  
**重要更新**: 
- 修正命令前缀（ATA,SET,）
- 修正回车换行符要求（\r\n）
- 修正响应格式（SET DONE!）
- 修正接口类型（USB虚拟串口）
- 修正串口号（COM3）
- 文件结构整理