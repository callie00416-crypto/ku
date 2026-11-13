"""
工业自动化测试平台 - 运行时事件定义
定义系统运行时产生的各类事件
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


@dataclass
class RuntimeEvent(ABC):
    """运行时事件基类"""
    event_id: str
    timestamp: datetime
    source: str
    payload: Dict[str, Any]
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())


# 设备相关事件
@dataclass
class DeviceConnected(RuntimeEvent):
    """设备连接事件"""
    device_id: str
    connection_info: Dict[str, Any]


@dataclass
class DeviceDisconnected(RuntimeEvent):
    """设备断开连接事件"""
    device_id: str
    reason: str


@dataclass
class HeartbeatLost(RuntimeEvent):
    """心跳丢失事件"""
    device_id: str
    last_heartbeat: datetime


@dataclass
class DeviceError(RuntimeEvent):
    """设备错误事件"""
    device_id: str
    error_code: str
    error_message: str


@dataclass
class DeviceStatusChanged(RuntimeEvent):
    """设备状态改变事件"""
    device_id: str
    old_status: str
    new_status: str


# 任务相关事件
@dataclass
class TaskCreated(RuntimeEvent):
    """任务创建事件"""
    task_id: str
    workorder_id: str
    task_type: str


@dataclass
class TaskStarted(RuntimeEvent):
    """任务开始事件"""
    task_id: str
    actor_id: str


@dataclass
class TaskCompleted(RuntimeEvent):
    """任务完成事件"""
    task_id: str
    result: str
    duration_ms: int


@dataclass
class TaskFailed(RuntimeEvent):
    """任务失败事件"""
    task_id: str
    error_code: str
    error_message: str


@dataclass
class TaskPaused(RuntimeEvent):
    """任务暂停事件"""
    task_id: str
    reason: str


@dataclass
class TaskResumed(RuntimeEvent):
    """任务恢复事件"""
    task_id: str


# 工单相关事件
@dataclass
class WorkOrderCreated(RuntimeEvent):
    """工单创建事件"""
    workorder_id: str
    product_model: str


@dataclass
class WorkOrderStarted(RuntimeEvent):
    """工单开始事件"""
    workorder_id: str


@dataclass
class WorkOrderCompleted(RuntimeEvent):
    """工单完成事件"""
    workorder_id: str
    completed_quantity: int
    ng_quantity: int


@dataclass
class WorkOrderCancelled(RuntimeEvent):
    """工单取消事件"""
    workorder_id: str
    reason: str


# 告警相关事件
@dataclass
class AlarmTriggered(RuntimeEvent):
    """告警触发事件"""
    alarm_id: str
    alarm_code: str
    alarm_level: str
    message: str


@dataclass
class AlarmAcknowledged(RuntimeEvent):
    """告警确认事件"""
    alarm_id: str
    acknowledged_by: str


@dataclass
class AlarmResolved(RuntimeEvent):
    """告警解决事件"""
    alarm_id: str
    resolved_by: str


@dataclass
class AlarmClosed(RuntimeEvent):
    """告警关闭事件"""
    alarm_id: str


# 系统相关事件
@dataclass
class SystemStarted(RuntimeEvent):
    """系统启动事件"""
    startup_info: Dict[str, Any]


@dataclass
class SystemShutdown(RuntimeEvent):
    """系统关闭事件"""
    shutdown_reason: str


@dataclass
class QueueOverflow(RuntimeEvent):
    """队列溢出事件"""
    queue_name: str
    current_size: int
    max_size: int


@dataclass
class TcpTimeout(RuntimeEvent):
    """TCP超时事件"""
    remote_address: str
    timeout_duration: int


@dataclass
class DatabaseConnectionIssue(RuntimeEvent):
    """数据库连接问题事件"""
    connection_string: str
    error_message: str


@dataclass
class MemoryPressure(RuntimeEvent):
    """内存压力事件"""
    current_usage_mb: int
    threshold_mb: int