"""
报告领域 - Report Domain（工业追溯真相）

【职责】
- 工业测试报告归档
- 测试结果快照保存
- 不可变历史记录
- 工业追溯证据链

【核心能力】
- 测试记录归档
- 快照数据固化
- 结果不可变
- 关联追溯链

【设计原则】
- Report 是归档真相，不是动态引用
- Report 生成后不可修改
- 支持追加模式
- 快照固化当时环境
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import time

from ..common.aggregate_root import AggregateRoot, ValueObject, Entity, generate_id
from ..common.enums import EventType, TaskResult
from .enums import ReportStatus
from ..common.exceptions import DomainException
from .exceptions import ReportArchiveException, ReportException
from ..common.temporal import Timestamp
from ..task.task import TaskMetrics, RuntimeSession, TaskFlow
from ..station.station import ResourceState, AlarmState, DeviceMount
from ..device.device import DeviceMetrics


@dataclass
class DeviceSnapshot(ValueObject):
    """设备快照（值对象）
    
    【职责】
    - 固化测试时设备状态
    - 记录设备配置
    - 存档设备能力
    """
    device_id: str
    station_id: str
    code: str
    name: str
    device_type: str
    protocol: str
    connect_status: str
    status: str
    is_connected: bool
    is_busy: bool
    is_heartbeat_alive: bool
    config: Dict[str, Any]
    metrics: Dict[str, Any]
    calibration_info: Dict[str, Any]
    last_heartbeat: Optional[float]
    created_at: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskSnapshot(ValueObject):
    """任务快照（值对象）
    
    【职责】
    - 固化测试时任务状态
    - 记录任务配置
    - 存档任务参数
    """
    task_id: str
    workorder_id: str
    station_id: int
    device_id: Optional[str]
    sn: str
    task_type: str
    priority: str
    status: str
    result: Optional[str]
    error_code: Optional[str]
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    actor_id: Optional[str]
    start_time: Optional[float]
    end_time: Optional[float]
    duration_ms: Optional[int]
    metrics: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StationSnapshot(ValueObject):
    """工位快照（值对象）
    
    【职责】
    - 固化测试时工位状态
    - 记录工位配置
    - 存档工位能力
    """
    station_id: str
    code: str
    name: str
    line_code: str
    area_code: str
    status: str
    mode: str
    current_task_id: Optional[str]
    is_enabled: bool
    resource_state: Dict[str, Any]
    alarm_state: Dict[str, Any]
    mounted_devices: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestRecord(ValueObject):
    """测试记录（值对象）
    
    【职责】
    - 记录单个测试项结果
    - 支持多种数据类型
    - 存档原始数据
    """
    record_id: str
    step: int
    name: str
    value_type: str  # 'float', 'bool', 'string', 'json', 'waveform', 'binary'
    value_raw: str   # 原始值，根据value_type解析
    expected: Optional[str] = None
    tolerance: Optional[str] = None
    is_pass: bool = False
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_parsed_value(self):
        """获取解析后的值"""
        if self.value_type == 'float':
            return float(self.value_raw) if self.value_raw else None
        elif self.value_type == 'bool':
            return self.value_raw.lower() == 'true' if self.value_raw else False
        elif self.value_type == 'json':
            import json
            return json.loads(self.value_raw) if self.value_raw else {}
        elif self.value_type == 'int':
            return int(self.value_raw) if self.value_raw else None
        elif self.value_type == 'timestamp':
            return float(self.value_raw) if self.value_raw else None
        else:
            return self.value_raw


@dataclass
class ReportMetrics(ValueObject):
    """报告指标（值对象）
    
    【职责】
    - 记录报告相关指标
    - 不可变
    """
    total_records: int = 0
    pass_records: int = 0
    fail_records: int = 0
    duration_ms: int = 0


@dataclass
class AlarmSnapshot(ValueObject):
    """告警快照（值对象）
    
    【职责】
    - 固化测试时的告警状态
    - 记录相关告警信息
    - 存档异常上下文
    """
    alarm_id: str
    alarm_code: str
    alarm_level: str
    message: str
    status: str
    occurred_at: float
    acknowledged_at: Optional[float]
    resolved_at: Optional[float]
    closed_at: Optional[float]
    task_id: Optional[str]
    station_id: Optional[str]
    device_id: Optional[str]
    workorder_id: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class SoftwareVersion(ValueObject):
    """软件版本（值对象）
    
    【职责】
    - 记录测试时软件版本
    - 固化运行环境
    - 支持版本追溯
    """
    encoder_test_version: str
    driver_version: str
    firmware_version: str
    os_version: str
    python_version: str
    created_at: float = field(default_factory=time.time)


@dataclass
class OperatorInfo(ValueObject):
    """操作员信息（值对象）
    
    【职责】
    - 记录操作员信息
    - 固化责任人
    - 支持责任追溯
    """
    operator_id: str
    operator_name: str
    role: str
    department: str
    timestamp: float = field(default_factory=time.time)


class Report(AggregateRoot):
    """报告聚合根（工业追溯核心）
    
    【职责】
    - 管理测试报告完整生命周期
    - 保证报告不可变性
    - 固化测试时快照数据
    - 支持追加模式
    
    【核心方法】
    - generate(): 生成报告
    - archive(): 归档报告
    - add_attachment(): 添加附件
    
    【工业原则】
    - Report是归档真相，不是动态引用
    - 生成后禁止修改
    - 支持追加，不支持更新
    
    【使用示例】
    >>> report = Report.create(
    ...     task_id="TASK-001",
    ...     workorder_id="WO-001",
    ...     sn="SN123456"
    ... )
    >>> report.generate(
    ...     task_snapshot=task_snapshot,
    ...     station_snapshot=station_snapshot,
    ...     device_snapshots=[device_snapshot],
    ...     test_records=[test_record],
    ...     alarm_snapshots=[alarm_snapshot]
    ... )
    >>> report.archive()
    """
    
    def __init__(self, report_id: str):
        """
        Args:
            report_id: 报告ID
        """
        super().__init__(report_id)
        
        self._task_id: Optional[str] = None
        self._workorder_id: Optional[str] = None
        self._sn: Optional[str] = None
        
        self._status = ReportStatus.DRAFT
        self._result: Optional[TaskResult] = None
        
        self._task_snapshot: Optional[TaskSnapshot] = None
        self._station_snapshot: Optional[StationSnapshot] = None
        self._device_snapshots: List[DeviceSnapshot] = []
        self._test_records: List[TestRecord] = []
        self._alarm_snapshots: List[AlarmSnapshot] = []
        
        self._software_version: Optional[SoftwareVersion] = None
        self._operator_info: Optional[OperatorInfo] = None
        self._metadata: Dict[str, Any] = {}
        
        self._generated_at: Optional[float] = None
        self._archived_at: Optional[float] = None
        
        self._metrics = ReportMetrics()
    
    @property
    def task_id(self) -> Optional[str]:
        return self._task_id
    
    @property
    def workorder_id(self) -> Optional[str]:
        return self._workorder_id
    
    @property
    def sn(self) -> Optional[str]:
        return self._sn
    
    @property
    def status(self) -> ReportStatus:
        return self._status
    
    @property
    def result(self) -> Optional[TaskResult]:
        return self._result
    
    @property
    def task_snapshot(self) -> Optional[TaskSnapshot]:
        return self._task_snapshot
    
    @property
    def station_snapshot(self) -> Optional[StationSnapshot]:
        return self._station_snapshot
    
    @property
    def device_snapshots(self) -> List[DeviceSnapshot]:
        return self._device_snapshots
    
    @property
    def test_records(self) -> List[TestRecord]:
        return self._test_records
    
    @property
    def alarm_snapshots(self) -> List[AlarmSnapshot]:
        return self._alarm_snapshots
    
    @property
    def software_version(self) -> Optional[SoftwareVersion]:
        return self._software_version
    
    @property
    def operator_info(self) -> Optional[OperatorInfo]:
        return self._operator_info
    
    @property
    def generated_at(self) -> Optional[float]:
        return self._generated_at
    
    @property
    def archived_at(self) -> Optional[float]:
        return self._archived_at
    
    @property
    def metrics(self) -> ReportMetrics:
        return self._metrics
    
    @classmethod
    def create(cls, task_id: str, workorder_id: str, sn: str,
               metadata: Dict[str, Any] = None) -> 'Report':
        """创建报告（工厂方法）
        
        Args:
            task_id: 关联任务ID
            workorder_id: 关联工单ID
            sn: 产品序列号
            metadata: 元数据
            
        Returns:
            Report实例
        """
        report_id = generate_id("REPORT")
        report = cls(report_id)
        
        report._task_id = task_id
        report._workorder_id = workorder_id
        report._sn = sn
        report._metadata = metadata or {}
        
        return report
    
    def generate(self, task_snapshot: TaskSnapshot, station_snapshot: StationSnapshot,
                 device_snapshots: List[DeviceSnapshot], test_records: List[TestRecord],
                 alarm_snapshots: List[AlarmSnapshot] = None,
                 software_version: SoftwareVersion = None, 
                 operator_info: OperatorInfo = None) -> None:
        """生成报告
        
        Args:
            task_snapshot: 任务快照
            station_snapshot: 工位快照
            device_snapshots: 设备快照列表
            test_records: 测试记录列表
            alarm_snapshots: 告警快照列表
            software_version: 软件版本信息
            operator_info: 操作员信息
        """
        if self._status != ReportStatus.DRAFT:
            raise DomainException(f"报告状态错误: {self._status.value}, 只能在DRAFT状态下生成")
        
        # 固化快照数据
        self._task_snapshot = task_snapshot
        self._station_snapshot = station_snapshot
        self._device_snapshots = device_snapshots
        self._test_records = test_records
        self._alarm_snapshots = alarm_snapshots or []
        self._software_version = software_version
        self._operator_info = operator_info
        
        # 计算结果
        self._result = self._calculate_result(test_records)
        
        # 更新指标
        self._update_metrics()
        
        # 设置生成时间
        self._generated_at = time.time()
        self._status = ReportStatus.GENERATED
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.REPORT_GENERATED,
            'aggregate_id': self._id,
            'aggregate_type': 'Report',
            'data': {
                'task_id': self._task_id,
                'result': self._result.value if self._result else None,
                'generated_at': self._generated_at
            }
        })
    
    def archive(self) -> None:
        """归档报告"""
        if self._status != ReportStatus.GENERATED:
            raise ReportArchiveException(self._id, f"报告状态错误: {self._status.value}, 只能在GENERATED状态下归档")
        
        self._status = ReportStatus.ARCHIVED
        self._archived_at = time.time()
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.REPORT_ARCHIVED,
            'aggregate_id': self._id,
            'aggregate_type': 'Report',
            'data': {
                'archived_at': self._archived_at
            }
        })
    
    def add_attachment(self, attachment_type: str, content: bytes, 
                      description: str = None) -> None:
        """添加附件（追加模式，不修改报告主体）"""
        if self._status == ReportStatus.DRAFT:
            raise ReportException(f"报告还在草稿状态，无法添加附件: {self._id}")
        
        attachment = {
            'attachment_id': generate_id("ATTACH"),
            'type': attachment_type,
            'size': len(content),
            'timestamp': time.time(),
            'description': description,
            'checksum': self._calculate_checksum(content)
        }
        
        # 将附件信息添加到元数据中，不改变报告主体
        attachments = self._metadata.get('attachments', [])
        attachments.append(attachment)
        self._metadata['attachments'] = attachments
        
        self._increment_version()
        
        # 发布领域事件
        self._add_domain_event({
            'event_type': EventType.REPORT_ATTACHMENT_ADDED,
            'aggregate_id': self._id,
            'aggregate_type': 'Report',
            'data': {
                'attachment_id': attachment['attachment_id'],
                'type': attachment_type
            }
        })
    
    def _calculate_result(self, test_records: List[TestRecord]) -> TaskResult:
        """计算报告结果"""
        if not test_records:
            return TaskResult.SKIP
        
        total_records = len(test_records)
        pass_records = sum(1 for record in test_records if record.is_pass)
        
        # 如果所有记录都通过，则PASS
        if pass_records == total_records:
            return TaskResult.PASS
        
        # 如果有任何记录失败，则FAIL
        return TaskResult.FAIL
    
    def _update_metrics(self):
        """更新指标"""
        total_records = len(self._test_records)
        pass_records = sum(1 for record in self._test_records if record.is_pass)
        fail_records = total_records - pass_records
        
        # 计算总耗时
        duration_ms = 0
        if self._task_snapshot and self._task_snapshot.start_time and self._task_snapshot.end_time:
            duration_ms = int((self._task_snapshot.end_time - self._task_snapshot.start_time) * 1000)
        
        self._metrics = ReportMetrics(
            total_records=total_records,
            pass_records=pass_records,
            fail_records=fail_records,
            duration_ms=duration_ms
        )
    
    def _calculate_checksum(self, content: bytes) -> str:
        """计算内容校验和"""
        import hashlib
        return hashlib.md5(content).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            报告信息字典
        """
        return {
            'id': self._id,
            'task_id': self._task_id,
            'workorder_id': self._workorder_id,
            'sn': self._sn,
            'status': self._status.value,
            'result': self._result.value if self._result else None,
            'task_snapshot': self._task_snapshot.__dict__ if self._task_snapshot else None,
            'station_snapshot': self._station_snapshot.__dict__ if self._station_snapshot else None,
            'device_snapshots': [ds.__dict__ for ds in self._device_snapshots],
            'test_records': [
                {
                    'record_id': tr.record_id,
                    'step': tr.step,
                    'name': tr.name,
                    'value_type': tr.value_type,
                    'value_raw': tr.value_raw,
                    'expected': tr.expected,
                    'tolerance': tr.tolerance,
                    'is_pass': tr.is_pass,
                    'timestamp': tr.timestamp,
                    'metadata': tr.metadata
                } 
                for tr in self._test_records
            ],
            'alarm_snapshots': [asnap.__dict__ for asnap in self._alarm_snapshots],
            'software_version': self._software_version.__dict__ if self._software_version else None,
            'operator_info': self._operator_info.__dict__ if self._operator_info else None,
            'generated_at': self._generated_at,
            'archived_at': self._archived_at,
            'metrics': {
                'total_records': self._metrics.total_records,
                'pass_records': self._metrics.pass_records,
                'fail_records': self._metrics.fail_records,
                'duration_ms': self._metrics.duration_ms
            },
            'metadata': self._metadata,
            'version': self.version,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self) -> str:
        return f"<Report id={self._id} sn={self._sn} result={self._result.value if self._result else None} status={self._status.value}>"