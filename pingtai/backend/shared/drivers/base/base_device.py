"""
设备基类 - 设备对象抽象

【职责】
- 代表真实工业设备
- 不直接管理通讯
- 使用 Protocol 进行数据交互

【标准接口】
┌─────────────────────────────────────────────────────────────┐
│  BaseDevice (设备抽象)                                     │
├─────────────────────────────────────────────────────────────┤
│  初始化:                                                   │
│    - __init__(protocol: BaseProtocol)  注入协议层          │
│                                                             │
│  生命周期:                                                 │
│    - connect() -> bool            连接设备                 │
│    - disconnect()                 断开                     │
│    - is_connected() -> bool     检查状态                  │
│                                                             │
│  数据操作:                                                 │
│    - read_data() -> Dict          读取设备数据             │
│    - write_data(data) -> bool    写入设备数据             │
│                                                             │
│  设备控制:                                                 │
│    - reset()                      重置设备                 │
│                                                             │
│  健康检查:                                                 │
│    - health_check() -> Dict       健康状态                 │
└─────────────────────────────────────────────────────────────┘
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseDevice(ABC):
    """设备基类 - 使用组合持有 BaseProtocol"""
    
    def __init__(self, driver_id: str, protocol: ABC = None, **kwargs):
        self.driver_id = driver_id
        self.protocol = protocol
        self._is_connected = False
        self._error_count = 0
        self._device_status = "initialized"
    
    @property
    def is_connected(self) -> bool:
        return self._is_connected
    
    @property
    def device_status(self) -> str:
        return self._device_status
    
    def increment_error(self):
        self._error_count += 1
    
    def reset_error(self):
        self._error_count = 0
    
    @abstractmethod
    def connect(self) -> bool:
        """连接设备（通过协议层）"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开设备连接"""
        pass
    
    @abstractmethod
    def read_data(self) -> Dict[str, Any]:
        """读取设备核心数据"""
        pass
    
    @abstractmethod
    def write_data(self, data: Dict[str, Any]) -> bool:
        """写入设备数据"""
        pass
    
    @abstractmethod
    def reset(self):
        """重置设备"""
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """设备层健康检查"""
        return {
            'driver_id': self.driver_id,
            'layer': 'device',
            'is_connected': self._is_connected,
            'device_status': self._device_status,
            'error_count': self._error_count,
            'protocol_driver_id': self.protocol.driver_id if self.protocol else None,
        }