# ASDB2电机控制指南

## 1. 速度源选择（SPD0/SPD1映射）

| SPD0 | SPD1 | 速度源 | 寄存器值 | 说明 |
|------|------|--------|----------|------|
| OFF  | ON   | P1-09  | reg=1    | 内部速度1 |
| ON   | OFF  | P1-10  | reg=2    | 内部速度2 |
| OFF  | OFF  | P1-11  | reg=3    | 内部速度3 |
| ON   | ON   | 模拟输入 | reg=0   | 外部模拟电压 |

### 设置方法

```python
# 设置SPD0和SPD1
spd0 = 0x0014  # SPD0功能码
spd1 = 0x0015  # SPD1功能码

# 根据reg值设置bit8
if (reg & 1) == 0:
    spd0 |= 0x0100  # bit8=1，SPD0 ON
if (reg & 2) == 0:
    spd1 |= 0x0100  # bit8=1，SPD1 ON

# 写入寄存器
client.write_register(address=0x0218, value=spd0, device_id=SLAVE_ID)  # P2-12
client.write_register(address=0x021A, value=spd1, device_id=SLAVE_ID)  # P2-13
```

## 2. 方向控制（CMDINV）

| CMDINV值 | 方向     | 反馈速度 | 说明 |
|----------|----------|----------|------|
| 0x0006   | 顺时针   | -100 RPM | 负值表示顺时针 |
| 0x0106   | 逆时针   | +100 RPM | 正值表示逆时针 |

### 设置方法

```python
# 设置方向（P2-15）
cmdinv = 0x0006 if direction == 'CW' else 0x0106
client.write_register(address=0x021E, value=cmdinv, device_id=SLAVE_ID)
```

## 3. 速度设置

### 速度寄存器

| 寄存器 | 地址 | 单位 | 说明 |
|--------|------|------|------|
| P1-09  | 0x0112 | 0.1 r/min | 内部速度1 |
| P1-10  | 0x0114 | 0.1 r/min | 内部速度2 |
| P1-11  | 0x0116 | 0.1 r/min | 内部速度3 |

### 设置方法

```python
# 设置速度（单位：RPM）
speed_rpm = 100
value = int(speed_rpm * 10)  # 转换为0.1 r/min单位

# 写入32位寄存器
client.write_registers(address=0x0112, values=[value & 0xFFFF, (value >> 16) & 0xFFFF], device_id=SLAVE_ID)
```

## 4. 反馈速度读取

### 读取方法

```python
# 设置P0-02=6（电机转速）
client.write_register(address=calc_addr(0, 2), value=6, device_id=SLAVE_ID)

# 读取P0-09（32位，单位0.1 r/min）
r = client.read_holding_registers(address=calc_addr(0, 9), count=2, device_id=SLAVE_ID)
low_word = r.registers[0]
high_word = r.registers[1]
speed_value = (high_word << 16) | low_word

# 处理32位有符号整数
if speed_value & 0x80000000:
    speed_value = speed_value - 0x100000000

# 转换为RPM
feedback_speed = speed_value / 10.0
```

### 反馈速度符号

| 符号 | 方向     | 说明 |
|------|----------|------|
| 正值 | 逆时针   | +100 RPM表示逆时针100 RPM |
| 负值 | 顺时针   | -100 RPM表示顺时针100 RPM |

## 5. 伺服使能

### 使能方法

```python
# 使能伺服（P2-10）
status = 0x0001  # DriverOn
client.write_register(address=0x0214, value=status, device_id=SLAVE_ID)
```

### 关闭方法

```python
# 关闭伺服（P2-10）
status = 0x0101  # DriverOff
client.write_register(address=0x0214, value=status, device_id=SLAVE_ID)
```

### 注意事项

- DriverOn → 0x0001
- DriverOff → 0x0101
- 这个值与之前的文档描述相反，请以103Calibrator代码为准

## 6. 完整控制流程

```python
# 1. 禁用EEPROM
client.write_register(address=0x023C, value=5, device_id=SLAVE_ID)

# 2. 配置DI7为速度模式
client.write_register(address=0x0220, value=0x0118, device_id=SLAVE_ID)  # P2-16

# 3. 设置速度值
client.write_registers(address=0x0112, values=[1000, 0], device_id=SLAVE_ID)  # P1-09=100 RPM

# 4. 选择速度源（P1-09）
client.write_register(address=0x0218, value=0x0014, device_id=SLAVE_ID)  # SPD0=OFF
client.write_register(address=0x021A, value=0x0115, device_id=SLAVE_ID)  # SPD1=ON

# 5. 设置方向（顺时针）
client.write_register(address=0x021E, value=0x0006, device_id=SLAVE_ID)  # CMDINV

# 6. 使能伺服
client.write_register(address=0x0214, value=0x0001, device_id=SLAVE_ID)  # DriverOn

# 7. 读取反馈速度
feedback_speed = read_feedback_speed(client)
```

## 7. API使用示例

```python
from asdb2_driver import ASDB2Driver

with ASDB2Driver(port='COM4', baudrate=38400, slave_id=0x7F) as driver:
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
```

## 8. 注意事项

1. **方向符号**：反馈速度的负值表示顺时针，正值表示逆时针
2. **速度单位**：P1-09/P1-10/P1-11的单位是0.1 r/min，需要乘以10
3. **32位处理**：速度寄存器是32位有符号整数，需要正确处理符号位
4. **SPD映射**：SPD0=OFF,SPD1=ON对应P1-09，SPD0=ON,SPD1=OFF对应P1-10，SPD0=OFF,SPD1=OFF对应P1-11
5. **CMDINV值**：0x0006是顺时针，0x0106是逆时针
6. **伺服使能值**：DriverOn → 0x0001，DriverOff → 0x0101

## 9. 测试结果

### 测试环境
- 虚拟环境：D:\Users\Administrator\PycharmProjects\django-vue3-admin\.venv
- Python版本：3.11
- 通讯端口：COM4
- 波特率：38400

### 测试结果

| 测试项目 | 设定速度 | 反馈速度 | 方向 | 结果 |
|---------|---------|---------|------|------|
| P1-09 顺时针 | 1 RPM | -1.0 RPM | 顺时针 | ✅ |
| P1-09 逆时针 | 1 RPM | 1.0 RPM | 逆时针 | ✅ |
| P1-10 顺时针 | 100 RPM | -100.0 RPM | 顺时针 | ✅ |
| P1-10 逆时针 | 100 RPM | 100.0 RPM | 逆时针 | ✅ |
| P1-11 顺时针 | 1000 RPM | -1000.0 RPM | 顺时针 | ✅ |
| P1-11 逆时针 | 1000 RPM | 1000.0 RPM | 逆时针 | ✅ |

### 关键修复点

1. **修正SPD0/SPD1设置逻辑**：根据103Calibrator代码正确映射速度源
   - P1-09: SPD0=OFF (0x0014), SPD1=ON (0x0115)
   - P1-10: SPD0=ON (0x0114), SPD1=OFF (0x0015)
   - P1-11: SPD0=OFF (0x0014), SPD1=OFF (0x0015)

2. **修正伺服使能值**：103Calibrator中DriverOn → 0x0001, DriverOff → 0x0101

3. **添加驱动器初始化**：禁用EEPROM（P2-30=5）、配置DI7为速度模式（P2-16=0x0118）

### 测试结论

- 反馈速度与设定速度完全一致
- 方向控制正确（负值=顺时针，正值=逆时针）
- 所有速度源（P1-09/P1-10/P1-11）都能正常工作
- 在虚拟环境中成功运行