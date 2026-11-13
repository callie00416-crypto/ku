"""
报告领域 - Report Domain

【导出内容】
- Report: 报告聚合根
- 各种快照和记录值对象
- Report相关枚举
- Report相关异常
- Report相关事件
"""
from .report import (
    Report, ReportMetrics,
    DeviceSnapshot, TaskSnapshot, StationSnapshot,
    TestRecord, AlarmSnapshot, SoftwareVersion, OperatorInfo
)
from .enums import ReportType, ReportFormat, ReportStatus, RecordValueType
from .exceptions import (
    ReportException, ReportNotFoundException, ReportGenerationException,
    ReportArchiveException, ReportImmutableException, ReportValidationException
)
from .events import (
    ReportEventType, ReportEvent, ReportCreatedEvent, ReportGeneratedEvent,
    ReportArchivedEvent, ReportAttachmentAddedEvent, ReportValidatedEvent
)

__all__ = [
    # 主要聚合根
    'Report',
    'ReportMetrics',
    
    # 快照和记录值对象
    'DeviceSnapshot',
    'TaskSnapshot',
    'StationSnapshot',
    'TestRecord',
    'AlarmSnapshot',
    'SoftwareVersion',
    'OperatorInfo',
    
    # 枚举
    'ReportType',
    'ReportFormat',
    'ReportStatus',
    'RecordValueType',
    
    # 异常
    'ReportException',
    'ReportNotFoundException',
    'ReportGenerationException',
    'ReportArchiveException',
    'ReportImmutableException',
    'ReportValidationException',
    
    # 事件
    'ReportEventType',
    'ReportEvent',
    'ReportCreatedEvent',
    'ReportGeneratedEvent',
    'ReportArchivedEvent',
    'ReportAttachmentAddedEvent',
    'ReportValidatedEvent'
]