"""
告警领域 - Alarm Domain

【导出内容】
- Alarm: 告警聚合根
- AlarmLevel, AlarmStatus: 枚举
- AlarmException及其子类: 异常
- AlarmEvent及其子类: 事件
"""
from .alarm import Alarm, AlarmStateMachine, AlarmMetrics
from .enums import AlarmLevel, AlarmStatus
from .exceptions import (
    AlarmException, AlarmNotFoundException, AlarmStatusTransitionException,
    AlarmAlreadyActiveException, AlarmAlreadyAcknowledgedException,
    AlarmAlreadyResolvedException, AlarmDeDuplicationException
)
from .events import (
    AlarmEventType, AlarmEvent, AlarmTriggeredEvent, AlarmAcknowledgedEvent,
    AlarmResolvedEvent, AlarmClosedEvent, AlarmReopenedEvent
)

__all__ = [
    # 主要聚合根
    'Alarm',
    'AlarmStateMachine',
    'AlarmMetrics',
    
    # 枚举
    'AlarmLevel',
    'AlarmStatus',
    
    # 异常
    'AlarmException',
    'AlarmNotFoundException',
    'AlarmStatusTransitionException',
    'AlarmAlreadyActiveException',
    'AlarmAlreadyAcknowledgedException',
    'AlarmAlreadyResolvedException',
    'AlarmDeDuplicationException',
    
    # 事件
    'AlarmEventType',
    'AlarmEvent',
    'AlarmTriggeredEvent',
    'AlarmAcknowledgedEvent',
    'AlarmResolvedEvent',
    'AlarmClosedEvent',
    'AlarmReopenedEvent'
]