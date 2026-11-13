"""
设备生成器 - 一键生成设备代码

【功能】
- 自动生成设备目录结构
- 自动生成设备驱动代码
- 自动生成设备适配器代码
- 自动生成测试代码
- 自动注册设备驱动

【使用示例】
# 基本使用
python tools/device_generator.py new_device

# 完整参数
python tools/device_generator.py temperature_sensor \
    --manufacturer "西门子" \
    --model "SITRANS T" \
    --protocol "modbus_rtu" \
    --communication "rs485" \
    --description "温度传感器"
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
        print(f"设备目录: {self.device_dir}")
        print(f"适配器文件: {self.adapter_dir / f'{self.device_name}_adapter.py'}")
        print(f"测试目录: {project_root / 'tests/device'}")
    
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
        test_dir = project_root / "tests/device"
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
from platform_core.domain.device.device import Device, DeviceConfig
from platform_core.domain.common.enums import DeviceType, ProtocolType

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
    from platform_core.domain.common.enums import ProtocolType
    
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
    from platform_core.domain.device.device import Device
    from platform_core.domain.common.enums import DeviceType, ProtocolType
    
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