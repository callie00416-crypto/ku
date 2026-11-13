"""
CaseContext - 测试用例上下文

所属层级：TestCase 层
职责：管理用例执行时的上下文数据

包含：
- 设备实例
- 测试参数
- 中间数据
- 测试结果
"""
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading


@dataclass
class CaseContext:
    """测试用例上下文
    
    管理：
    - devices: 设备字典
    - parameters: 测试参数
    - runtime: 运行时数据
    - test_data: 测试数据记录
    """
    
    context_id: str = ""
    case_id: str = ""
    task_id: Optional[str] = None
    station_id: Optional[str] = None
    
    start_time: datetime = field(default_factory=datetime.now)
    
    devices: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    runtime: Dict[str, Any] = field(default_factory=dict)
    test_data: Dict[str, Any] = field(default_factory=dict)
    
    _local = None
    
    def __post_init__(self):
        self._local = threading.local()
    
    def set_device(self, name: str, device: Any):
        """注册设备"""
        self.devices[name] = device
    
    def get_device(self, name: str) -> Optional[Any]:
        """获取设备"""
        return self.devices.get(name)
    
    def set_parameter(self, key: str, value: Any):
        """设置测试参数"""
        self.parameters[key] = value
    
    def get_parameter(self, key: str, default=None) -> Any:
        """获取测试参数"""
        return self.parameters.get(key, default)
    
    def set_runtime(self, key: str, value: Any):
        """设置运行时数据"""
        self.runtime[key] = value
    
    def get_runtime(self, key: str, default=None) -> Any:
        """获取运行时数据"""
        return self.runtime.get(key, default)
    
    def record_data(self, key: str, value: Any):
        """记录测试数据"""
        self.test_data[key] = value
    
    def get_data(self, key: str, default=None) -> Any:
        """获取测试数据"""
        return self.test_data.get(key, default)
    
    def get_all_data(self) -> Dict[str, Any]:
        """获取所有测试数据"""
        return self.test_data.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'context_id': self.context_id,
            'case_id': self.case_id,
            'task_id': self.task_id,
            'station_id': self.station_id,
            'start_time': self.start_time.isoformat(),
            'devices': list(self.devices.keys()),
            'parameters': self.parameters,
            'test_data_keys': list(self.test_data.keys())
        }
    
    def clear(self):
        """清空运行时数据"""
        self.runtime.clear()
        self.test_data.clear()


class ContextManager:
    """上下文管理器（线程安全）"""
    
    _local = threading.local()
    _instances: Dict[str, 'ContextManager'] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls, task_id: str = None) -> 'ContextManager':
        """获取实例"""
        tid = task_id or 'default'
        with cls._lock:
            if tid not in cls._instances:
                cls._instances[tid] = cls()
            return cls._instances[tid]
    
    def set_context(self, context: CaseContext):
        """设置当前上下文"""
        self._local.context = context
    
    def get_context(self) -> Optional[CaseContext]:
        """获取当前上下文"""
        return getattr(self._local, 'context', None)
    
    def clear_context(self):
        """清除当前上下文"""
        self._local.context = None