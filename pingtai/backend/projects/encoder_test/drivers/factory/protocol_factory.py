"""
Protocol 工厂 - 创建协议层实例

所属层级：Protocol 层
职责：根据配置创建 Protocol 实例（Modbus/CANopen/SCPI）

禁止：
- 直接 new ModbusDriver() 等具体类
- 在工厂类中处理设备业务逻辑
"""
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from projects.encoder_test.drivers.base.base_comm import BaseComm


class ProtocolFactory:
    """Protocol 工厂类"""
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, protocol_class: type):
        """注册 Protocol 类型"""
        cls._registry[name] = protocol_class
    
    @classmethod
    def create(cls, protocol_type: str, comm: 'BaseComm' = None, **kwargs) -> Any:
        """创建 Protocol 实例
        
        Args:
            protocol_type: 'modbus_rtu' | 'modbus_tcp' | 'canopen' | 'scpi'
            comm: 通讯层实例
            
        Returns:
            BaseProtocol 子类实例
            
        使用示例：
        >>> from drivers.factory import CommFactory, ProtocolFactory
        >>> comm = CommFactory.create('rs485', port='COM4')
        >>> protocol = ProtocolFactory.create('modbus_rtu', comm=comm, slave_id=1)
        """
        if protocol_type not in cls._registry:
            raise ValueError(f"Unknown protocol type: {protocol_type}")
            
        protocol_class = cls._registry[protocol_type]
        return protocol_class(comm=comm, **kwargs)
    
    @classmethod
    def create_modbus(cls, comm: 'BaseComm' = None, **kwargs):
        """快捷创建 Modbus RTU"""
        return cls.create('modbus_rtu', comm=comm, **kwargs)
    
    @classmethod
    def create_canopen(cls, comm: 'BaseComm' = None, **kwargs):
        """快捷创建 CANopen"""
        return cls.create('canopen', comm=comm, **kwargs)
    
    @classmethod
    def create_mock(cls, **kwargs):
        """快捷创建 Mock Protocol"""
        return cls.create('modbus_rtu', comm=None, **kwargs)


from shared.drivers.protocol.modbus_rtu import ModbusDriver
ProtocolFactory.register('modbus_rtu', ModbusDriver)
ProtocolFactory.register('modbus_tcp', ModbusDriver)
ProtocolFactory.register('canopen', ModbusDriver)