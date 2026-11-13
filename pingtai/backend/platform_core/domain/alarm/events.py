"""
告警领域事件 - Alarm Domain Events

【职责】
- 定义告警领域事件
- 支持事件溯源
- 提供状态变更通知

【设计原则】
- 事件不可变
- 事件包含完整上下文
- 支持事件回放
"""
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time

from ..common.aggregate_root import generate_id


class AlarmEventType(Enum):
    """告警事件类型"""
    ALARM_TRIGGERED = "alarm.triggered"           # 告警触发
    ALARM_ACKNOWLEDGED = "alarm.acknowledged"     # 告警确认
    ALARM_RESOLVED = "alarm.resolved"             # 告警解决
    ALARM_CLOSED = "alarm.closed"                 # 告警关闭
    ALARM_REOPENED = "alarm.reopened"             # 告警重新打开


@dataclass
class AlarmEvent:
    """告警事件基类"""
    event_type: AlarmEventType
    alarm_id: str
    timestamp: float
    data: Dict[str, Any]
    event_id: str = None
    correlation_id: str = None  # 关联ID，用于追踪整个事件链
    causation_id: str = None    # 因果ID，用于追踪事件源头
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = generate_id("EVNT")
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class AlarmTriggeredEvent(AlarmEvent):
    """告警触发事件"""
    
    def __init__(self, alarm_id: str, alarm_code: str, alarm_level: str, 
                 message: str, occurred_at: float, task_id: str = None, 
                 station_id: str = None, device_id: str = None, 
                 workorder_id: str = None, metadata: Dict[str, Any] = None):
        data = {
            'alarm_code': alarm_code,
            'alarm_level': alarm_level,
            'message': message,
            'occurred_at': occurred_at,
            'task_id': task_id,
            'station_id': station_id,
            'device_id': device_id,
            'workorder_id': workorder_id,
            'metadata': metadata or {}
        }
        super().__init__(
            event_type=AlarmEventType.ALARM_TRIGGERED,
            alarm_id=alarm_id,
            timestamp=occurred_at,
            data=data
        )


@dataclass
class AlarmAcknowledgedEvent(AlarmEvent):
    """告警确认事件"""
    
    def __init__(self, alarm_id: str, operator_id: str, acknowledged_at: float, 
                 extra_data: Dict[str, Any] = None):
        data = {
            'operator_id': operator_id,
            'acknowledged_at': acknowledged_at,
            'extra_data': extra_data or {}
        }
        super().__init__(
            event_type=AlarmEventType.ALARM_ACKNOWLEDGED,
            alarm_id=alarm_id,
            timestamp=acknowledged_at,
            data=data
        )


@dataclass
class AlarmResolvedEvent(AlarmEvent):
    """告警解决事件"""
    
    def __init__(self, alarm_id: str, operator_id: str, resolved_at: float, 
                 resolution_notes: str = None, extra_data: Dict[str, Any] = None):
        data = {
            'operator_id': operator_id,
            'resolved_at': resolved_at,
            'resolution_notes': resolution_notes,
            'extra_data': extra_data or {}
        }
        super().__init__(
            event_type=AlarmEventType.ALARM_RESOLVED,
            alarm_id=alarm_id,
            timestamp=resolved_at,
            data=data
        )


@dataclass
class AlarmClosedEvent(AlarmEvent):
    """告警关闭事件"""
    
    def __init__(self, alarm_id: str, operator_id: str, closed_at: float, 
                 close_reason: str = None, extra_data: Dict[str, Any] = None):
        data = {
            'operator_id': operator_id,
            'closed_at': closed_at,
            'close_reason': close_reason,
            'extra_data': extra_data or {}
        }
        super().__init__(
            event_type=AlarmEventType.ALARM_CLOSED,
            alarm_id=alarm_id,
            timestamp=closed_at,
            data=data
        )


@dataclass
class AlarmReopenedEvent(AlarmEvent):
    """告警重新打开事件"""
    
    def __init__(self, alarm_id: str, operator_id: str, reopened_at: float, 
                 reopen_reason: str = None, extra_data: Dict[str, Any] = None):
        data = {
            'operator_id': operator_id,
            'reopened_at': reopened_at,
            'reopen_reason': reopen_reason,
            'extra_data': extra_data or {}
        }
        super().__init__(
            event_type=AlarmEventType.ALARM_REOPENED,
            alarm_id=alarm_id,
            timestamp=reopened_at,
            data=data
        )