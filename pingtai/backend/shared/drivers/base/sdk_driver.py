"""
SDK 基类 - SDK 封装层抽象

【职责】
- 封装第三方 SDK
- 提供统一的 SDK 接口
- 不是设备或通讯抽象
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SDKDriver(ABC):
    """SDK 基类 - 封装第三方 SDK 接口"""
    
    def __init__(self, driver_id: str, **kwargs):
        self.driver_id = driver_id
        self._is_initialized = False
        self._error_count = 0
        self.config = kwargs
    
    @property
    def is_initialized(self) -> bool:
        return self._is_initialized
    
    def increment_error(self):
        self._error_count += 1
    
    def reset_error(self):
        self._error_count = 0
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化 SDK"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理 SDK 资源"""
        pass
    
    @abstractmethod
    def execute_command(self, cmd: str, params: Dict[str, Any]) -> Optional[Any]:
        """执行 SDK 命令"""
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """SDK 健康检查"""
        return {
            'driver_id': self.driver_id,
            'layer': 'sdk',
            'is_initialized': self._is_initialized,
            'error_count': self._error_count,
            'config_keys': list(self.config.keys()) if self.config else [],
        }