"""
Actor消息定义
"""
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, Dict
from datetime import datetime


class MessageType(Enum):
    """消息类型枚举"""
    # 控制类消息
    EMERGENCY_STOP = "EMERGENCY_STOP"      # 急停
    START_TASK = "START_TASK"              # 开始任务
    STOP_TASK = "STOP_TASK"                # 停止任务
    RESET_DEVICE = "RESET_DEVICE"          # 重置设备
    
    # 状态类消息
    DEVICE_STATUS_UPDATE = "DEVICE_STATUS_UPDATE"  # 设备状态更新
    TASK_STATUS_UPDATE = "TASK_STATUS_UPDATE"      # 任务状态更新
    HEARTBEAT = "HEARTBEAT"                        # 心跳
    
    # 数据类消息
    MEASUREMENT_DATA = "MEASUREMENT_DATA"          # 测量数据
    ALARM_TRIGGERED = "ALARM_TRIGGERED"            # 报警触发
    WORKORDER_UPDATE = "WORKORDER_UPDATE"          # 工单更新
    
    # 系统类消息
    SYSTEM_COMMAND = "SYSTEM_COMMAND"              # 系统命令
    HEALTH_CHECK = "HEALTH_CHECK"                  # 健康检查


@dataclass
class ActorMessage:
    """Actor消息基类"""
    message_id: str
    message_type: MessageType
    content: Any
    timestamp: datetime
    source: str
    destination: str
    priority: int = 1  # 数值越小优先级越高
    correlation_id: Optional[str] = None  # 关联ID，用于追踪消息链
    timeout: Optional[float] = None      # 超时时间（秒）
    

@dataclass
class ControlMessage(ActorMessage):
    """控制类消息"""
    command: str
    params: Dict[str, Any] = None
    

@dataclass
class StatusMessage(ActorMessage):
    """状态类消息"""
    status: str
    details: Dict[str, Any] = None
    

@dataclass
class DataMessage(ActorMessage):
    """数据类消息"""
    data_type: str
    value: Any
    unit: Optional[str] = None
    

@dataclass
class SystemMessage(ActorMessage):
    """系统类消息"""
    level: str  # INFO, WARNING, ERROR, CRITICAL
    component: str