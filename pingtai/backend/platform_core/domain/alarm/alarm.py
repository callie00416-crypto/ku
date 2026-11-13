"""
告警领域 - Alarm Domain（工业异常治理体系）

【职责】
- 工业异常状态管理
- 告警生命周期管理
- 告警去重机制
- 告警关联追踪

【核心能力】
- 告警状态机
- 告警去重
- 告警关联(task_id/station_id/device_id/workorder_id)
- 告警确认/恢复/关闭

【设计原则】
- Alarm 是聚合根
- 告警状态转换必须通过领域方法
- 支持告警去重机制
- 支持生命周期管理
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import time

from ..common.aggregate_root import AggregateRoot, ValueObject, Entity, generate_id
from ..common.enums import EventType
from ..common.exceptions import DomainException
from ..common.state_machine import StateMachine
from .enums import AlarmLevel, AlarmStatus


@dataclass(frozen=True)
class AlarmMetrics(ValueObject):
    """告警指标（值对象）
    
    【职责】
    - 记录告警相关指标
    - 不可变
    """
    trigger_count: int = 0
    ack_count: int = 0
    resolve_count: int = 0
    close_count: int = 0
    
    def __hash__(self):
        return hash((
            self.trigger_count,
            self.ack_count,
            self.resolve_count,
            self.close_count
        ))


class AlarmStateMachine(StateMachine):
    """告警状态机
    
    【状态流转】
    active -> acked -> resolved -> closed
    
    【特殊状态】
    - active: 激活状态
    - acked: 已确认
    - resolved: 已解决
    - closed: 已关闭
    
    【生命周期】
    1. active: 告警触发
    2. acked: 运维确认
    3. resolved: 问题解决
    4. closed: 归档关闭
    """
    
    def __init__(self, alarm_id: str):
        """
        Args:
            alarm_id: 告警ID
        """
        transitions = {
            'active': ['acked', 'resolved', 'closed'],
            'acked': ['resolved', 'closed'],
            'resolved': ['closed'],
            'closed': []  # closed is final state
        }
        super().__init__(
            initial_state='active',
            transitions=transitions,
            state_machine_id=f"alarm_{alarm_id}"
        )
        self._alarm_id = alarm_id
    
    def ack(self) -> bool:
        """确认告警
        
        Returns:
            是否成功
        """
        return self.transition('acked', reason='告警已确认')
    
    def resolve(self) -> bool:
        """解决告警
        
        Returns:
            是否成功
        """
        return self.transition('resolved', reason='告警已解决')
    
    def close(self) -> bool:
        """关闭告警
        
        Returns:
            是否成功
        """
        return self.transition('closed', reason='告警已关闭')


@dataclass
class Alarm(AggregateRoot):
    """告警聚合根（工业异常核心）
    
    【职责】
    - 管理告警完整生命周期
    - 保证告警状态转换合法性
    - 支持告警去重机制
    - 支持告警关联追踪
    
    【状态流转】
    active -> acked -> resolved -> closed
    
    【核心方法】
    - trigger(): 触发告警
    - acknowledge(): 确认告警
    - resolve(): 解决告警
    - close(): 关闭告警
    
    【关联关系】
    - task_id: 关联任务
    - station_id: 关联工位
    - device_id: 关联设备
    - workorder_id: 关联工单
    
    【使用示例】
    >>> alarm = Alarm.create(
    ...     alarm_code="CONN_ERR_001",
    ...     alarm_level=AlarmLevel.ERROR,
    ...     message="设备连接失败",
    ...     task_id="TASK-001",
    ...     station_id="STATION-001",
    ...     device_id="DEV-001"
    ... )
    >>> alarm.trigger()
    >>> alarm.acknowledge()
    >>> alarm.resolve()
    >>> alarm.close()
    """
    
    def __init__(self, alarm_id: str):
        """
        Args:
            alarm_id: 告警ID
        """
        super().__init__(alarm_id)
        
        self._alarm_code: Optional[str] = None
        self._alarm_level: Optional[AlarmLevel] = None
        self._message: Optional[str] = None
        self._source_type: Optional[str] = None
        self._source_id: Optional[str] = None
        
        self._task_id: Optional[str] = None
        self._station_id: Optional[str] = None
        self._device_id: Optional[str] = None
        self._workorder_id: Optional[str] = None
        
        self._status = AlarmStatus.ACTIVE
        self._occurred_at: Optional[float] = None
        self._acknowledged_at: Optional[float] = None
        self._resolved_at: Optional[float] = None
        self._closed_at: Optional[float] = None
        
        self._operator_id: Optional[str] = None
        self._ack_operator: Optional[str] = None
        self._resolve_operator: Optional[str] = None
        self._close_operator: Optional[str] = None
        
        self._metadata: Dict[str, Any] = {}
        self._metrics = AlarmMetrics()
        
        self._state_machine = AlarmStateMachine(alarm_id)
    
    @property
    def alarm_code(self) -> Optional[str]:
        return self._alarm_code
    
    @property
    def alarm_level(self) -> Optional[AlarmLevel]:
        return self._alarm_level
    
    @property
    def message(self) -> Optional[str]:
        return self._message
    
    @property
    def source_type(self) -> Optional[str]:
        return self._source_type
    
    @property
    def source_id(self) -> Optional[str]:
        return self._source_id
    
    @property
    def task_id(self) -> Optional[str]:
        return self._task_id
    
    @property
    def station_id(self) -> Optional[str]:
        return self._station_id
    
    @property
    def device_id(self) -> Optional[str]:
        return self._device_id
    
    @property
    def workorder_id(self) -> Optional[str]:
        return self._workorder_id
    
    @property
    def status(self) -> AlarmStatus:
        return self._status
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata
    
    @property
    def occurred_at(self) -> Optional[float]:
        return self._occurred_at
    
    @property
    def acknowledged_at(self) -> Optional[float]:
        return self._acknowledged_at
    
    @property
    def resolved_at(self) -> Optional[float]:
        return self._resolved_at
    
    @property
    def closed_at(self) -> Optional[float]:
        return self._closed_at
    
    @property
    def operator_id(self) -> Optional[str]:
        return self._operator_id

    @property
    def ack_operator(self) -> Optional[str]:
        return self._ack_operator

    @property
    def resolve_operator(self) -> Optional[str]:
        return self._resolve_operator

    @property
    def close_operator(self) -> Optional[str]:
        return self._close_operator

    @property
    def metrics(self) -> AlarmMetrics:
        return self._metrics
    
    @classmethod
    def create(cls, alarm_code: str, alarm_level: AlarmLevel, message: str,
               task_id: str = None, station_id: str = None, 
               device_id: str = None, workorder_id: str = None,
               source_type: str = None, source_id: str = None,
               metadata: Dict[str, Any] = None) -> 'Alarm':
        """创建告警（工厂方法）
        
        Args:
            alarm_code: 告警代码
            alarm_level: 告警等级
            message: 告警消息
            task_id: 关联任务ID
            station_id: 关联工位ID
            device_id: 关联设备ID
            workorder_id: 关联工单ID
            source_type: 源类型
            source_id: 源ID
            metadata: 元数据
            
        Returns:
            Alarm实例
        """
        alarm_id = generate_id("ALARM")
        alarm = cls(alarm_id)
        
        alarm._alarm_code = alarm_code
        alarm._alarm_level = alarm_level
        alarm._message = message
        alarm._source_type = source_type
        alarm._source_id = source_id
        alarm._task_id = task_id
        alarm._station_id = station_id
        alarm._device_id = device_id
        alarm._workorder_id = workorder_id
        alarm._metadata = metadata or {}
        
        return alarm
    
    def trigger(self, operator_id: str = None) -> None:
        """触发告警
        
        Args:
            operator_id: 操作员ID
        """
        self._state_machine.transition('active', reason='告警触发')
        self._status = AlarmStatus.ACTIVE
        self._occurred_at = time.time()
        self._operator_id = operator_id
        
        # 更新指标
        self._metrics = AlarmMetrics(
            trigger_count=self._metrics.trigger_count + 1,
            ack_count=self._metrics.ack_count,
            resolve_count=self._metrics.resolve_count,
            close_count=self._metrics.close_count
        )
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.ALARM_TRIGGERED,
            'aggregate_id': self._id,
            'aggregate_type': 'Alarm',
            'data': {
                'alarm_code': self._alarm_code,
                'alarm_level': self._alarm_level.value,
                'message': self._message,
                'occurred_at': self._occurred_at
            }
        })
    
    def acknowledge(self, operator_id: str) -> None:
        """确认告警
        
        Args:
            operator_id: 确认操作员ID
        """
        self._state_machine.ack()
        self._status = AlarmStatus.ACKED
        self._acknowledged_at = time.time()
        self._ack_operator = operator_id
        
        # 更新指标
        self._metrics = AlarmMetrics(
            trigger_count=self._metrics.trigger_count,
            ack_count=self._metrics.ack_count + 1,
            resolve_count=self._metrics.resolve_count,
            close_count=self._metrics.close_count
        )
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.ALARM_ACKNOWLEDGED,
            'aggregate_id': self._id,
            'aggregate_type': 'Alarm',
            'data': {
                'ack_operator': operator_id,
                'acknowledged_at': self._acknowledged_at
            }
        })
    
    def resolve(self, operator_id: str) -> None:
        """解决告警
        
        Args:
            operator_id: 解决操作员ID
        """
        self._state_machine.resolve()
        self._status = AlarmStatus.RESOLVED
        self._resolved_at = time.time()
        self._resolve_operator = operator_id
        
        # 更新指标
        self._metrics = AlarmMetrics(
            trigger_count=self._metrics.trigger_count,
            ack_count=self._metrics.ack_count,
            resolve_count=self._metrics.resolve_count + 1,
            close_count=self._metrics.close_count
        )
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.ALARM_RESOLVED,
            'aggregate_id': self._id,
            'aggregate_type': 'Alarm',
            'data': {
                'resolve_operator': operator_id,
                'resolved_at': self._resolved_at
            }
        })
    
    def close(self, operator_id: str) -> None:
        """关闭告警
        
        Args:
            operator_id: 关闭操作员ID
        """
        self._state_machine.close()
        self._status = AlarmStatus.CLOSED
        self._closed_at = time.time()
        self._close_operator = operator_id
        
        # 更新指标
        self._metrics = AlarmMetrics(
            trigger_count=self._metrics.trigger_count,
            ack_count=self._metrics.ack_count,
            resolve_count=self._metrics.resolve_count,
            close_count=self._metrics.close_count + 1
        )
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.ALARM_CLOSED,
            'aggregate_id': self._id,
            'aggregate_type': 'Alarm',
            'data': {
                'close_operator': operator_id,
                'closed_at': self._closed_at
            }
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            告警信息字典
        """
        return {
            'id': self._id,
            'alarm_code': self._alarm_code,
            'alarm_level': self._alarm_level.value if self._alarm_level else None,
            'message': self._message,
            'source_type': self._source_type,
            'source_id': self._source_id,
            'task_id': self._task_id,
            'station_id': self._station_id,
            'device_id': self._device_id,
            'workorder_id': self._workorder_id,
            'status': self._status.value,
            'occurred_at': self._occurred_at,
            'acknowledged_at': self._acknowledged_at,
            'resolved_at': self._resolved_at,
            'closed_at': self._closed_at,
            'operator_id': self._operator_id,
            'ack_operator': self._ack_operator,
            'resolve_operator': self._resolve_operator,
            'close_operator': self._close_operator,
            'metadata': self._metadata,
            'metrics': {
                'trigger_count': self._metrics.trigger_count,
                'ack_count': self._metrics.ack_count,
                'resolve_count': self._metrics.resolve_count,
                'close_count': self._metrics.close_count
            },
            'version': self.version,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self) -> str:
        return f"<Alarm id={self._id} code={self._alarm_code} level={self._alarm_level.value if self._alarm_level else None} status={self._status.value}>"