"""
工业自动化测试平台 - 读模型系统
Read Models for Industrial Query Optimization
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class TaskReadModel:
    """任务读模型 - 工业核心"""
    id: int
    task_id: str
    workorder_id: Optional[str]
    station_id: Optional[int]
    device_id: Optional[str]
    sn: Optional[str]  # 产品序列号
    task_type: Optional[str]
    priority: int
    status: str
    result: Optional[str]
    error_code: Optional[str]
    error_message: Optional[str]
    retry_count: int
    actor_id: Optional[str]  # 执行者ID
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]  # 任务执行时长(毫秒)
    metrics: Optional[Dict[str, Any]]  # 任务指标
    trace_id: Optional[str]  # 追踪ID
    correlation_id: Optional[str]  # 关联ID
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass
class ReportReadModel:
    """报告读模型 - 最关键工业追溯"""
    id: int
    report_id: str
    task_id: Optional[str]
    workorder_id: Optional[str]
    sn: Optional[str]  # 产品序列号
    station_id: Optional[int]
    device_id: Optional[str]
    result: Optional[str]
    detail: Optional[Dict[str, Any]]  # 详细测试结果
    report_snapshot: Optional[Dict[str, Any]]  # 报告快照（5年追溯用）
    attachments: Optional[List[Dict[str, Any]]]  # 附件系统
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass
class AlarmReadModel:
    """告警读模型"""
    id: int
    alarm_id: str
    station_id: Optional[int]
    device_id: Optional[str]
    alarm_type: Optional[str]
    severity: str  # INFO, WARNING, ERROR, CRITICAL
    title: Optional[str]
    description: Optional[str]
    status: str  # ACTIVE, RESOLVED, ACKNOWLEDGED
    dedup_key: Optional[str]  # 告警去重Key
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass
class StationReadModel:
    """工位读模型"""
    id: int
    station_id: str
    name: str
    location: Optional[str]
    status: str
    config: Optional[Dict[str, Any]]  # 工位配置
    last_heartbeat: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass
class DeviceReadModel:
    """设备读模型"""
    id: int
    device_id: str
    name: str
    device_type: Optional[str]
    station_id: Optional[int]
    ip_address: Optional[str]
    port: Optional[int]
    status: str
    connection_info: Optional[Dict[str, Any]]  # 连接信息
    config: Optional[Dict[str, Any]]  # 设备配置
    health_status: Optional[Dict[str, Any]]  # 健康状态
    last_heartbeat: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass
class WorkOrderReadModel:
    """工单读模型"""
    id: int
    workorder_id: str
    product_model: str
    batch_number: Optional[str]
    planned_quantity: int
    completed_quantity: int
    ng_quantity: int
    route_config: Optional[Dict[str, Any]]  # 工艺路线配置
    priority: int
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass
class TestRecordReadModel:
    """测试记录读模型"""
    id: int
    record_id: str
    task_id: Optional[str]
    report_id: Optional[str]
    test_item: str  # 测试项
    expected_value: Optional[str]
    actual_value: Optional[str]
    tolerance: Optional[str]  # 公差
    result: Optional[str]  # PASS/FAIL
    unit: Optional[str]  # 单位
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass
class YieldRateData:
    """良率数据"""
    workorder_id: str
    total_count: int
    pass_count: int
    fail_count: int
    yield_rate: float
    calculated_at: datetime


@dataclass
class FailDistributionData:
    """故障分布数据"""
    error_code: str
    error_message: str
    count: int
    percentage: float


@dataclass
class StationPerformanceData:
    """工位性能数据"""
    station_id: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    avg_duration_ms: float
    uptime_hours: float
    downtime_hours: float
    calculated_at: datetime


@dataclass
class TaskTimelineData:
    """任务时间线数据"""
    task_id: str
    sn: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    station_id: Optional[int]


@dataclass
class StationHistoryData:
    """工位历史数据"""
    station_id: str
    task_id: str
    sn: str
    result: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    created_at: datetime