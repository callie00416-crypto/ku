"""
通用领域组件 - Common Domain Components

【导出内容】
- 基础聚合根、实体、值对象
- 通用枚举
- 通用异常
- 状态机
- 时间处理
"""
from .aggregate_root import AggregateRoot, Entity, ValueObject, generate_id
from .enums import EventType, TaskStatus, TaskResult, TaskPriority, StationMode, StationStatus, DeviceStatus, DeviceConnectStatus, DeviceType, ProtocolType, WorkOrderStatus, ReportStatus, AlarmLevel
from .exceptions import (
    DomainException, ValidationException, ConcurrencyException,
    TaskException, TaskNotFoundException, TaskStatusTransitionException,
    TaskAlreadyRunningException, TaskRetryExhaustedException,
    StationException, StationNotFoundException, StationOfflineException, StationBusyException,
    DeviceException, DeviceNotFoundException, DeviceNotConnectedException, DeviceBusyException
)
from .state_machine import StateMachine, TaskStateMachine, StationStateMachine, StateTransition
from .temporal import Timestamp, get_current_timestamp, format_timestamp, parse_datetime_to_timestamp, TimeRange

__all__ = [
    # 基础组件
    'AggregateRoot',
    'Entity', 
    'ValueObject',
    'generate_id',
    
    # 枚举
    'EventType',
    'TaskStatus', 
    'TaskResult',
    'TaskPriority',
    'StationMode',
    'StationStatus',
    'DeviceStatus',
    'DeviceConnectStatus',
    'DeviceType',
    'ProtocolType',
    'WorkOrderStatus',
    'ReportStatus',
    'AlarmLevel',
    
    # 异常
    'DomainException',
    'ValidationException',
    'ConcurrencyException',
    'TaskException',
    'TaskNotFoundException',
    'TaskStatusTransitionException',
    'TaskAlreadyRunningException',
    'TaskRetryExhaustedException',
    'StationException',
    'StationNotFoundException',
    'StationOfflineException',
    'StationBusyException',
    'DeviceException',
    'DeviceNotFoundException',
    'DeviceNotConnectedException',
    'DeviceBusyException',
    
    # 状态机
    'StateMachine',
    'TaskStateMachine',
    'StationStateMachine',
    'StateTransition',
    
    # 时间处理
    'Timestamp',
    'get_current_timestamp',
    'format_timestamp',
    'parse_datetime_to_timestamp',
    'TimeRange'
]