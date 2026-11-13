"""
Device 工厂 - 创建设备层实例

所属层级：Device 层
职责：根据配置创建设备实例（电源/电机/编码器/激光）

禁止：
- 直接 new PowerSupply() 等具体类
- 在工厂类中处理协议或通讯细节
"""
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from projects.encoder_test.drivers.base.base_protocol import BaseProtocol


class DeviceFactory:
    """Device 工厂类"""
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, device_class: type):
        """注册 Device 类型"""
        cls._registry[name] = device_class
    
    @classmethod
    def create(cls, device_type: str, protocol: 'BaseProtocol' = None, **kwargs) -> Any:
        """创建设备实例
        
        Args:
            device_type: 'power_supply' | 'motor' | 'encoder' | 'laser'
            protocol: 协议层实例
            
        Returns:
            BaseDevice 子类实例
            
        使用示例：
        >>> from drivers.factory import CommFactory, ProtocolFactory, DeviceFactory
        >>> comm = CommFactory.create('rs485', port='COM4')
        >>> protocol = ProtocolFactory.create('modbus_rtu', comm=comm)
        >>> ps = DeviceFactory.create('power_supply', protocol=protocol)
        >>> ps.connect()
        """
        if device_type not in cls._registry:
            raise ValueError(f"Unknown device type: {device_type}")
            
        device_class = cls._registry[device_type]
        return device_class(protocol=protocol, **kwargs)
    
    @classmethod
    def create_power_supply(cls, protocol: 'BaseProtocol' = None, **kwargs):
        """快捷创建电源"""
        return cls.create('power_supply', protocol=protocol, **kwargs)
    
    @classmethod
    def create_motor(cls, protocol: 'BaseProtocol' = None, **kwargs):
        """快捷创建电机"""
        return cls.create('motor', protocol=protocol, **kwargs)
    
    @classmethod
    def create_encoder(cls, protocol: 'BaseProtocol' = None, **kwargs):
        """快捷创建编码器"""
        return cls.create('encoder', protocol=protocol, **kwargs)
    
    @classmethod
    def create_mock(cls, device_type: str = 'power_supply', **kwargs):
        """快捷创建 Mock 设备"""
        from drivers.mock.mock_modbus import MockModbusDriver
        
        mock_protocol = MockModbusDriver()
        return cls.create(device_type, protocol=mock_protocol, **kwargs)
    
    @classmethod
    def get_all_registered_types(cls) -> list:
        """获取所有注册的设备类型"""
        return list(cls._registry.keys())


from projects.encoder_test.drivers.device.power_supply.power_supply import PowerSupply
from projects.encoder_test.drivers.device.encoder.analyzer_encoder import AnalyzerEncoderDriver
from projects.encoder_test.drivers.device.power_amplifier.power_amplifier import ATA101BPowerAmplifier
from projects.encoder_test.drivers.device.waveform_generator.dg811 import DG811WaveformGenerator

DeviceFactory.register('power_supply', PowerSupply)
DeviceFactory.register('encoder', AnalyzerEncoderDriver)
DeviceFactory.register('power_amplifier', ATA101BPowerAmplifier)
DeviceFactory.register('waveform_generator', DG811WaveformGenerator)