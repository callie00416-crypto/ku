# 设备生成器使用示例

## 快速开始

### 1. 基本使用

```bash
# 生成一个名为 temperature_sensor 的设备
python tools/device_generator.py temperature_sensor
```

这将自动生成：
- 设备驱动代码：`projects/encoder_test/drivers/device/temperature_sensor/temperature_sensor.py`
- 设备适配器：`projects/encoder_test/adapters/temperature_sensor_adapter.py`
- 单元测试：`tests/device/test_temperature_sensor.py`
- 集成测试：`tests/device/test_temperature_sensor_full_link.py`
- 自动注册到驱动工厂

### 2. 完整参数使用

```bash
# 生成一个温度传感器设备，包含完整设备信息
python tools/device_generator.py temperature_sensor \
    --manufacturer "西门子" \
    --model "SITRANS T" \
    --protocol "modbus_rtu" \
    --communication "rs485" \
    --description "工业温度传感器"
```

## 实际案例

### 案例1：添加压力传感器

```bash
# 生成压力传感器设备
python tools/device_generator.py pressure_sensor \
    --manufacturer "霍尼韦尔" \
    --model "Honeywell PPT" \
    --protocol "modbus_rtu" \
    --communication "rs485" \
    --description "高精度压力传感器"
```

生成的文件结构：
```
projects/encoder_test/drivers/device/pressure_sensor/
├── __init__.py
└── pressure_sensor.py

projects/encoder_test/adapters/
└── pressure_sensor_adapter.py

tests/device/
├── test_pressure_sensor.py
└── test_pressure_sensor_full_link.py
```

### 案例2：添加PLC控制器

```bash
# 生成PLC控制器设备
python tools/device_generator.py plc_controller \
    --manufacturer "西门子" \
    --model "S7-1200" \
    --protocol "s7_protocol" \
    --communication "ethernet" \
    --description "可编程逻辑控制器"
```

### 案例3：添加伺服电机

```bash
# 生成伺服电机设备
python tools/device_generator.py servo_motor \
    --manufacturer "松下" \
    --model "MINAS A6" \
    --protocol "modbus_rtu" \
    --communication "rs485" \
    --description "交流伺服电机驱动器"
```

## 使用生成的设备

### 1. 导入生成的设备

```python
from projects.encoder_test.drivers.device.pressure_sensor.pressure_sensor import PressureSensor
from projects.encoder_test.adapters.pressure_sensor_adapter import PressureSensorAdapter
from shared.drivers.factory import CommFactory, ProtocolFactory
from platform.domain.common.enums import ProtocolType
```

### 2. 创建平台设备

```python
# 创建平台设备
platform_device = PressureSensorAdapter.to_platform_device(
    station_id=1,
    device_code="PS-001",
    device_name="压力传感器",
    protocol=ProtocolType.MODBUS_RTU,
    connection_params=PressureSensorAdapter.create_connection_params(
        port='COM3',
        baudrate=9600,
        slave_id=2
    ),
    device_params=PressureSensorAdapter.create_device_params(
        range_min=0.0,
        range_max=10.0,
        unit='MPa'
    )
)
```

### 3. 创建通信层

```python
# 创建通信层
comm = CommFactory.create('rs485', port='COM3', baudrate=9600)
protocol = ProtocolFactory.create('modbus_rtu', comm=comm, slave_id=2)
```

### 4. 创建设备驱动

```python
# 创建设备驱动
sensor = PressureSensor(
    driver_id='pressure_sensor',
    protocol=protocol,
    platform_device=platform_device
)
```

### 5. 使用设备

```python
# 连接设备
if sensor.connect():
    print("设备连接成功")
    
    # 读取数据
    data = sensor.read_data()
    print(f"当前压力: {data.get('pressure', 0)} MPa")
    
    # 健康检查
    health = sensor.health_check()
    print(f"设备状态: {health['device_status']}")
    
    # 断开连接
    sensor.disconnect()
```

## 测试生成的设备

### 运行单元测试

```bash
# 运行压力传感器单元测试
python tests/device/test_pressure_sensor.py
```

### 运行集成测试

```bash
# 运行压力传感器全链路测试
python tests/device/test_pressure_sensor_full_link.py
```

## 自定义设备实现

生成基础代码后，您需要根据具体设备实现以下方法：

### 1. 实现设备初始化

```python
def _initialize_device(self):
    """初始化设备"""
    # 设置设备工作模式
    self.protocol.write_register(0x1000, 0x01)
    
    # 配置采样参数
    self.protocol.write_register(0x1001, 0x0A)  # 采样间隔
    
    # 启动设备
    self.protocol.write_register(0x1002, 0x01)
```

### 2. 实现数据读取

```python
def read_data(self) -> Dict[str, Any]:
    """读取设备数据"""
    if not self.is_connected:
        raise ConnectionError("设备未连接")
    
    try:
        # 读取压力值
        pressure_raw = self.protocol.read_long(0x2000)
        pressure = pressure_raw / 1000.0  # 转换为MPa
        
        # 读取温度值
        temp_raw = self.protocol.read_long(0x2002)
        temperature = temp_raw / 10.0  # 转换为摄氏度
        
        data = {
            'pressure': pressure,
            'temperature': temperature,
            'timestamp': time.time()
        }
        
        # 集成平台设备操作记录
        if self.platform_device:
            self.platform_device.record_operation(success=True)
        
        return data
    except Exception as e:
        logger.error(f"读取数据失败: {e}")
        if self.platform_device:
            self.platform_device.record_operation(success=False)
        raise
```

### 3. 实现数据写入

```python
def write_data(self, data: Dict[str, Any]) -> bool:
    """写入设备数据"""
    if not self.is_connected:
        raise ConnectionError("设备未连接")
    
    try:
        # 写入零点校准值
        if 'zero_calibration' in data:
            zero_value = int(data['zero_calibration'] * 1000)
            self.protocol.write_long(0x3000, zero_value)
        
        # 写入量程校准值
        if 'span_calibration' in data:
            span_value = int(data['span_calibration'] * 1000)
            self.protocol.write_long(0x3002, span_value)
        
        # 集成平台设备操作记录
        if self.platform_device:
            self.platform_device.record_operation(success=True)
        
        return True
    except Exception as e:
        logger.error(f"写入数据失败: {e}")
        if self.platform_device:
            self.platform_device.record_operation(success=False)
        return False
```

### 4. 实现设备特定方法

```python
def set_pressure_range(self, min_pressure: float, max_pressure: float) -> bool:
    """设置压力量程
    
    Args:
        min_pressure: 最小压力 (MPa)
        max_pressure: 最大压力 (MPa)
        
    Returns:
        是否成功
    """
    if not self.is_connected:
        raise ConnectionError("设备未连接")
    
    try:
        # 写入量程参数
        min_value = int(min_pressure * 1000)
        max_value = int(max_pressure * 1000)
        
        self.protocol.write_long(0x4000, min_value)
        self.protocol.write_long(0x4002, max_value)
        
        # 保存配置
        self.protocol.write_register(0x4004, 0x01)
        
        logger.info(f"压力量程设置: {min_pressure}-{max_pressure} MPa")
        return True
    except Exception as e:
        logger.error(f"设置压力量程失败: {e}")
        return False

def start_calibration(self) -> bool:
    """开始校准
    
    Returns:
        是否成功
    """
    if not self.is_connected:
        raise ConnectionError("设备未连接")
    
    try:
        # 进入校准模式
        self.protocol.write_register(0x5000, 0x01)
        time.sleep(0.5)
        
        # 执行零点校准
        self.protocol.write_register(0x5001, 0x01)
        time.sleep(2.0)
        
        # 执行量程校准
        self.protocol.write_register(0x5002, 0x01)
        time.sleep(2.0)
        
        # 退出校准模式
        self.protocol.write_register(0x5000, 0x00)
        
        logger.info("校准完成")
        return True
    except Exception as e:
        logger.error(f"校准失败: {e}")
        return False
```

### 5. 实现状态监控

```python
def _get_device_status(self) -> Dict[str, Any]:
    """获取设备状态
    
    Returns:
        设备状态字典
    """
    try:
        # 读取设备状态寄存器
        status_reg = self.protocol.read_register(0x6000)
        
        # 解析状态位
        status = {
            'normal': (status_reg & 0x01) != 0,
            'calibration_mode': (status_reg & 0x02) != 0,
            'fault': (status_reg & 0x04) != 0,
            'maintenance_required': (status_reg & 0x08) != 0,
            'over_range': (status_reg & 0x10) != 0
        }
        
        return status
    except Exception as e:
        logger.error(f"获取设备状态失败: {e}")
        return {}
```

## 验证清单

使用生成的设备前，请确保完成以下验证：

- [ ] 设备连接/断开功能正常
- [ ] 数据读取功能正常
- [ ] 数据写入功能正常
- [ ] 设备特定方法实现完成
- [ ] 健康检查功能正常
- [ ] 单元测试全部通过
- [ ] 集成测试全部通过
- [ ] 平台设备状态同步正常
- [ ] 错误处理机制完善
- [ ] 日志记录完整

## 故障排除

### 问题1：导入错误

```bash
ModuleNotFoundError: No module named 'projects.encoder_test.drivers.device.pressure_sensor'
```

**解决方案**：
确保设备已正确注册到驱动工厂，检查 `driver_factory.py` 中的导入和注册代码。

### 问题2：连接失败

```bash
设备连接失败: [Errno 2] could not open port 'COM3'
```

**解决方案**：
检查串口是否被占用，确认串口号正确，确保设备已连接。

### 问题3：读取数据失败

```bash
读取数据失败: Modbus IO Error
```

**解决方案**：
检查通信参数（波特率、从站地址等）是否正确，确认设备地址配置正确。

## 进阶使用

### 1. 创建设备配置文件

```python
# config/pressure_sensor_config.py
PRESSURE_SENSOR_CONFIG = {
    'default_connection': {
        'port': 'COM3',
        'baudrate': 9600,
        'slave_id': 2,
        'timeout': 5.0
    },
    'default_params': {
        'range_min': 0.0,
        'range_max': 10.0,
        'unit': 'MPa'
    },
    'registers': {
        'pressure': 0x2000,
        'temperature': 0x2002,
        'status': 0x6000
    }
}
```

### 2. 创建设备管理器

```python
# managers/pressure_sensor_manager.py
class PressureSensorManager:
    """压力传感器管理器"""
    
    def __init__(self):
        self.sensors = {}
    
    def add_sensor(self, sensor_id: str, config: dict):
        """添加传感器"""
        sensor = PressureSensor(
            driver_id=sensor_id,
            protocol=self._create_protocol(config),
            platform_device=self._create_platform_device(config)
        )
        self.sensors[sensor_id] = sensor
    
    def get_sensor(self, sensor_id: str) -> PressureSensor:
        """获取传感器"""
        return self.sensors.get(sensor_id)
    
    def read_all_sensors(self) -> Dict[str, Dict]:
        """读取所有传感器数据"""
        results = {}
        for sensor_id, sensor in self.sensors.items():
            try:
                data = sensor.read_data()
                results[sensor_id] = data
            except Exception as e:
                results[sensor_id] = {'error': str(e)}
        return results
```

## 总结

设备生成器工具大大简化了设备开发流程：

1. **快速生成**: 一条命令生成完整的设备代码框架
2. **标准化**: 确保所有设备遵循统一的架构规范
3. **自动化**: 自动处理注册、测试等繁琐工作
4. **可扩展**: 生成的基础代码易于扩展和定制

通过这个工具，您可以专注于设备特定逻辑的实现，而无需关心架构集成等通用问题。