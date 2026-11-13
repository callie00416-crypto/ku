"""
报告领域事件 - Report Domain Events

【职责】
- 定义报告领域事件
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


class ReportEventType(Enum):
    """报告事件类型"""
    REPORT_CREATED = "report.created"                 # 报告创建
    REPORT_GENERATED = "report.generated"             # 报告生成
    REPORT_ARCHIVED = "report.archived"               # 报告归档
    REPORT_ATTACHMENT_ADDED = "report.attachment_added"  # 报告附件添加
    REPORT_VALIDATED = "report.validated"             # 报告验证


@dataclass
class ReportEvent:
    """报告事件基类"""
    event_type: ReportEventType
    report_id: str
    timestamp: float
    data: Dict[str, Any]
    event_id: str = None
    correlation_id: str = None  # 关联ID，用于追踪整个事件链
    causation_id: str = None    # 因果ID，用于追踪事件源头
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = generate_id("RPT_EVT")
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class ReportCreatedEvent(ReportEvent):
    """报告创建事件"""
    
    def __init__(self, report_id: str, task_id: str, workorder_id: str, 
                 sn: str, metadata: Dict[str, Any] = None):
        data = {
            'task_id': task_id,
            'workorder_id': workorder_id,
            'sn': sn,
            'metadata': metadata or {},
            'created_at': time.time()
        }
        super().__init__(
            event_type=ReportEventType.REPORT_CREATED,
            report_id=report_id,
            timestamp=time.time(),
            data=data
        )


@dataclass
class ReportGeneratedEvent(ReportEvent):
    """报告生成事件"""
    
    def __init__(self, report_id: str, task_id: str, result: str, 
                 total_records: int, generated_at: float, 
                 metadata: Dict[str, Any] = None):
        data = {
            'task_id': task_id,
            'result': result,
            'total_records': total_records,
            'generated_at': generated_at,
            'metadata': metadata or {}
        }
        super().__init__(
            event_type=ReportEventType.REPORT_GENERATED,
            report_id=report_id,
            timestamp=generated_at,
            data=data
        )


@dataclass
class ReportArchivedEvent(ReportEvent):
    """报告归档事件"""
    
    def __init__(self, report_id: str, archived_at: float, 
                 retention_period: int = None, metadata: Dict[str, Any] = None):
        data = {
            'archived_at': archived_at,
            'retention_period': retention_period,
            'metadata': metadata or {}
        }
        super().__init__(
            event_type=ReportEventType.REPORT_ARCHIVED,
            report_id=report_id,
            timestamp=archived_at,
            data=data
        )


@dataclass
class ReportAttachmentAddedEvent(ReportEvent):
    """报告附件添加事件"""
    
    def __init__(self, report_id: str, attachment_id: str, attachment_type: str, 
                 size: int, description: str = None, timestamp: float = None, 
                 metadata: Dict[str, Any] = None):
        data = {
            'attachment_id': attachment_id,
            'type': attachment_type,
            'size': size,
            'description': description,
            'timestamp': timestamp or time.time(),
            'metadata': metadata or {}
        }
        super().__init__(
            event_type=ReportEventType.REPORT_ATTACHMENT_ADDED,
            report_id=report_id,
            timestamp=timestamp or time.time(),
            data=data
        )


@dataclass
class ReportValidatedEvent(ReportEvent):
    """报告验证事件"""
    
    def __init__(self, report_id: str, validator_id: str, is_valid: bool,
                 validation_errors: list = None, validated_at: float = None, 
                 metadata: Dict[str, Any] = None):
        data = {
            'validator_id': validator_id,
            'is_valid': is_valid,
            'validation_errors': validation_errors or [],
            'validated_at': validated_at or time.time(),
            'metadata': metadata or {}
        }
        super().__init__(
            event_type=ReportEventType.REPORT_VALIDATED,
            report_id=report_id,
            timestamp=validated_at or time.time(),
            data=data
        )