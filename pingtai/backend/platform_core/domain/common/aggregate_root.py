"""
通用领域基础 - Common Domain Foundation

【职责】
- 聚合根基类
- 实体基类
- 值对象基类

【设计原则】
- 聚合根：唯一标识、生命周期管理、业务不变性
- 实体：唯一标识、生命周期依附聚合根
- 值对象：不可变、无标识、通过属性相等
"""
from abc import ABC
from typing import Any, Optional
import uuid
import time


class AggregateRoot(ABC):
    """聚合根基类
    
    【职责】
    - 唯一标识
    - 生命周期管理
    - 业务不变性保证
    - 领域事件发布
    
    【使用示例】
    >>> class Task(AggregateRoot):
    ...     def __init__(self, task_id: str):
    ...         super().__init__(task_id)
    ...         self._version = 0
    ...
    >>> task = Task("TASK-001")
    >>> task.id
    'TASK-001'
    """
    
    def __init__(self, entity_id: str):
        """
        Args:
            entity_id: 聚合根唯一标识
        """
        self._id = entity_id
        self._version = 0
        self._created_at = time.time()
        self._updated_at = time.time()
        self._domain_events = []
    
    @property
    def id(self) -> str:
        """获取聚合根ID"""
        return self._id
    
    @property
    def version(self) -> int:
        """获取版本号（乐观锁）"""
        return self._version
    
    @property
    def created_at(self) -> float:
        """创建时间"""
        return self._created_at
    
    @property
    def updated_at(self) -> float:
        """更新时间"""
        return self._updated_at
    
    def _increment_version(self):
        """递增版本号"""
        self._version += 1
        self._updated_at = time.time()
    
    def _add_domain_event(self, event: Any):
        """添加领域事件
        
        Args:
            event: 领域事件
        """
        self._domain_events.append(event)
    
    def pull_domain_events(self) -> list:
        """拉取并清空领域事件
        
        Returns:
            领域事件列表
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def __eq__(self, other) -> bool:
        """通过ID比较相等"""
        if not isinstance(other, AggregateRoot):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """通过ID计算哈希"""
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id} version={self._version}>"


class Entity(ABC):
    """实体基类
    
    【职责】
    - 唯一标识
    - 生命周期依附聚合根
    - 可变状态
    
    【使用示例】
    >>> class TaskFlow(Entity):
    ...     def __init__(self, flow_id: str):
    ...         super().__init__(flow_id)
    ...
    >>> flow = TaskFlow("FLOW-001")
    >>> flow.id
    'FLOW-001'
    """
    
    def __init__(self, entity_id: str):
        """
        Args:
            entity_id: 实体唯一标识
        """
        self._id = entity_id
    
    @property
    def id(self) -> str:
        """获取实体ID"""
        return self._id
    
    def __eq__(self, other) -> bool:
        """通过ID比较相等"""
        if not isinstance(other, Entity):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """通过ID计算哈希"""
        return hash(self._id)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id}>"


class ValueObject(ABC):
    """值对象基类
    
    【职责】
    - 不可变
    - 无标识
    - 通过属性相等
    
    【使用示例】
    >>> class TaskMetrics(ValueObject):
    ...     def __init__(self, duration_ms: int, step_count: int):
    ...         self.duration_ms = duration_ms
    ...         self.step_count = step_count
    ...
    >>> m1 = TaskMetrics(1000, 10)
    >>> m2 = TaskMetrics(1000, 10)
    >>> m1 == m2
    True
    """
    
    def __eq__(self, other) -> bool:
        """通过属性比较相等"""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        """通过属性计算哈希"""
        return hash(tuple(sorted(self.__dict__.items())))
    
    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"<{self.__class__.__name__} {attrs}>"


def generate_id(prefix: str = "") -> str:
    """生成唯一ID
    
    Args:
        prefix: ID前缀
        
    Returns:
        唯一ID
    """
    unique_id = str(uuid.uuid4()).replace("-", "").upper()[:16]
    return f"{prefix}-{unique_id}" if prefix else f"ID-{unique_id}"