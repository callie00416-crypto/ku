"""
协议基类 - 协议解析抽象

【职责】
- 协议编解码
- 不直接管理连接
- 使用 BaseComm 进行数据收发

【标准接口】
┌─────────────────────────────────────────────────────────────┐
│  BaseProtocol (协议抽象)                                   │
├─────────────────────────────────────────────────────────────┤
│  初始化:                                                   │
│    - __init__(comm: BaseComm)    注入通讯层               │
│                                                             │
│  生命周期:                                                 │
│    - connect() -> bool           连接设备                  │
│    - disconnect()                断开                      │
│    - is_connected() -> bool     检查状态                  │
│                                                             │
│  协议操作:                                                 │
│    - read_register(addr)         读寄存器                  │
│    - write_register(addr, value)  写寄存器                  │
│                                                             │
│  健康检查:                                                 │
│    - health_check() -> Dict       健康状态                 │
└─────────────────────────────────────────────────────────────┘
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseProtocol(ABC):
    """协议基类 - 使用组合持有 BaseComm"""
    
    def __init__(self, driver_id: str, comm: ABC = None, **kwargs):
        self.driver_id = driver_id
        self.comm = comm
        self._is_connected = False
        self._error_count = 0
    
    @property
    def is_connected(self) -> bool:
        return self._is_connected
    
    def increment_error(self):
        self._error_count += 1
    
    def reset_error(self):
        self._error_count = 0
    
    @abstractmethod
    def connect(self) -> bool:
        """连接设备（通过底层通讯）"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开连接"""
        pass
    
    @abstractmethod
    def read_register(self, address: int, slave_id: int = None) -> Optional[int]:
        """读寄存器"""
        pass
    
    @abstractmethod
    def write_register(self, address: int, value: int, slave_id: int = None) -> bool:
        """写寄存器"""
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """协议层健康检查"""
        return {
            'driver_id': self.driver_id,
            'layer': 'protocol',
            'is_connected': self._is_connected,
            'error_count': self._error_count,
            'comm_driver_id': self.comm.driver_id if self.comm else None,
        }