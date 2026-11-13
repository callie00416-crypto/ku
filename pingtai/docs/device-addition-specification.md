# 工业自动化测试平台 - 设备添加规范和流程

## 📋 目录
- [1. 设备添加规范](#1-设备添加规范)
- [2. 设备添加流程](#2-设备添加流程)
- [3. 设备开发模板](#3-设备开发模板)
- [4. 一键添加设备工具](#4-一键添加设备工具)
- [5. 设备验证清单](#5-设备验证清单)

---

## 1. 设备添加规范

### 1.1 设备分层架构

```
projects/encoder_test/drivers/device/
├── {device_name}/           # 设备目录
│   ├── __init__.py         # 包初始化
│   ├── {device_name}.py    # 设备驱动实现
│   ├── config.py           # 设备配置
│   └── constants.py        # 设备常量
```

### 1.2 设备类设计规范

#### 必须继承基类
```python
from shared.drivers.base.base_device import BaseDevice

class NewDevice(BaseDevice):
    """新设备驱动"""
    pass
```

#### 必须实现的核心方法
```python
# 生命周期方法
def connect(self) -> bool
def disconnect(self)

# 数据操作方法  
def read_data(self) -> Dict[str, Any]
def write_data(self, data: Dict[str, Any]) -> bool

# 设备控制方法
def reset(self)

# 健康检查方法
def health_check(self) -> Dict[str, Any]
```

#### 必须集成的平台能力
```python
# 平台设备集成
def __init__(self, driver_id: str, protocol=None, platform_device=None, **kwargs):
    super().__init__(driver_id, protocol, **kwargs)
    self.platform_device = platform_device  # 平台设备对象
    
# 平台状态同步
def connect(self) -> bool:
    # 设备连接逻辑
    if self.platform_device:
        self.platform_device.connect()  # 同步平台状态
        
def disconnect(self):
    # 设备断开逻辑
    if self.platform_device:
        self.platform_device.disconnect()  # 同步平台状态
```

### 1.3 命名规范

#### 文件命名
- 设备目录: 小写+下划线 `power_supply/`
- 设备文件: 小写+下划线 `power_supply.py`
- 类名: 大驼峰 `PowerSupply`

#### 方法命名
- 连接相关: `connect()`, `disconnect()`, `is_connected`
- 数据操作: `read_xxx()`, `write_xxx()`, `set_xxx()`, `get_xxx()`
- 状态管理: `health_check()`, `reset()`, `get_status()`

#### 属性命名
- 私有属性: `_xxx`
- 公共属性: `xxx`
- 常量: `XXX_YYY`

### 1.4 文档规范

#### 类文档模板
```python
class PowerSupply(BaseDevice):
    """可编程双路电源驱动（Modbus RTU）
    
    【组合关系】
    PowerSupply -> ModbusDriver -> RS485Comm
    
    【架构集成】
    - 继承 BaseDevice 基类
    - 支持平台设备生命周期管理
    - 集成平台事件系统
    - 符合工业设备规范
    
    【使用示例】
    >>> from shared.drivers.factory import CommFactory, ProtocolFactory, DeviceFactory
    >>> from projects.encoder_test.adapters.power_supply_adapter import PowerSupplyDeviceAdapter
    
    # 创建平台设备
    >>> platform_device = PowerSupplyDeviceAdapter.to_platform_device(
    ...     station_id=1,
    ...     device_code="PS-001",
    ...     device_name="可编程双路电源"
    ... )
    
    # 创建通信层
    >>> comm = CommFactory.create('rs485', port='COM4', baudrate=9600)
    >>> protocol = ProtocolFactory.create('modbus_rtu', comm=comm, slave_id=1)
    
    # 创建设备驱动
    >>> ps = PowerSupply(driver_id='power_supply', protocol=protocol)
    >>> ps.connect()
    >>> ps.set_voltage(5.0, channel=1)
    """
```

#### 方法文档模板
```python
def set_voltage(self, voltage: float, channel: int = 1) -> bool:
    """设置通道电压 (V)
    
    【架构集成】
    - 参数验证
    - 状态记录
    - 错误处理
    - 平台设备操作记录
    
    Args:
        voltage: 目标电压
        channel: 通道号 (1或2)
        
    Returns:
        是否成功
        
    Raises:
        ConnectionError: 设备未连接
        ValueError: 参数无效
    """
```

---

## 2. 设备添加流程

### 2.1 标准开发流程

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 设备分析                                            │
│  - 确定设备类型和通信协议                                    │
│  - 分析设备寄存器/命令映射                                   │
│  - 确定设备参数和状态                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: 创建设备目录结构                                    │
│  - 创建设备目录                                              │
│  - 创建基础文件                                              │
│  - 配置包初始化                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: 实现设备驱动                                        │
│  - 继承BaseDevice                                            │
│  - 实现核心方法                                              │
│  - 集成平台能力                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: 创建设备适配器                                      │
│  - 实现项目设备到平台设备的转换                              │
│  - 实现平台设备到项目设备的转换                              │
│  - 实现状态和类型映射                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 5: 注册设备驱动                                        │
│  - 在DriverFactory中注册                                    │
│  - 更新自动注册逻辑                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 6: 编写单元测试                                        │
│  - 测试设备连接/断开                                         │
│  - 测试数据读写                                              │
│  - 测试平台集成                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 7: 全链路集成测试                                      │
│  - 测试适配器转换                                            │
│  - 测试设备生命周期                                          │
│  - 测试平台集成                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 8: 文档和验证                                          │
│  - 完善代码文档                                              │
│  - 验证所有规范                                              │
│  - 性能和稳定性测试                                          │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 详细步骤说明

#### Step 1: 设备分析
```python
# 设备分析清单
device_analysis = {
    "device_name": "可编程双路电源",
    "manufacturer": "博瑞",
    "model": "程控系列",
    "protocol": "Modbus RTU",
    "communication": "RS485",
    "registers": {
        "remote_mode": 0,
        "voltage_set_ch1": 257,
        "current_set_ch1": 259,
        "voltage_out_ch1": 261,
        "current_out_ch1": 263,
        "output_ch1": 265,
        "status_ch1": 266
    },
    "parameters": {
        "max_voltage": 30.0,
        "max_current": 5.0,
        "channels": 2
    },
    "capabilities": [
        "voltage_control",
        "current_control", 
        "output_control",
        "status_monitoring"
    ]
}
```

#### Step 2: 创建设备目录结构
```bash
# 创建设备目录
mkdir -p projects/encoder_test/drivers/device/new_device

# 创建基础文件
touch projects/encoder_test/drivers/device/new_device/__init__.py
touch projects/encoder_test/drivers/device/new_device/new_device.py
touch projects/encoder_test/drivers/device/new_device/config.py
touch projects/encoder_test/drivers/device/new_device/constants.py
```

#### Step 3: 实现设备驱动
```python
# new_device.py
from shared.drivers.base.base_device import BaseDevice
from shared.drivers.protocol.modbus_rtu import ModbusDriver
import time
import logging

logger = logging.getLogger(__name__)

class NewDevice(BaseDevice):
    """新设备驱动"""
    
    def __init__(self, driver_id: str = 'new_device', protocol=None, 
                 platform_device=None, **kwargs):
        super().__init__(driver_id, protocol, **kwargs)
        self.protocol = protocol
        self.platform_device = platform_device
        
        # 设备特定状态
        self._device_state = {}
        
        # 设备信息
        self._device_info = {}
    
    def connect(self) -> bool:
        """连接设备"""
        try:
            # 连接协议层
            if not self.protocol.is_connected:
                if not self.protocol.connect():
                    return False
            
            # 设备初始化
            self._initialize_device()
            
            # 更新状态
            self._is_connected = True
            self._device_status = "connected"
            
            # 集成平台设备
            if self.platform_device:
                self.platform_device.connect()
            
            logger.info(f"设备连接成功: {self.driver_id}")
            return True
        except Exception as e:
            logger.error(f"设备连接失败: {e}")
            if self.platform_device:
                self.platform_device.disconnect()
            return False
    
    def disconnect(self):
        """断开设备连接"""
        self._is_connected = False
        self._device_status = "disconnected"
        
        if self.protocol:
            self.protocol.disconnect()
        
        if self.platform_device:
            self.platform_device.disconnect()
        
        logger.info(f"设备已断开: {self.driver_id}")
    
    def read_data(self) -> Dict[str, Any]:
        """读取设备数据"""
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        # 实现具体的数据读取逻辑
        return {}
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """写入设备数据"""
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        # 实现具体的数据写入逻辑
        return True
    
    def reset(self):
        """重置设备"""
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        # 实现设备重置逻辑
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """设备健康检查"""
        base = super().health_check()
        
        # 设备特定健康检查
        try:
            if self.is_connected:
                device_status = self._get_device_status()
                base.update({
                    'device_status': device_status,
                    'device_info': self._device_info
                })
        except Exception as e:
            base['health_status'] = 'error'
            base['error_message'] = str(e)
        
        return base
    
    def _initialize_device(self):
        """初始化设备"""
        # 设备初始化逻辑
        pass
    
    def _get_device_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        # 设备状态获取逻辑
        return {}
```

#### Step 4: 创建设备适配器
```python
# projects/encoder_test/adapters/new_device_adapter.py
from typing import Dict, Any, Optional
from platform.domain.device.device import Device, DeviceConfig
from platform.domain.common.enums import DeviceType, ProtocolType

class NewDeviceAdapter:
    """新设备适配器"""
    
    @staticmethod
    def to_platform_device(
        station_id: int,
        device_code: str,
        device_name: str,
        protocol: ProtocolType = ProtocolType.MODBUS_RTU,
        connection_params: Optional[Dict[str, Any]] = None,
        device_params: Optional[Dict[str, Any]] = None
    ) -> Device:
        """将项目设备转换为平台设备"""
        config = DeviceConfig(
            protocol=protocol.value,
            connection_params=connection_params or {},
            device_params=device_params or {},
            timeout=5.0,
            retry_count=3
        )
        
        return Device.create(
            station_id=station_id,
            code=device_code,
            name=device_name,
            device_type=DeviceType.NEW_DEVICE,
            protocol=protocol,
            config=config
        )
    
    @staticmethod
    def from_platform_device(platform_device: Device) -> Dict[str, Any]:
        """将平台设备转换为项目设备DTO"""
        return {
            "device_id": platform_device.id,
            "station_id": platform_device.station_id,
            "code": platform_device.code,
            "name": platform_device.name,
            "device_type": platform_device.device_type.value,
            "protocol": platform_device.protocol.value,
            "status": platform_device.status.value,
            "connect_status": platform_device.connect_status.value,
            "is_connected": platform_device.is_connected,
            "created_at": platform_device.created_at,
            "updated_at": platform_device.updated_at
        }
    
    @staticmethod
    def create_connection_params(**kwargs) -> Dict[str, Any]:
        """创建连接参数"""
        return {
            'port': kwargs.get('port', 'COM1'),
            'baudrate': kwargs.get('baudrate', 9600),
            'slave_id': kwargs.get('slave_id', 1),
            'timeout': kwargs.get('timeout', 5.0)
        }
    
    @staticmethod
    def create_device_params(**kwargs) -> Dict[str, Any]:
        """创建设备参数"""
        return {
            'channels': kwargs.get('channels', 1),
            'max_voltage': kwargs.get('max_voltage', 30.0),
            'max_current': kwargs.get('max_current', 5.0)
        }
```

#### Step 5: 注册设备驱动
```python
# projects/encoder_test/drivers/factory/driver_factory.py
def auto_register_drivers():
    """自动注册常用驱动类型"""
    try:
        # 通讯层驱动
        from shared.drivers.comm.rs485_comm import RS485Comm
        from shared.drivers.comm.tcp_comm import TCPComm
        from shared.drivers.comm.can_comm import CANComm
        
        # 协议层驱动
        from shared.drivers.protocol.modbus_rtu import ModbusDriver
        
        # 设备层驱动
        from projects.encoder_test.drivers.device.encoder.encoder import EncoderDriver
        from projects.encoder_test.drivers.device.motor.servo_motor import ServoMotor
        from projects.encoder_test.drivers.device.power_supply.power_supply import PowerSupply
        from projects.encoder_test.drivers.device.new_device.new_device import NewDevice  # 新增
        
        # 注册通讯驱动
        DriverFactory.register_comm('rs485', RS485Comm)
        DriverFactory.register_comm('tcp', TCPComm)
        DriverFactory.register_comm('can', CANComm)
        
        # 注册协议驱动
        DriverFactory.register_protocol('modbus', ModbusDriver)
        
        # 注册设备驱动
        DriverFactory.register_device('encoder', EncoderDriver)
        DriverFactory.register_device('motor', ServoMotor)
        DriverFactory.register_device('power_supply', PowerSupply)
        DriverFactory.register_device('new_device', NewDevice)  # 新增
        
        logger.info("常用驱动类型已自动注册")
    except ImportError as e:
        logger.warning(f"驱动自动注册失败: {e}")
```

#### Step 6: 编写单元测试
```python
# tests/device/test_new_device.py
import unittest
from unittest.mock import Mock, MagicMock
from projects.encoder_test.drivers.device.new_device.new_device import NewDevice

class TestNewDevice(unittest.TestCase):
    """新设备单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_protocol = Mock()
        self.mock_protocol.is_connected = False
        self.mock_protocol.connect.return_value = True
        self.mock_protocol.disconnect.return_value = None
        
        self.device = NewDevice(
            driver_id='test_new_device',
            protocol=self.mock_protocol
        )
    
    def test_connect(self):
        """测试设备连接"""
        result = self.device.connect()
        self.assertTrue(result)
        self.assertTrue(self.device.is_connected)
        self.assertEqual(self.device.device_status, "connected")
    
    def test_disconnect(self):
        """测试设备断开"""
        self.device.connect()
        self.device.disconnect()
        self.assertFalse(self.device.is_connected)
        self.assertEqual(self.device.device_status, "disconnected")
    
    def test_read_data(self):
        """测试读取数据"""
        self.device.connect()
        data = self.device.read_data()
        self.assertIsInstance(data, dict)
    
    def test_write_data(self):
        """测试写入数据"""
        self.device.connect()
        result = self.device.write_data({"test": "data"})
        self.assertTrue(result)
    
    def test_health_check(self):
        """测试健康检查"""
        self.device.connect()
        health = self.device.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('is_connected', health)
        self.assertTrue(health['is_connected'])

if __name__ == '__main__':
    unittest.main()
```

#### Step 7: 全链路集成测试
```python
# tests/integration/test_new_device_full_link.py
import sys
from pathlib import Path
import logging

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_adapter_conversion():
    """测试适配器转换"""
    from projects.encoder_test.adapters.new_device_adapter import NewDeviceAdapter
    from platform.domain.common.enums import ProtocolType
    
    platform_device = NewDeviceAdapter.to_platform_device(
        station_id=1,
        device_code="NEW-001",
        device_name="新设备",
        protocol=ProtocolType.MODBUS_RTU
    )
    
    assert platform_device is not None
    assert platform_device.code == "NEW-001"
    
    device_dto = NewDeviceAdapter.from_platform_device(platform_device)
    assert device_dto['code'] == "NEW-001"
    
    logger.info("[PASS] 适配器转换测试")

def test_device_lifecycle():
    """测试设备生命周期"""
    from projects.encoder_test.drivers.device.new_device.new_device import NewDevice
    from platform.domain.device.device import Device
    
    platform_device = Device.create(
        station_id=1,
        code="NEW-001",
        name="新设备",
        device_type=DeviceType.NEW_DEVICE,
        protocol=ProtocolType.MODBUS_RTU,
        config=None
    )
    
    mock_protocol = Mock()
    mock_protocol.is_connected = False
    mock_protocol.connect.return_value = True
    
    device = NewDevice(
        driver_id='test_new_device',
        protocol=mock_protocol,
        platform_device=platform_device
    )
    
    # 测试连接
    assert device.connect()
    assert device.is_connected
    assert platform_device.is_connected
    
    # 测试断开
    device.disconnect()
    assert not device.is_connected
    assert not platform_device.is_connected
    
    logger.info("[PASS] 设备生命周期测试")

def main():
    """运行所有测试"""
    logger.info("开始新设备全链路测试")
    
    try:
        test_adapter_conversion()
        test_device_lifecycle()
        
        logger.info("[SUCCESS] 所有测试通过！")
        return 0
    except Exception as e:
        logger.error(f"[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

---

## 3. 设备开发模板

### 3.1 设备类模板

```python
# {device_name}.py
"""
{device_name} - 设备驱动

【设备信息】
- 制造商: {manufacturer}
- 型号: {model}
- 通信协议: {protocol}
- 通信接口: {communication}

【架构集成】
- 继承 BaseDevice 基类
- 支持平台设备生命周期管理
- 集成平台事件系统
- 符合工业设备规范
"""
from shared.drivers.base.base_device import BaseDevice
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class {DeviceName}(BaseDevice):
    """{device_description}
    
    【组合关系】
    {DeviceName} -> {Protocol} -> {Comm}
    
    【架构集成】
    - 继承 BaseDevice 基类
    - 支持平台设备生命周期管理
    - 集成平台事件系统
    - 符合工业设备规范
    
    【使用示例】
    >>> from shared.drivers.factory import CommFactory, ProtocolFactory
    >>> from projects.encoder_test.adapters.{device_name}_adapter import {DeviceName}Adapter
    
    # 创建平台设备
    >>> platform_device = {DeviceName}Adapter.to_platform_device(
    ...     station_id=1,
    ...     device_code="{DEVICE_CODE}",
    ...     device_name="{device_name}"
    ... )
    
    # 创建通信层
    >>> comm = CommFactory.create('{comm_type}', port='COM1', baudrate=9600)
    >>> protocol = ProtocolFactory.create('{protocol}', comm=comm, slave_id=1)
    
    # 创建设备驱动
    >>> device = {DeviceName}(driver_id='{device_name}', protocol=protocol)
    >>> device.connect()
    """
    
    # 设备常量定义
    {DEVICE_CONSTANTS}
    
    def __init__(self, driver_id: str = '{device_name}', protocol=None, 
                 platform_device=None, **kwargs):
        """
        Args:
            driver_id: 驱动ID
            protocol: 协议对象
            platform_device: 平台设备对象（可选）
            **kwargs: 其他参数
        """
        super().__init__(driver_id, protocol, **kwargs)
        self.protocol = protocol
        self.platform_device = platform_device
        
        # 设备特定状态
        self._device_state = {}
        
        # 设备信息
        self._device_info = {
            'manufacturer': '{manufacturer}',
            'model': '{model}',
            'protocol': '{protocol}',
            'communication': '{communication}'
        }
    
    def connect(self) -> bool:
        """连接设备
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持平台设备状态管理
        - 集成平台事件发布
        """
        try:
            # 更新状态为连接中
            self._device_status = "connecting"
            
            # 连接协议层
            if not self.protocol.is_connected:
                if not self.protocol.connect():
                    self._device_status = "fault"
                    if self.platform_device:
                        self.platform_device.disconnect()
                    return False
            
            # 初始化设备
            self._initialize_device()
            
            # 更新状态为已连接
            self._is_connected = True
            self._device_status = "connected"
            
            # 集成平台设备
            if self.platform_device:
                self.platform_device.connect()
            
            logger.info(f"设备连接成功: {self.driver_id}")
            return True
        except Exception as e:
            logger.error(f"设备连接失败: {e}")
            self._device_status = "fault"
            self.increment_error()
            
            if self.platform_device:
                self.platform_device.disconnect()
            
            return False
    
    def disconnect(self):
        """断开设备连接
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持平台设备状态管理
        - 集成平台事件发布
        """
        self._is_connected = False
        self._device_status = "disconnected"
        
        # 断开协议层
        if self.protocol:
            self.protocol.disconnect()
        
        # 集成平台设备
        if self.platform_device:
            self.platform_device.disconnect()
        
        logger.info(f"设备已断开: {self.driver_id}")
    
    def read_data(self) -> Dict[str, Any]:
        """读取设备数据
        
        Returns:
            设备数据字典
        """
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        try:
            # 实现具体的数据读取逻辑
            data = {}
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return data
        except Exception as e:
            logger.error(f"读取数据失败: {e}")
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            raise
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """写入设备数据
        
        Args:
            data: 要写入的数据
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        try:
            # 实现具体的数据写入逻辑
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return True
        except Exception as e:
            logger.error(f"写入数据失败: {e}")
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            return False
    
    def reset(self):
        """重置设备"""
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        try:
            # 实现设备重置逻辑
            logger.info(f"设备重置: {self.driver_id}")
        except Exception as e:
            logger.error(f"设备重置失败: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """设备健康检查
        
        Returns:
            健康状态字典
        """
        base = super().health_check()
        
        # 设备特定健康检查
        try:
            if self.is_connected:
                device_status = self._get_device_status()
                base.update({
                    'device_status': device_status,
                    'device_info': self._device_info
                })
        except Exception as e:
            base['health_status'] = 'error'
            base['error_message'] = str(e)
        
        return base
    
    def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息
        
        Returns:
            设备信息字典
        """
        base_info = {
            'driver_id': self.driver_id,
            'device_info': self._device_info,
            'device_status': self._device_status,
            'is_connected': self.is_connected
        }
        
        if self.platform_device:
            base_info['platform_device'] = {
                'device_id': self.platform_device.id,
                'code': self.platform_device.code,
                'name': self.platform_device.name,
                'is_connected': self.platform_device.is_connected,
                'status': self.platform_device.status.value
            }
        
        return base_info
    
    def _initialize_device(self):
        """初始化设备"""
        # 设备初始化逻辑
        pass
    
    def _get_device_status(self) -> Dict[str, Any]:
        """获取设备状态
        
        Returns:
            设备状态字典
        """
        # 设备状态获取逻辑
        return {}
    
    # 设备特定方法
    {DEVICE_SPECIFIC_METHODS}
```

### 3.2 设备适配器模板

```python
# {device_name}_adapter.py
"""
{device_name}适配器 - Device Adapter

【职责】
将项目{device_name}转换为平台通用设备
{DeviceName} → Platform Device

【设计原则】
- DTO转换
- 参数映射
- 配置转换
- 禁止业务规则
- 禁止Runtime控制
- 禁止Repository操作
"""
from typing import Dict, Any, Optional
from platform.domain.device.device import Device, DeviceConfig
from platform.domain.common.enums import DeviceType, ProtocolType

class {DeviceName}Adapter:
    """{device_name}设备适配器"""
    
    @staticmethod
    def to_platform_device(
        station_id: int,
        device_code: str,
        device_name: str,
        protocol: ProtocolType = ProtocolType.MODBUS_RTU,
        connection_params: Optional[Dict[str, Any]] = None,
        device_params: Optional[Dict[str, Any]] = None
    ) -> Device:
        """将项目{device_name}转换为平台设备
        
        Args:
            station_id: 工位ID
            device_code: 设备编号
            device_name: 设备名称
            protocol: 协议类型
            connection_params: 连接参数
            device_params: 设备参数
            
        Returns:
            平台设备对象
        """
        config = DeviceConfig(
            protocol=protocol.value,
            connection_params=connection_params or {},
            device_params=device_params or {},
            timeout=5.0,
            retry_count=3
        )
        
        return Device.create(
            station_id=station_id,
            code=device_code,
            name=device_name,
            device_type=DeviceType.{DEVICE_TYPE},
            protocol=protocol,
            config=config
        )
    
    @staticmethod
    def from_platform_device(platform_device: Device) -> Dict[str, Any]:
        """将平台设备转换为项目设备DTO
        
        Args:
            platform_device: 平台设备对象
            
        Returns:
            项目设备DTO
        """
        return {
            "device_id": platform_device.id,
            "station_id": platform_device.station_id,
            "code": platform_device.code,
            "name": platform_device.name,
            "device_type": platform_device.device_type.value,
            "protocol": platform_device.protocol.value,
            "status": platform_device.status.value,
            "connect_status": platform_device.connect_status.value,
            "is_connected": platform_device.is_connected,
            "created_at": platform_device.created_at,
            "updated_at": platform_device.updated_at
        }
    
    @staticmethod
    def create_connection_params(**kwargs) -> Dict[str, Any]:
        """创建连接参数
        
        Args:
            **kwargs: 连接参数
            
        Returns:
            连接参数字典
        """
        return {
            'port': kwargs.get('port', 'COM1'),
            'baudrate': kwargs.get('baudrate', 9600),
            'slave_id': kwargs.get('slave_id', 1),
            'timeout': kwargs.get('timeout', 5.0)
        }
    
    @staticmethod
    def create_device_params(**kwargs) -> Dict[str, Any]:
        """创建设备参数
        
        Args:
            **kwargs: 设备参数
            
        Returns:
            设备参数字典
        """
        return {
            # 设备特定参数
        }
```

---

## 4. 一键添加设备工具

### 4.1 设备生成器脚本

```python
# tools/device_generator.py
"""
设备生成器 - 一键生成设备代码

【功能】
- 自动生成设备目录结构
- 自动生成设备驱动代码
- 自动生成设备适配器代码
- 自动生成测试代码
- 自动注册设备驱动
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any
import argparse

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class DeviceGenerator:
    """设备生成器"""
    
    def __init__(self, device_name: str, config: Dict[str, Any]):
        """
        Args:
            device_name: 设备名称（小写+下划线）
            config: 设备配置
        """
        self.device_name = device_name
        self.config = config
        self.class_name = self._to_class_name(device_name)
        self.device_dir = project_root / "projects/encoder_test/drivers/device" / device_name
        self.adapter_dir = project_root / "projects/encoder_test/adapters"
    
    def _to_class_name(self, name: str) -> str:
        """转换为类名"""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def generate(self):
        """生成设备代码"""
        print(f"开始生成设备: {self.device_name}")
        
        # 创建目录结构
        self._create_directory_structure()
        
        # 生成设备驱动
        self._generate_device_driver()
        
        # 生成设备适配器
        self._generate_device_adapter()
        
        # 生成测试代码
        self._generate_tests()
        
        # 注册设备驱动
        self._register_device()
        
        print(f"设备 {self.device_name} 生成完成！")
    
    def _create_directory_structure(self):
        """创建目录结构"""
        print(f"创建目录结构: {self.device_dir}")
        self.device_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建__init__.py
        init_file = self.device_dir / "__init__.py"
        init_file.write_text(f"""
\"\"\"{self.device_name} - 设备驱动包\"\"\"
from .{self.device_name} import {self.class_name}

__all__ = ['{self.class_name}']
""")
    
    def _generate_device_driver(self):
        """生成设备驱动"""
        print(f"生成设备驱动: {self.device_name}.py")
        
        device_file = self.device_dir / f"{self.device_name}.py"
        device_content = self._get_device_template()
        device_file.write_text(device_content)
    
    def _generate_device_adapter(self):
        """生成设备适配器"""
        print(f"生成设备适配器: {self.device_name}_adapter.py")
        
        adapter_file = self.adapter_dir / f"{self.device_name}_adapter.py"
        adapter_content = self._get_adapter_template()
        adapter_file.write_text(adapter_content)
    
    def _generate_tests(self):
        """生成测试代码"""
        print(f"生成测试代码")
        
        # 创建测试目录
        test_dir = project_root / "tests" / "device"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成单元测试
        unit_test_file = test_dir / f"test_{self.device_name}.py"
        unit_test_content = self._get_unit_test_template()
        unit_test_file.write_text(unit_test_content)
        
        # 生成集成测试
        integration_test_file = test_dir / f"test_{self.device_name}_full_link.py"
        integration_test_content = self._get_integration_test_template()
        integration_test_file.write_text(integration_test_content)
    
    def _register_device(self):
        """注册设备驱动"""
        print(f"注册设备驱动")
        
        factory_file = project_root / "projects/encoder_test/drivers/factory/driver_factory.py"
        
        # 读取现有内容
        with open(factory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加导入
        import_line = f"from projects.encoder_test.drivers.device.{self.device_name}.{self.device_name} import {self.class_name}"
        if import_line not in content:
            # 在现有导入后添加新导入
            lines = content.split('\n')
            import_section_end = 0
            for i, line in enumerate(lines):
                if 'from projects.encoder_test.drivers.device' in line:
                    import_section_end = i + 1
            
            lines.insert(import_section_end, import_line)
            content = '\n'.join(lines)
        
        # 添加注册
        register_line = f"DriverFactory.register_device('{self.device_name}', {self.class_name})"
        if register_line not in content:
            # 在现有注册后添加新注册
            lines = content.split('\n')
            register_section_end = 0
            for i, line in enumerate(lines):
                if 'DriverFactory.register_device' in line:
                    register_section_end = i + 1
            
            lines.insert(register_section_end, register_line)
            content = '\n'.join(lines)
        
        # 写回文件
        with open(factory_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _get_device_template(self) -> str:
        """获取设备模板"""
        return f'''
"""
{self.device_name} - 设备驱动

【设备信息】
- 制造商: {self.config.get('manufacturer', 'Unknown')}
- 型号: {self.config.get('model', 'Unknown')}
- 通信协议: {self.config.get('protocol', 'Unknown')}
- 通信接口: {self.config.get('communication', 'Unknown')}

【架构集成】
- 继承 BaseDevice 基类
- 支持平台设备生命周期管理
- 集成平台事件系统
- 符合工业设备规范
"""
from shared.drivers.base.base_device import BaseDevice
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class {self.class_name}(BaseDevice):
    """{self.config.get('description', self.device_name)}
    
    【组合关系】
    {self.class_name} -> {self.config.get('protocol', 'Protocol')} -> {self.config.get('communication', 'Comm')}
    
    【架构集成】
    - 继承 BaseDevice 基类
    - 支持平台设备生命周期管理
    - 集成平台事件系统
    - 符合工业设备规范
    
    【使用示例】
    >>> from shared.drivers.factory import CommFactory, ProtocolFactory
    >>> from projects.encoder_test.adapters.{self.device_name}_adapter import {self.class_name}Adapter
    
    # 创建平台设备
    >>> platform_device = {self.class_name}Adapter.to_platform_device(
    ...     station_id=1,
    ...     device_code="{self.device_name.upper()}-001",
    ...     device_name="{self.config.get('description', self.device_name)}"
    ... )
    
    # 创建通信层
    >>> comm = CommFactory.create('{self.config.get('communication', 'rs485')}', port='COM1', baudrate=9600)
    >>> protocol = ProtocolFactory.create('{self.config.get('protocol', 'modbus_rtu')}', comm=comm, slave_id=1)
    
    # 创建设备驱动
    >>> device = {self.class_name}(driver_id='{self.device_name}', protocol=protocol)
    >>> device.connect()
    """
    
    def __init__(self, driver_id: str = '{self.device_name}', protocol=None, 
                 platform_device=None, **kwargs):
        """
        Args:
            driver_id: 驱动ID
            protocol: 协议对象
            platform_device: 平台设备对象（可选）
            **kwargs: 其他参数
        """
        super().__init__(driver_id, protocol, **kwargs)
        self.protocol = protocol
        self.platform_device = platform_device
        
        # 设备特定状态
        self._device_state = {{}}
        
        # 设备信息
        self._device_info = {{
            'manufacturer': '{self.config.get('manufacturer', 'Unknown')}',
            'model': '{self.config.get('model', 'Unknown')}',
            'protocol': '{self.config.get('protocol', 'Unknown')}',
            'communication': '{self.config.get('communication', 'Unknown')}'
        }}
    
    def connect(self) -> bool:
        """连接设备
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持平台设备状态管理
        - 集成平台事件发布
        """
        try:
            # 更新状态为连接中
            self._device_status = "connecting"
            
            # 连接协议层
            if not self.protocol.is_connected:
                if not self.protocol.connect():
                    self._device_status = "fault"
                    if self.platform_device:
                        self.platform_device.disconnect()
                    return False
            
            # 初始化设备
            self._initialize_device()
            
            # 更新状态为已连接
            self._is_connected = True
            self._device_status = "connected"
            
            # 集成平台设备
            if self.platform_device:
                self.platform_device.connect()
            
            logger.info(f"设备连接成功: {{self.driver_id}}")
            return True
        except Exception as e:
            logger.error(f"设备连接失败: {{e}}")
            self._device_status = "fault"
            self.increment_error()
            
            if self.platform_device:
                self.platform_device.disconnect()
            
            return False
    
    def disconnect(self):
        """断开设备连接
        
        【架构集成】
        - 遵循工业设备生命周期规范
        - 支持平台设备状态管理
        - 集成平台事件发布
        """
        self._is_connected = False
        self._device_status = "disconnected"
        
        # 断开协议层
        if self.protocol:
            self.protocol.disconnect()
        
        # 集成平台设备
        if self.platform_device:
            self.platform_device.disconnect()
        
        logger.info(f"设备已断开: {{self.driver_id}}")
    
    def read_data(self) -> Dict[str, Any]:
        """读取设备数据
        
        Returns:
            设备数据字典
        """
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        try:
            # 实现具体的数据读取逻辑
            data = {{}}
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return data
        except Exception as e:
            logger.error(f"读取数据失败: {{e}}")
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            raise
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """写入设备数据
        
        Args:
            data: 要写入的数据
            
        Returns:
            是否成功
        """
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        try:
            # 实现具体的数据写入逻辑
            
            # 集成平台设备操作记录
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return True
        except Exception as e:
            logger.error(f"写入数据失败: {{e}}")
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            return False
    
    def reset(self):
        """重置设备"""
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        try:
            # 实现设备重置逻辑
            logger.info(f"设备重置: {{self.driver_id}}")
        except Exception as e:
            logger.error(f"设备重置失败: {{e}}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """设备健康检查
        
        Returns:
            健康状态字典
        """
        base = super().health_check()
        
        # 设备特定健康检查
        try:
            if self.is_connected:
                device_status = self._get_device_status()
                base.update({{
                    'device_status': device_status,
                    'device_info': self._device_info
                }})
        except Exception as e:
            base['health_status'] = 'error'
            base['error_message'] = str(e)
        
        return base
    
    def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息
        
        Returns:
            设备信息字典
        """
        base_info = {{
            'driver_id': self.driver_id,
            'device_info': self._device_info,
            'device_status': self._device_status,
            'is_connected': self.is_connected
        }}
        
        if self.platform_device:
            base_info['platform_device'] = {{
                'device_id': self.platform_device.id,
                'code': self.platform_device.code,
                'name': self.platform_device.name,
                'is_connected': self.platform_device.is_connected,
                'status': self.platform_device.status.value
            }}
        
        return base_info
    
    def _initialize_device(self):
        """初始化设备"""
        # 设备初始化逻辑
        pass
    
    def _get_device_status(self) -> Dict[str, Any]:
        """获取设备状态
        
        Returns:
            设备状态字典
        """
        # 设备状态获取逻辑
        return {{}}
'''
    
    def _get_adapter_template(self) -> str:
        """获取适配器模板"""
        return f'''
"""
{self.device_name}适配器 - Device Adapter

【职责】
将项目{self.device_name}转换为平台通用设备
{self.class_name} → Platform Device

【设计原则】
- DTO转换
- 参数映射
- 配置转换
- 禁止业务规则
- 禁止Runtime控制
- 禁止Repository操作
"""
from typing import Dict, Any, Optional
from platform.domain.device.device import Device, DeviceConfig
from platform.domain.common.enums import DeviceType, ProtocolType

class {self.class_name}Adapter:
    """{self.device_name}设备适配器"""
    
    @staticmethod
    def to_platform_device(
        station_id: int,
        device_code: str,
        device_name: str,
        protocol: ProtocolType = ProtocolType.MODBUS_RTU,
        connection_params: Optional[Dict[str, Any]] = None,
        device_params: Optional[Dict[str, Any]] = None
    ) -> Device:
        """将项目{self.device_name}转换为平台设备
        
        Args:
            station_id: 工位ID
            device_code: 设备编号
            device_name: 设备名称
            protocol: 协议类型
            connection_params: 连接参数
            device_params: 设备参数
            
        Returns:
            平台设备对象
        """
        config = DeviceConfig(
            protocol=protocol.value,
            connection_params=connection_params or {{}},
            device_params=device_params or {{}},
            timeout=5.0,
            retry_count=3
        )
        
        return Device.create(
            station_id=station_id,
            code=device_code,
            name=device_name,
            device_type=DeviceType.{self.device_name.upper()},
            protocol=protocol,
            config=config
        )
    
    @staticmethod
    def from_platform_device(platform_device: Device) -> Dict[str, Any]:
        """将平台设备转换为项目设备DTO
        
        Args:
            platform_device: 平台设备对象
            
        Returns:
            项目设备DTO
        """
        return {{
            "device_id": platform_device.id,
            "station_id": platform_device.station_id,
            "code": platform_device.code,
            "name": platform_device.name,
            "device_type": platform_device.device_type.value,
            "protocol": platform_device.protocol.value,
            "status": platform_device.status.value,
            "connect_status": platform_device.connect_status.value,
            "is_connected": platform_device.is_connected,
            "created_at": platform_device.created_at,
            "updated_at": platform_device.updated_at
        }}
    
    @staticmethod
    def create_connection_params(**kwargs) -> Dict[str, Any]:
        """创建连接参数
        
        Args:
            **kwargs: 连接参数
            
        Returns:
            连接参数字典
        """
        return {{
            'port': kwargs.get('port', 'COM1'),
            'baudrate': kwargs.get('baudrate', 9600),
            'slave_id': kwargs.get('slave_id', 1),
            'timeout': kwargs.get('timeout', 5.0)
        }}
    
    @staticmethod
    def create_device_params(**kwargs) -> Dict[str, Any]:
        """创建设备参数
        
        Args:
            **kwargs: 设备参数
            
        Returns:
            设备参数字典
        """
        return {{
            # 设备特定参数
        }}
'''
    
    def _get_unit_test_template(self) -> str:
        """获取单元测试模板"""
        return f'''
"""
{self.device_name} 单元测试
"""
import unittest
from unittest.mock import Mock, MagicMock
from projects.encoder_test.drivers.device.{self.device_name}.{self.device_name} import {self.class_name}

class Test{self.class_name}(unittest.TestCase):
    """{self.class_name}单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_protocol = Mock()
        self.mock_protocol.is_connected = False
        self.mock_protocol.connect.return_value = True
        self.mock_protocol.disconnect.return_value = None
        
        self.device = {self.class_name}(
            driver_id='test_{self.device_name}',
            protocol=self.mock_protocol
        )
    
    def test_connect(self):
        """测试设备连接"""
        result = self.device.connect()
        self.assertTrue(result)
        self.assertTrue(self.device.is_connected)
        self.assertEqual(self.device.device_status, "connected")
    
    def test_disconnect(self):
        """测试设备断开"""
        self.device.connect()
        self.device.disconnect()
        self.assertFalse(self.device.is_connected)
        self.assertEqual(self.device.device_status, "disconnected")
    
    def test_read_data(self):
        """测试读取数据"""
        self.device.connect()
        data = self.device.read_data()
        self.assertIsInstance(data, dict)
    
    def test_write_data(self):
        """测试写入数据"""
        self.device.connect()
        result = self.device.write_data({{"test": "data"}})
        self.assertTrue(result)
    
    def test_health_check(self):
        """测试健康检查"""
        self.device.connect()
        health = self.device.health_check()
        self.assertIn('driver_id', health)
        self.assertIn('is_connected', health)
        self.assertTrue(health['is_connected'])

if __name__ == '__main__':
    unittest.main()
'''
    
    def _get_integration_test_template(self) -> str:
        """获取集成测试模板"""
        return f'''
"""
{self.device_name} 全链路集成测试
"""
import sys
from pathlib import Path
import logging
from unittest.mock import Mock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_adapter_conversion():
    """测试适配器转换"""
    from projects.encoder_test.adapters.{self.device_name}_adapter import {self.class_name}Adapter
    from platform.domain.common.enums import ProtocolType
    
    platform_device = {self.class_name}Adapter.to_platform_device(
        station_id=1,
        device_code="{self.device_name.upper()}-001",
        device_name="{self.config.get('description', self.device_name)}",
        protocol=ProtocolType.MODBUS_RTU
    )
    
    assert platform_device is not None
    assert platform_device.code == "{self.device_name.upper()}-001"
    
    device_dto = {self.class_name}Adapter.from_platform_device(platform_device)
    assert device_dto['code'] == "{self.device_name.upper()}-001"
    
    logger.info("[PASS] 适配器转换测试")

def test_device_lifecycle():
    """测试设备生命周期"""
    from projects.encoder_test.drivers.device.{self.device_name}.{self.device_name} import {self.class_name}
    from platform.domain.device.device import Device
    from platform.domain.common.enums import DeviceType, ProtocolType
    
    platform_device = Device.create(
        station_id=1,
        code="{self.device_name.upper()}-001",
        name="{self.config.get('description', self.device_name)}",
        device_type=DeviceType.{self.device_name.upper()},
        protocol=ProtocolType.MODBUS_RTU,
        config=None
    )
    
    mock_protocol = Mock()
    mock_protocol.is_connected = False
    mock_protocol.connect.return_value = True
    
    device = {self.class_name}(
        driver_id='test_{self.device_name}',
        protocol=mock_protocol,
        platform_device=platform_device
    )
    
    # 测试连接
    assert device.connect()
    assert device.is_connected
    assert platform_device.is_connected
    
    # 测试断开
    device.disconnect()
    assert not device.is_connected
    assert not platform_device.is_connected
    
    logger.info("[PASS] 设备生命周期测试")

def main():
    """运行所有测试"""
    logger.info("开始{self.device_name}全链路测试")
    
    try:
        test_adapter_conversion()
        test_device_lifecycle()
        
        logger.info("[SUCCESS] 所有测试通过！")
        return 0
    except Exception as e:
        logger.error(f"[FAIL] 测试失败: {{e}}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
'''


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='设备生成器 - 一键生成设备代码')
    parser.add_argument('device_name', help='设备名称（小写+下划线，如：new_device）')
    parser.add_argument('--manufacturer', help='制造商')
    parser.add_argument('--model', help='设备型号')
    parser.add_argument('--protocol', help='通信协议（如：modbus_rtu）')
    parser.add_argument('--communication', help='通信接口（如：rs485）')
    parser.add_argument('--description', help='设备描述')
    
    args = parser.parse_args()
    
    # 构建设备配置
    config = {
        'manufacturer': args.manufacturer or 'Unknown',
        'model': args.model or 'Unknown',
        'protocol': args.protocol or 'modbus_rtu',
        'communication': args.communication or 'rs485',
        'description': args.description or args.device_name
    }
    
    # 生成设备
    generator = DeviceGenerator(args.device_name, config)
    generator.generate()


if __name__ == '__main__':
    main()
```

### 4.2 使用示例

```bash
# 基本使用
python tools/device_generator.py new_device

# 完整参数
python tools/device_generator.py temperature_sensor \
    --manufacturer "西门子" \
    --model "SITRANS T" \
    --protocol "modbus_rtu" \
    --communication "rs485" \
    --description "温度传感器"
```

---

## 5. 设备验证清单

### 5.1 代码规范验证

- [ ] 继承BaseDevice基类
- [ ] 实现所有必需方法
- [ ] 集成平台设备生命周期
- [ ] 使用正确的命名规范
- [ ] 完整的文档注释
- [ ] 正确的错误处理

### 5.2 功能验证

- [ ] 设备连接/断开功能正常
- [ ] 数据读写功能正常
- [ ] 设备重置功能正常
- [ ] 健康检查功能正常
- [ ] 参数验证功能正常
- [ ] 错误处理功能正常

### 5.3 平台集成验证

- [ ] 适配器转换功能正常
- [ ] 平台设备状态同步正常
- [ ] 平台事件发布正常
- [ ] 平台操作记录正常
- [ ] 平台设备指标正常

### 5.4 测试验证

- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 全链路测试通过
- [ ] 测试覆盖率达标
- [ ] 性能测试通过

### 5.5 文档验证

- [ ] 代码文档完整
- [ ] 使用示例清晰
- [ ] 架构说明准确
- [ ] 接口文档完整

---

## 📝 总结

本规范提供了完整的设备添加流程和工具支持，包括：

1. **标准化规范**: 统一的设备开发标准和命名规范
2. **完整流程**: 从分析到部署的完整开发流程
3. **代码模板**: 可复用的设备和适配器模板
4. **自动化工具**: 一键生成设备代码的工具
5. **验证清单**: 确保设备质量的验证标准

使用本规范，可以快速、标准化地添加新设备，确保所有设备都符合平台架构要求，并充分利用平台能力。