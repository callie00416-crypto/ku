---
name: "device-generator"
description: "生成工业设备驱动代码和规范文档。调用当需要添加新设备、创建设备驱动或查看设备添加流程时使用。"
---

# 设备生成器 - 工业设备驱动开发工具

## 📋 Skill 概述

这个skill提供工业自动化测试平台的设备添加完整解决方案，包括标准化规范、开发流程、代码模板和自动化工具。

## 🎯 适用场景

**在以下情况调用此skill：**

- 需要添加新的工业设备驱动
- 需要创建设备适配器
- 需要了解设备添加规范和流程
- 需要使用设备生成器工具
- 需要验证设备代码质量

## 📚 核心内容

### 1. 设备添加规范

#### 架构要求
- 必须继承 `BaseDevice` 基类
- 必须集成平台设备生命周期管理
- 必须支持平台事件系统
- 必须符合工业设备生命周期规范

#### 命名规范
- 设备目录: 小写+下划线 `power_supply/`
- 设备文件: 小写+下划线 `power_supply.py`
- 类名: 大驼峰 `PowerSupply`

#### 必须实现的方法
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

### 2. 设备添加流程（8步标准流程）

```
Step 1: 设备分析 → Step 2: 创建目录结构 → Step 3: 实现设备驱动 
→ Step 4: 创建适配器 → Step 5: 注册驱动 → Step 6: 编写单元测试 
→ Step 7: 全链路测试 → Step 8: 文档验证
```

#### 详细步骤说明

**Step 1: 设备分析**
- 确定设备类型和通信协议
- 分析设备寄存器/命令映射
- 确定设备参数和状态

**Step 2: 创建设备目录结构**
```bash
mkdir -p projects/encoder_test/drivers/device/new_device
touch projects/encoder_test/drivers/device/new_device/__init__.py
touch projects/encoder_test/drivers/device/new_device/new_device.py
```

**Step 3: 实现设备驱动**
- 继承BaseDevice
- 实现核心方法
- 集成平台能力

**Step 4: 创建设备适配器**
- 实现项目设备到平台设备的转换
- 实现平台设备到项目设备的转换
- 实现状态和类型映射

**Step 5: 注册设备驱动**
- 在DriverFactory中注册
- 更新自动注册逻辑

**Step 6: 编写单元测试**
- 测试设备连接/断开
- 测试数据读写
- 测试平台集成

**Step 7: 全链路集成测试**
- 测试适配器转换
- 测试设备生命周期
- 测试平台集成

**Step 8: 文档和验证**
- 完善代码文档
- 验证所有规范
- 性能和稳定性测试

### 3. 设备生成器工具

#### 工具位置
`backend/tools/device_generator.py`

#### 基本使用
```bash
# 生成一个新设备
python tools/device_generator.py temperature_sensor
```

#### 完整参数
```bash
python tools/device_generator.py pressure_sensor \
    --manufacturer "霍尼韦尔" \
    --model "Honeywell PPT" \
    --protocol "modbus_rtu" \
    --communication "rs485" \
    --description "高精度压力传感器"
```

#### 自动生成内容
- 设备驱动代码: `projects/encoder_test/drivers/device/{device_name}/{device_name}.py`
- 设备适配器: `projects/encoder_test/adapters/{device_name}_adapter.py`
- 单元测试: `tests/device/test_{device_name}.py`
- 集成测试: `tests/device/test_{device_name}_full_link.py`
- 自动注册到驱动工厂

### 4. 设备类模板

```python
from shared.drivers.base.base_device import BaseDevice
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class NewDevice(BaseDevice):
    """新设备驱动
    
    【架构集成】
    - 继承 BaseDevice 基类
    - 支持平台设备生命周期管理
    - 集成平台事件系统
    """
    
    def __init__(self, driver_id: str = 'new_device', protocol=None, 
                 platform_device=None, **kwargs):
        super().__init__(driver_id, protocol, **kwargs)
        self.protocol = protocol
        self.platform_device = platform_device
        
        # 设备特定状态
        self._device_state = {}
        
        # 设备信息
        self._device_info = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'protocol': 'Unknown',
            'communication': 'Unknown'
        }
    
    def connect(self) -> bool:
        """连接设备"""
        try:
            self._device_status = "connecting"
            
            if not self.protocol.is_connected:
                if not self.protocol.connect():
                    self._device_status = "fault"
                    if self.platform_device:
                        self.platform_device.disconnect()
                    return False
            
            self._initialize_device()
            self._is_connected = True
            self._device_status = "connected"
            
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
        
        try:
            data = {}
            
            if self.platform_device:
                self.platform_device.record_operation(success=True)
            
            return data
        except Exception as e:
            logger.error(f"读取数据失败: {e}")
            if self.platform_device:
                self.platform_device.record_operation(success=False)
            raise
    
    def write_data(self, data: Dict[str, Any]) -> bool:
        """写入设备数据"""
        if not self.is_connected:
            raise ConnectionError("设备未连接")
        
        try:
            # 实现具体的数据写入逻辑
            
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
            logger.info(f"设备重置: {self.driver_id}")
        except Exception as e:
            logger.error(f"设备重置失败: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """设备健康检查"""
        base = super().health_check()
        
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
        pass
    
    def _get_device_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        return {}
```

### 5. 设备适配器模板

```python
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
```

### 6. 使用示例

#### 创建和使用设备
```python
from projects.encoder_test.drivers.device.pressure_sensor.pressure_sensor import PressureSensor
from projects.encoder_test.adapters.pressure_sensor_adapter import PressureSensorAdapter
from shared.drivers.factory import CommFactory, ProtocolFactory
from platform.domain.common.enums import ProtocolType

# 创建平台设备
platform_device = PressureSensorAdapter.to_platform_device(
    station_id=1,
    device_code="PS-001",
    device_name="压力传感器",
    protocol=ProtocolType.MODBUS_RTU
)

# 创建通信层
comm = CommFactory.create('rs485', port='COM3', baudrate=9600)
protocol = ProtocolFactory.create('modbus_rtu', comm=comm, slave_id=2)

# 创建设备驱动
sensor = PressureSensor(
    driver_id='pressure_sensor',
    protocol=protocol,
    platform_device=platform_device
)

# 使用设备
if sensor.connect():
    data = sensor.read_data()
    print(f"当前压力: {data.get('pressure', 0)} MPa")
    sensor.disconnect()
```

### 7. 设备验证清单

#### 代码规范验证
- [ ] 继承BaseDevice基类
- [ ] 实现所有必需方法
- [ ] 集成平台设备生命周期
- [ ] 使用正确的命名规范
- [ ] 完整的文档注释
- [ ] 正确的错误处理

#### 功能验证
- [ ] 设备连接/断开功能正常
- [ ] 数据读写功能正常
- [ ] 设备重置功能正常
- [ ] 健康检查功能正常
- [ ] 参数验证功能正常
- [ ] 错误处理功能正常

#### 平台集成验证
- [ ] 适配器转换功能正常
- [ ] 平台设备状态同步正常
- [ ] 平台事件发布正常
- [ ] 平台操作记录正常
- [ ] 平台设备指标正常

#### 测试验证
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 全链路测试通过
- [ ] 测试覆盖率达标
- [ ] 性能测试通过

### 8. 常见问题解决

#### 问题1: 导入错误
```bash
ModuleNotFoundError: No module named 'projects.encoder_test.drivers.device.new_device'
```
**解决方案**: 确保设备已正确注册到驱动工厂

#### 问题2: 连接失败
```bash
设备连接失败: [Errno 2] could not open port 'COM3'
```
**解决方案**: 检查串口是否被占用，确认串口号正确

#### 问题3: 读取数据失败
```bash
读取数据失败: Modbus IO Error
```
**解决方案**: 检查通信参数是否正确，确认设备地址配置

## 📖 相关文档

- 完整规范文档: `docs/device-addition-specification.md`
- 使用示例文档: `docs/device-generator-usage.md`
- 设备生成器工具: `backend/tools/device_generator.py`

## 🎯 最佳实践

1. **使用生成器工具**: 优先使用设备生成器创建基础代码
2. **遵循规范**: 严格按照命名规范和架构要求开发
3. **完整测试**: 确保单元测试和集成测试全部通过
4. **文档完善**: 为设备特定方法提供完整的文档注释
5. **错误处理**: 实现完善的错误处理和日志记录
6. **平台集成**: 充分利用平台的生命周期管理和事件系统

## 🔧 扩展建议

1. **自定义模板**: 根据项目需求定制代码模板
2. **设备配置**: 创建设备配置文件统一管理参数
3. **设备管理器**: 实现设备管理器统一管理多个设备
4. **性能优化**: 根据实际需求优化设备通信性能

## 📞 获取帮助

如果在使用过程中遇到问题，请：
1. 检查相关文档是否完整
2. 查看验证清单确保所有要求已满足
3. 参考现有设备实现作为示例
4. 运行测试确认功能正常