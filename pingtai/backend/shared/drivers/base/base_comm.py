"""
通讯基类 - 通信通道抽象

【职责】
- 管理物理连接
- 数据收发
- 不是设备对象

【标准接口】
┌─────────────────────────────────────────────────────────────┐
│  BaseComm (通讯抽象)                                      │
├─────────────────────────────────────────────────────────────┤
│  生命周期:                                                 │
│    - open() -> bool           打开端口                    │
│    - close()                  关闭端口                    │
│    - is_open() -> bool        检查状态                    │
│                                                             │
│  数据收发:                                                 │
│    - send(data: bytes)       发送数据                    │
│    - recv(size, timeout)     接收数据                    │
│    - send_recv(data, timeout) 发送并接收                   │
│                                                             │
│  健康检查:                                                 │
│    - health_check() -> Dict   健康状态                    │
└─────────────────────────────────────────────────────────────┘
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseComm(ABC):
    """通讯基类 - 独立于设备存在"""
    
    def __init__(self, driver_id: str, port: str = '', baudrate: int = 9600, **kwargs):
        self.driver_id = driver_id
        self.port = port
        self.baudrate = baudrate
        self._is_open = False
        self._error_count = 0
    
    @property
    def is_open(self) -> bool:
        return self._is_open
    
    def increment_error(self):
        self._error_count += 1
    
    def reset_error(self):
        self._error_count = 0
    
    @abstractmethod
    def open(self) -> bool:
        """打开通讯端口"""
        pass
    
    @abstractmethod
    def close(self):
        """关闭通讯端口"""
        pass
    
    @abstractmethod
    def send(self, data: bytes) -> int:
        """发送数据"""
        pass
    
    @abstractmethod
    def recv(self, size: int = 1, timeout: float = 1.0) -> Optional[bytes]:
        """接收数据"""
        pass
    
    def send_recv(self, data: bytes, timeout: float = 1.0) -> Optional[bytes]:
        """发送并接收"""
        self.send(data)
        return self.recv(size=1024, timeout=timeout)
    
    def health_check(self) -> Dict[str, Any]:
        """通讯层健康检查"""
        return {
            'driver_id': self.driver_id,
            'layer': 'comm',
            'is_open': self._is_open,
            'error_count': self._error_count,
            'port': self.port,
            'baudrate': self.baudrate,
        }