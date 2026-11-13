"""
ActionContext - 动作执行上下文

所属层级：Action 层
职责：管理动作执行时的设备、运行时数据、多工位/多任务

为什么重要：
- 多工位并发
- 资源隔离
- 运行时数据共享
- 任务追踪
"""
import threading
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class ActionContext:
    """动作执行上下文
    
    管理：
    - devices: 设备字典
    - runtime: 运行时数据
    - station_id: 工位ID
    - task_id: 任务ID
    - start_time: 开始时间
    - metadata: 元数据
    """
    
    context_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    station_id: Optional[str] = None
    task_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    
    devices: Dict[str, Any] = field(default_factory=dict)
    runtime: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    _local = None
    
    def __post_init__(self):
        self._local = threading.local()
    
    @property
    def task_start_time(self) -> datetime:
        return self.start_time
    
    def set_device(self, name: str, device: Any):
        """注册设备"""
        self.devices[name] = device
    
    def get_device(self, name: str) -> Optional[Any]:
        """获取设备"""
        return self.devices.get(name)
    
    def get_all_devices(self) -> Dict[str, Any]:
        """获取所有设备"""
        return self.devices.copy()
    
    def set_runtime(self, key: str, value: Any):
        """设置运行时数据"""
        self.runtime[key] = value
    
    def get_runtime(self, key: str, default=None) -> Any:
        """获取运行时数据"""
        return self.runtime.get(key, default)
    
    def set_metadata(self, key: str, value: Any):
        """设置元数据"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default=None) -> Any:
        """获取元数据"""
        return self.metadata.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'context_id': self.context_id,
            'station_id': self.station_id,
            'task_id': self.task_id,
            'start_time': self.start_time.isoformat(),
            'devices': list(self.devices.keys()),
            'runtime_keys': list(self.runtime.keys()),
            'metadata': self.metadata
        }


class ContextHolder:
    """上下文持有者（线程安全）
    
    保证每个线程有独立的上下文
    """
    
    _local = threading.local()
    _instances: Dict[str, 'ContextHolder'] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls, task_id: str = None) -> 'ContextHolder':
        """获取实例"""
        tid = task_id or 'default'
        with cls._lock:
            if tid not in cls._instances:
                cls._instances[tid] = cls()
            return cls._instances[tid]
    
    def set_context(self, context: ActionContext):
        """设置当前上下文"""
        self._local.context = context
    
    def get_context(self) -> Optional[ActionContext]:
        """获取当前上下文"""
        return getattr(self._local, 'context', None)
    
    def clear_context(self):
        """清除当前上下文"""
        self._local.context = None