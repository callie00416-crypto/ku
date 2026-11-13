# 设备集成指南 - 基于电源设备测试经验

## 📋 经验教训总结

基于博瑞程控双路电源设备的实际测试经验，总结以下关键教训，避免下次接入其他设备时遇到同样的问题。

---

## 🔧 关键技术问题

### 1. 寄存器地址偏移问题

**问题现象：**
- 使用协议文档中的寄存器地址（0x0001, 0x0003等）无法正常通信
- 只有远程模式寄存器（0x0000）可以正常读写

**根本原因：**
- 电源设备是**双路输出型号**，寄存器地址偏移了256（0x0100）
- 协议文档中的地址需要加上256才能正常访问

**解决方案：**
```python
# 设备配置中添加地址偏移
DEVICE_CONFIG = {
    'address_offset': 256,  # 双路型号地址偏移
}

# 读取时自动应用偏移
def _read_uint32(self, address: int) -> int:
    offset = self.DEVICE_CONFIG.get('address_offset', 0)
    actual_address = address + offset
    # ... 读取逻辑
```

**预防措施：**
- 在设备规范中明确标注地址偏移
- 代码生成模板支持地址偏移配置
- 测试时验证不同地址范围的寄存器

---

### 2. 数据格式错误

**问题现象：**
- 使用IEEE 754浮点数格式设置电压/电流，电源屏幕显示错误数值
- 读取的数据格式不正确

**根本原因：**
- 电源设备使用**32位整数格式**，不是IEEE 754浮点数
- 电压单位是mV（毫伏），电流单位是mA（毫安）

**解决方案：**
```python
# 正确的数据格式转换
def set_voltage(self, voltage: float):
    # 转换为32位整数（单位：mV）
    voltage_mv = int(voltage * 1000)
    
    # 拆分为两个16位整数（大端序）
    high_word = (voltage_mv >> 16) & 0xFFFF
    low_word = voltage_mv & 0xFFFF
    
    # 写入寄存器
    self.protocol.write_registers(address, [high_word, low_word])

def read_voltage(self) -> float:
    # 读取两个寄存器
    registers = self.protocol.read_registers(address, count=2)
    
    # 合并为32位整数
    voltage_mv = (registers[0] << 16) | registers[1]
    
    # 转换为V
    return voltage_mv / 1000.0
```

**预防措施：**
- 在设备规范中明确标注数据格式
- 支持多种数据格式（uint32, int32, float32等）
- 支持单位转换和缩放因子
- 代码生成模板支持数据格式配置

---

### 3. 控制逻辑相反

**问题现象：**
- 写入1打开输出，实际输出关闭
- 写入0关闭输出，实际输出打开

**根本原因：**
- 电源设备的输出控制逻辑与常规**相反**
- 0=打开，1=关闭（常规是1=打开，0=关闭）

**解决方案：**
```python
# 控制逻辑映射
CONTROL_LOGIC = {
    'output': {
        'normal': {'on': 1, 'off': 0},
        'inverted': {'on': 0, 'off': 1}
    }
}

# 使用映射
def turn_on(self, channel: int):
    logic = self.CONTROL_LOGIC['output']['inverted']
    self.protocol.write_register(address, logic['on'])

def turn_off(self, channel: int):
    logic = self.CONTROL_LOGIC['output']['inverted']
    self.protocol.write_register(address, logic['off'])
```

**预防措施：**
- 在设备规范中明确标注控制逻辑
- 支持控制逻辑映射配置
- 测试时验证控制方向是否正确

---

### 4. Modbus API参数错误

**问题现象：**
- `ModbusClientMixin.read_holding_registers() got an unexpected keyword argument 'slave'`
- `ModbusClientMixin.write_register() got an unexpected keyword argument 'slave'`

**根本原因：**
- pymodbus 3.x版本API变化
- 参数名从`slave`改为`device_id`
- `count`参数需要关键字参数传递

**解决方案：**
```python
# 正确的API调用
def read_registers(self, address: int, count: int = 1, slave_id: int = None):
    sid = slave_id or self.slave_id
    result = self._client.read_holding_registers(
        address, 
        count=count,      # 关键字参数
        device_id=sid     # device_id而非slave
    )

def write_register(self, address: int, value: int, slave_id: int = None):
    sid = slave_id or self.slave_id
    result = self._client.write_register(
        address, 
        value, 
        device_id=sid     # device_id而非slave
    )
```

**预防措施：**
- 检查pymodbus版本和API文档
- 使用参数名而非位置参数
- 代码生成模板支持API版本兼容

---

### 5. 连接状态检查问题

**问题现象：**
- `Modbus 未连接`错误，但实际已连接成功
- 依赖协议层连接状态检查导致连接失败

**根本原因：**
- Modbus驱动的`is_connected()`方法检查不准确
- 串口连接后客户端状态未正确更新

**解决方案：**
```python
# 不依赖连接状态检查
def connect(self) -> bool:
    try:
        # 直接连接，不检查状态
        if not self.protocol.connect():
            return False
        
        # 初始化设备
        self._initialize_device()
        
        self._is_connected = True
        return True
    except Exception as e:
        logger.error(f"连接失败: {e}")
        return False

# 修复连接状态检查
def is_connected(self) -> bool:
    if not self._client:
        return False
    if hasattr(self._client, 'is_socket_open'):
        return self._client.is_socket_open()
    if hasattr(self._client, 'connected'):
        return self._client.connected
    return self._is_connected
```

**预防措施：**
- 不依赖协议层连接状态检查
- 直接调用连接方法
- 提供多种连接状态检查方式

---

## 📁 设备规范模板

基于以上经验，创建标准化的设备规范模板：

```python
DEVICE_SPEC = {
    # 基本信息
    "device_name": "device_name",
    "class_name": "DeviceClass",
    "description": "设备描述",
    
    "manufacturer": "制造商",
    "model": "型号",
    "protocol": "modbus_rtu",
    "communication": "rs485",
    "channels": 1,
    
    # 设备配置（关键）
    "device_config": {
        "channels": 1,
        "address_offset": 0,      # 地址偏移
        "byte_order": "big",       # 字节序
        "data_format": "uint32"    # 数据格式
    },
    
    # 通道寄存器映射
    "channel_registers": {
        1: {
            "V_SET": {
                "address": 0x0001,
                "format": "uint32",
                "unit": "mV",
                "scale": 0.001,     # 单位转换
                "description": "设定电压"
            },
            "OUTPUT": {
                "address": 0x0009,
                "format": "uint16",
                "control_logic": {
                    "on": 1,        # 控制逻辑
                    "off": 0
                },
                "description": "输出控制"
            }
        }
    },
    
    # 数据格式配置
    "data_formats": {
        "uint32": {
            "size": 4,
            "signed": False,
            "description": "32位无符号整数"
        }
    },
    
    # 控制逻辑映射
    "control_logic": {
        "output": {
            "normal": {"on": 1, "off": 0},
            "inverted": {"on": 0, "off": 1}
        }
    }
}
```

---

## 🧪 测试流程

### 1. 基础连接测试
```python
# 测试串口连接
client = ModbusSerialClient(port='COM4', baudrate=9600)
if client.connect():
    print("连接成功")
    print(f"connected: {client.connected}")
    print(f"is_socket_open: {client.is_socket_open()}")
```

### 2. 寄存器扫描测试
```python
# 扫描不同地址范围
for addr in range(0, 100):
    try:
        result = client.read_holding_registers(addr, count=1, device_id=1)
        if not result.isError():
            print(f"0x{addr:04X}: {result.registers[0]}")
    except:
        pass
```

### 3. 数据格式验证
```python
# 测试不同数据格式
test_values = [5.0, 10.0, 12.0]
for value in test_values:
    # 尝试IEEE 754格式
    ieee754_bytes = struct.pack('>f', value)
    # 尝试32位整数格式
    uint32_value = int(value * 1000)
```

### 4. 控制逻辑验证
```python
# 测试输出控制
for test_value in [0, 1]:
    client.write_register(output_addr, test_value, device_id=1)
    time.sleep(1.0)
    # 观察设备响应
```

---

## 🎯 最佳实践

### 1. 设备规范先行
- 在编写代码前，先完善设备规范
- 明确标注所有特殊配置
- 包括地址偏移、数据格式、控制逻辑等

### 2. 分阶段测试
- 先测试基础连接
- 再测试寄存器访问
- 最后测试业务逻辑

### 3. 错误处理完善
- 捕获所有异常
- 提供详细错误信息
- 支持资源清理

### 4. 日志记录详细
- 记录所有操作
- 记录设备响应
- 记录异常信息

### 5. 文档同步更新
- 及时更新设备规范
- 记录测试结果
- 标注已知问题

---

## 📚 相关文件

- [device_enhanced.py.j2](file:///D:\Users\Administrator\PycharmProjects\django-vue3-admin\backend\platform\codegen\templates\device\device_enhanced.py.j2) - 增强版设备模板
- [power_supply_spec.py](file:///D:\Users\Administrator\PycharmProjects\django-vue3-admin\backend\platform\codegen\examples\power_supply_spec.py) - 电源设备规范示例
- [modbus_rtu.py](file:///D:\Users\Administrator\PycharmProjects\django-vue3-admin\backend\shared\drivers\protocol\modbus_rtu.py) - Modbus协议驱动
- [power_supply.py](file:///D:\Users\Administrator\PycharmProjects\django-vue3-admin\backend\projects\encoder_test\drivers\device\power_supply\power_supply.py) - 电源设备驱动

---

## 🔄 持续改进

### 下次接入设备时：
1. **先完善设备规范** - 基于本指南的模板
2. **使用增强版模板** - 支持复杂配置
3. **分阶段测试** - 避免一次性测试所有功能
4. **记录测试结果** - 更新设备规范
5. **分享经验教训** - 更新本指南

### 代码生成平台改进：
1. **支持更多数据格式** - uint16, uint32, int32, float32等
2. **支持控制逻辑映射** - normal/inverted
3. **支持地址偏移配置** - 自动应用偏移
4. **支持单位转换** - 自动缩放
5. **支持多通道设备** - 通道映射配置

---

## 📞 技术支持

如有问题，请参考：
- 设备协议文档
- pymodbus API文档
- 本指南的经验教训
- 相关测试脚本

**记住：经验是最好的老师，但文档是最好的传承！**