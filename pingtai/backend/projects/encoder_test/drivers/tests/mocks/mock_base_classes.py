"""
Mock 基础类 - 用于测试的基础驱动类

这些类实现了 BaseComm、BaseProtocol、BaseDevice 的抽象方法，
用于在测试中替代真实的驱动实现。
"""
from abc import ABC
from projects.encoder_test.drivers.base import BaseComm, BaseProtocol, BaseDevice


class MockComm(BaseComm):
    """Mock 通讯类 - 实现 BaseComm 的所有抽象方法"""
    
    def __init__(self, driver_id: str = 'mock_comm', port: str = 'COM1', baudrate: int = 9600, **kwargs):
        super().__init__(driver_id, port, baudrate, **kwargs)
        self._sent_data = []
        self._received_data = []
    
    @property
    def error_count(self):
        return self._error_count
    
    def open(self) -> bool:
        self._is_open = True
        return True
    
    def close(self):
        self._is_open = False
    
    def send(self, data: bytes) -> int:
        self._sent_data.append(data)
        return len(data)
    
    def recv(self, size: int = 1024, timeout: float = 1.0) -> bytes:
        if self._received_data:
            return self._received_data.pop(0)
        return b''
    
    def connect(self):
        self._is_open = True
        return True
    
    def disconnect(self):
        self._is_open = False


class MockProtocol(BaseProtocol):
    """Mock 协议类 - 实现 BaseProtocol 的所有抽象方法"""
    
    def __init__(self, driver_id: str = 'mock_protocol', comm=None, **kwargs):
        super().__init__(driver_id, comm, **kwargs)
        self._registers = {}
        self._connected = False
    
    def set_comm(self, comm):
        """设置通讯驱动"""
        self.comm = comm
    
    def connect(self) -> bool:
        self._is_connected = True
        self._connected = True
        return True
    
    def disconnect(self):
        self._is_connected = False
        self._connected = False
    
    def read_register(self, addr: int, count: int = 1) -> list:
        values = []
        for i in range(count):
            values.append(self._registers.get(addr + i, 0))
        return values
    
    def write_register(self, addr: int, value) -> bool:
        self._registers[addr] = value
        return True


class MockDevice(BaseDevice):
    """Mock 设备类 - 实现 BaseDevice 的所有抽象方法"""
    
    def __init__(self, driver_id: str = 'mock_device', protocol=None, **kwargs):
        super().__init__(driver_id, protocol, **kwargs)
        self._data = {}
        self._connected = False
    
    def set_protocol(self, protocol):
        """设置协议驱动"""
        self.protocol = protocol
    
    def connect(self) -> bool:
        self._is_connected = True
        self._connected = True
        return True
    
    def disconnect(self):
        self._is_connected = False
        self._connected = False
    
    def read_data(self) -> dict:
        return self._data.copy()
    
    def write_data(self, data: dict) -> bool:
        self._data.update(data)
        return True
    
    def reset(self):
        self._data.clear()