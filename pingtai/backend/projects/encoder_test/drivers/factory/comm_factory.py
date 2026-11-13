"""
Comm 工厂 - 创建通讯层实例

所属层级：Comm 层
职责：根据配置创建 Comm 实例（RS485/TCP/CAN/USB）

禁止：
- 直接 new RS485Comm() 等具体类
- 在工厂类中处理协议或设备逻辑
"""
from typing import Optional, Dict, Any


class CommFactory:
    """Comm 工厂类"""
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, comm_class: type):
        """注册 Comm 类型"""
        cls._registry[name] = comm_class
    
    @classmethod
    def create(cls, comm_type: str, **kwargs) -> Any:
        """创建 Comm 实例
        
        Args:
            comm_type: 'rs485' | 'tcp' | 'can' | 'usb' | 'mock'
            
        Returns:
            BaseComm 子类实例
            
        使用示例：
        >>> comm = CommFactory.create('rs485', port='COM4', baudrate=9600)
        >>> comm.open()
        """
        if comm_type not in cls._registry:
            from projects.encoder_test.drivers.mock.mock_serial import MockSerial
            cls._registry[comm_type] = MockSerial
            
        comm_class = cls._registry[comm_type]
        return comm_class(**kwargs)
    
    @classmethod
    def create_rs485(cls, port: str = 'COM4', baudrate: int = 9600, **kwargs):
        """快捷创建 RS485"""
        return cls.create('rs485', port=port, baudrate=baudrate, **kwargs)
    
    @classmethod
    def create_tcp(cls, host: str = '127.0.0.1', port: int = 8080, **kwargs):
        """快捷创建 TCP"""
        return cls.create('tcp', host=host, port=port, **kwargs)
    
    @classmethod
    def create_mock(cls, **kwargs):
        """快捷创建 Mock"""
        return cls.create('mock', **kwargs)


from shared.drivers.comm.rs485_comm import RS485Comm
from shared.drivers.comm.tcp_comm import TCPComm
from shared.drivers.comm.can_comm import CANComm
CommFactory.register('rs485', RS485Comm)
CommFactory.register('tcp', TCPComm)
CommFactory.register('can', CANComm)