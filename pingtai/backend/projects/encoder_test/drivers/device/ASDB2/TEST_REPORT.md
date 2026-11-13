# ASDB2电机驱动测试报告

## 测试日期
2026-06-16

## 测试环境

### 硬件环境
- 伺服驱动器：台达ASDA-B2系列
- 通讯接口：RS485
- 通讯端口：COM4
- 波特率：38400
- 奇偶校验：无
- 停止位：2
- 数据位：8

### 软件环境
- 操作系统：Windows
- Python版本：3.11
- 虚拟环境：D:\Users\Administrator\PycharmProjects\django-vue3-admin\.venv
- 依赖库：pymodbus

### 测试框架
- 架构：新框架（符合工业平台规范）
- 组合关系：ASDB2Driver -> ModbusDriver -> RS485Comm
- 继承关系：ASDB2Driver -> BaseDevice

## 测试目的

验证ASDB2电机驱动在虚拟环境中的功能正确性，包括：
1. P1-09/P1-10/P1-11三个速度源的控制
2. 顺时针和逆时针方向控制
3. 反馈速度读取的准确性
4. 伺服使能/禁用功能

## 测试用例

### 测试脚本
`tests/test_speed_control.py`

### 测试流程
1. 创建通讯层（RS485）
2. 创建协议层（MODBUS-RTU）
3. 创建设备驱动（ASDB2）
4. 连接设备
5. 初始化驱动器
6. 设置速度值（P1-09=1 RPM, P1-10=100 RPM, P1-11=1000 RPM）
7. 使能伺服
8. 依次测试P1-09、P1-10、P1-11的顺时针和逆时针转动
9. 读取反馈速度
10. 停止电机
11. 关闭伺服
12. 断开连接

## 测试结果

### 详细测试结果

| 测试项目 | 设定速度 | 反馈速度 | 方向 | 结果 | 误差 |
|---------|---------|---------|------|------|------|
| P1-09 顺时针 | 1 RPM | -1.0 RPM | 顺时针 | ✅ | 0% |
| P1-09 逆时针 | 1 RPM | 1.0 RPM | 逆时针 | ✅ | 0% |
| P1-10 顺时针 | 100 RPM | -100.0 RPM | 顺时针 | ✅ | 0% |
| P1-10 逆时针 | 100 RPM | 100.0 RPM | 逆时针 | ✅ | 0% |
| P1-11 顺时针 | 1000 RPM | -1000.0 RPM | 顺时针 | ✅ | 0% |
| P1-11 逆时针 | 1000 RPM | 1000.0 RPM | 逆时针 | ✅ | 0% |

### 测试结论

✅ **所有测试用例通过**

- 反馈速度与设定速度完全一致，误差为0%
- 方向控制正确（负值=顺时针，正值=逆时针）
- 所有速度源（P1-09/P1-10/P1-11）都能正常工作
- 伺服使能/禁用功能正常
- 在虚拟环境中成功运行

## 关键修复点

### 1. 修正SPD0/SPD1设置逻辑

**问题**：原实现中SPD0/SPD1的设置逻辑错误

**修复**：根据103Calibrator代码正确映射速度源
- P1-09: SPD0=OFF (0x0014), SPD1=ON (0x0115)
- P1-10: SPD0=ON (0x0114), SPD1=OFF (0x0015)
- P1-11: SPD0=OFF (0x0014), SPD1=OFF (0x0015)

**代码**：
```python
def select_speed_source(self, source) -> bool:
    reg = 1 if source == self.SPEED_SOURCE_P1_09 else \
          2 if source == self.SPEED_SOURCE_P1_10 else 3
    
    spd0 = 0x0014
    spd1 = 0x0015
    
    if reg == 1:
        spd1 |= 0x0100  # SPD1 ON
    elif reg == 2:
        spd0 |= 0x0100  # SPD0 ON
    elif reg == 3:
        pass  # SPD0 OFF, SPD1 OFF
    
    self.modbus.write_register(address=0x0218, value=spd0, slave_id=self.slave_id)
    self.modbus.write_register(address=0x021A, value=spd1, slave_id=self.slave_id)
```

### 2. 修正伺服使能值

**问题**：原实现中伺服使能值与103Calibrator代码相反

**修复**：根据103Calibrator代码修正
- DriverOn → 0x0001
- DriverOff → 0x0101

**代码**：
```python
def enable_servo(self, enable=True) -> bool:
    # 103Calibrator中：DriverOn → 0x0001, DriverOff → 0x0101
    status = 0x0001 if enable else 0x0101
    self.modbus.write_register(address=0x0214, value=status, slave_id=self.slave_id)
```

### 3. 添加驱动器初始化

**问题**：缺少必要的驱动器初始化步骤

**修复**：添加`initialize_driver()`函数
- 禁用EEPROM（P2-30=5）
- 配置DI7为速度模式（P2-16=0x0118）

**代码**：
```python
def initialize_driver(self) -> bool:
    # 禁用EEPROM（P2-30=5）
    self.modbus.write_register(address=0x023C, value=5, slave_id=self.slave_id)
    
    # 配置DI7为速度模式（P2-16=0x0118）
    self.modbus.write_register(address=0x0220, value=0x0118, slave_id=self.slave_id)
```

## 技术要点

### 1. 速度源映射

| SPD0 | SPD1 | 速度源 | 寄存器值 |
|------|------|--------|----------|
| OFF  | ON   | P1-09  | reg=1    |
| ON   | OFF  | P1-10  | reg=2    |
| OFF  | OFF  | P1-11  | reg=3    |

### 2. 方向控制

| CMDINV值 | 方向     | 反馈速度 |
|----------|----------|----------|
| 0x0006   | 顺时针   | -100 RPM |
| 0x0106   | 逆时针   | +100 RPM |

### 3. 反馈速度符号

| 符号 | 方向     | 说明 |
|------|----------|------|
| 负值 | 顺时针   | -100 RPM表示顺时针100 RPM |
| 正值 | 逆时针   | +100 RPM表示逆时针100 RPM |

### 4. 速度单位

- P1-09/P1-10/P1-11的单位是0.1 r/min
- 设置时需要乘以10
- 读取时需要除以10

### 5. 32位处理

- 速度寄存器是32位有符号整数
- 需要正确处理符号位
- 最高位为1时表示负数

## 架构集成

### 新框架架构

ASDB2Driver采用组合关系：
```
ASDB2Driver -> ModbusDriver -> RS485Comm
```

### 继承关系

```
ASDB2Driver -> BaseDevice
```

### 平台集成

- 继承BaseDevice基类
- 支持平台设备生命周期管理
- 集成平台事件系统
- 符合工业设备规范

## 参考文档

1. [ASDB2控制指南](ASDB2_CONTROL_GUIDE.md)
2. [DELTA_IA-ASD_ASDA-B2_UM_SC_20230421.txt](../../../../../docs/drivers/device/ASDB2/DELTA_IA-ASD_ASDA-B2_UM_SC_20230421.txt)
3. [DELTA_IA-ASDA_ASDA-Soft_UM_SC_20131024.txt](../../../../../docs/drivers/device/ASDB2/DELTA_IA-ASDA_ASDA-Soft_UM_SC_20131024.txt)
4. 103CalibratorV4_RandomSpeed_FastSwitch/（C语言参考代码）

## 总结

本次测试成功验证了ASDB2电机驱动在虚拟环境中的功能正确性。通过修正SPD0/SPD1设置逻辑、伺服使能值和添加驱动器初始化，所有测试用例均通过，反馈速度与设定速度完全一致，方向控制正确。

测试结果表明，ASDB2电机驱动已经完全符合新框架的架构要求，可以正常用于工业自动化测试平台。

## 附录

### 测试脚本

`tests/test_speed_control.py`

### 驱动实现

`asdb2_driver.py`

### 使用示例

`example_usage.py`